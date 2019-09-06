use futures::{Poll, SinkExt, Stream, StreamExt};
use std::{error::Error, io, net::SocketAddr, pin::Pin, task::Context};
use tokio::{
    self,
    codec::{Framed, LinesCodec, LinesCodecError},
    net::{TcpListener, TcpStream},
    sync::{mpsc, Lock},
};
use async_trait::async_trait;
#[macro_use]
extern crate simple_error;

type ClientTx = mpsc::UnboundedSender<ClientEvent>;
type ClientRx = mpsc::UnboundedReceiver<ClientEvent>;
type CoreTx = mpsc::UnboundedSender<Event>;
type CoreRx = mpsc::UnboundedReceiver<Event>;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "127.0.0.1:8080".parse::<SocketAddr>()?;
    let mut listener = TcpListener::bind(&addr).await?;

    let (tx, rx) = mpsc::unbounded_channel();

    let core = Core::new(rx);

    tokio::spawn(async move {
        if let Err(e) = process_core(core).await {
            println!("An error occured when processing core; error = {:?}", e);
        }
    });

    loop {
        let (stream, addr) = listener.accept().await?;

        let tx = tx.clone();

        tokio::spawn(async move {
            if let Err(e) = process_client(tx, stream, addr).await {
                println!("an error occured; error = {:?}", e);
            }
        });
    }
}

async fn process_core(mut core: Core) -> Result<(), Box<dyn Error>> {
    let mut room = Room::new("Test", "This is a test room");
    room.is_start = true;
    core.map.rooms.insert("Test".into(), room);

    while let Some(result) = core.next().await {
        match result {
            Event::NewClient(username, tx) => {
                let mut data = PlayerData::new(username.clone(), tx);
                if data.room.len() == 0 { // new player
                    data.send(ClientEvent::SendData("Welcome to MUD!".into())).await?;
                    data.room = core.map.get_first_room().unwrap();
                }
                let message = format!("{} appeared in {}", username, data.room);
                if core.clients.len() == 0 {
                    data.admin = true;
                }
                core.send_to_map(&data.room, ClientEvent::SendData(message)).await?;
                data.send(ClientEvent::SendData(core.map.get_room_by_name(&data.room).unwrap().look())).await?;
                let players = core.get_players_in_room(&data.room);
                if players.len() != 0 {
                    data.send(ClientEvent::SendData(format!("You see {} around", players.join(", ")))).await?;
                }
                data.send(ClientEvent::SendData(">".into())).await?;
                core.clients.insert(username, data);
            },
            Event::ClientSendsCommand(username, command) => {
                let client = core.clients.get(&username).cloned();
                if let Some(mut client) = client {
                    command.execute(&mut core, &mut client).await?;
                    client.send(ClientEvent::SendData(">".into())).await?;
                }
            },
            Event::ClientDisconnected(username) => {
                let client = core.clients.remove(&username);
                let message = format!("{} disconnected", username);
                println!("{}", message);
                if let Some(client) = client {
                    core.send_to_map(&client.room, ClientEvent::SendData(message)).await?;
                }
            }
        }
    }
    Ok(())
}

async fn get_username(lines: &mut Framed<TcpStream, LinesCodec>, addr: &SocketAddr) -> Result<String, Box<dyn Error>> {
    lines.send(String::from("Please enter your username:")).await?;
    while let Some(line) = lines.next().await {
        match line {
            Ok(line) => {
                if line.len() != 0 {
                    return Ok(line);
                }
            },
            _ => bail!(format!("failed to get username for {}", addr))
        };
        lines.send(String::from("Please enter your username:")).await?;
    }
    bail!(format!("connection closed for {}", addr));
}

async fn process_client(tx: CoreTx, stream: TcpStream, addr: SocketAddr) -> Result<(), Box<dyn Error>> {
    let mut lines = Framed::new(stream, LinesCodec::new());

    let username = get_username(&mut lines, &addr).await?;

    let mut client = Client::new(&username, tx, lines).await?;

    while let Some(result) = client.next().await {
        match result {
            Ok(ClientData::Data(data)) => {
                if data.len() == 0 {
                    continue;
                }
                if data.starts_with("exit") {
                    break;
                }
                if data.starts_with("/kick ") {
                    let params: Vec<&str> = data.split(" ").skip(1).take(2).collect();
                    if params.len() < 1 || params.len() > 2 {
                        client.lines.send(String::from("usage: /kick <user> [reason]")).await?;
                    } else {
                        let user = params[0];
                        let reason = if params.len() == 2 { params[1] } else { "" };
                        client.send_queue.send(Event::ClientSendsCommand(username.clone(),
                            Box::new(Kick::new(user.into(), reason.into())))).await?;
                    }
                } else {
                    client.send_queue.send(Event::ClientSendsCommand(username.clone(),
                        Box::new(SendMessage(data)))).await?;
                }
            },
            Ok(ClientData::ClientEvent(event)) => match event {
                ClientEvent::SendData(data) => client.lines.send(data).await?,
                ClientEvent::Disconnect => break,
            },
            Err(e) => {
                println!("an error occured while processing messages for {}; error = {:?}", username, e);
            }
        }
    }
    client.send_queue.send(Event::ClientDisconnected(username)).await?;
    Ok(())
}

#[derive(Clone)]
struct PlayerData {
    username: String,
    room: String,
    tx: ClientTx,
    admin: bool
}

impl PlayerData {
    fn new(username: String, tx: ClientTx) -> Self {
        Self {
            username,
            room: "".into(),
            tx,
            admin: false
        }
    }

    async fn send(self: &mut PlayerData, data: ClientEvent) -> Result<(), mpsc::error::UnboundedSendError> {
        self.tx.send(data).await
    }
}

struct Core {
    clients: std::collections::HashMap<String, PlayerData>,
    map: Map,
    read_queue: CoreRx,
}

impl Core {
    fn new(read_queue: CoreRx) -> Self {
        Self {
            clients: std::collections::HashMap::new(),
            map: Map::new(),
            read_queue
        }
    }

    fn get_players_in_room(self: &mut Core, room: &str) -> Vec<String> {
        self.clients.values().filter_map(|c| if c.room == room { Some(c.username.clone()) } else { None }).collect()
    }

    async fn send_to_map(self: &mut Core, room: &str, event: ClientEvent) -> Result<(), mpsc::error::UnboundedSendError> {
        for (_, client) in &mut self.clients {
            if client.room == room {
                client.send(event.clone()).await?;
            }
        }
        Ok(())
    }
}

impl Stream for Core {
    type Item = Event;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        self.read_queue.poll_next_unpin(cx)
    }
}

struct Client {
    lines: Framed<TcpStream, LinesCodec>,
    read_queue: ClientRx,
    send_queue: CoreTx,
}

impl Client {
    async fn new(username: &str, mut send_queue: CoreTx, lines: Framed<TcpStream, LinesCodec>) -> Result<Self, mpsc::error::UnboundedSendError> {
        let (tx, rx) = mpsc::unbounded_channel();

        send_queue.send(Event::NewClient(username.into(), tx)).await?;

        Ok(Client {
            lines,
            read_queue: rx,
            send_queue
        })
    }
}

enum ClientData {
    ClientEvent(ClientEvent),
    Data(String)
}

impl Stream for Client {
    type Item = Result<ClientData, LinesCodecError>;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if let Poll::Ready(Some(v)) = self.read_queue.poll_next_unpin(cx) {
            return Poll::Ready(Some(Ok(ClientData::ClientEvent(v))));
        }
        let result: Option<_> = futures::ready!(self.lines.poll_next_unpin(cx));

        Poll::Ready(match result {
            Some(Ok(message)) => Some(Ok(ClientData::Data(message))),
            Some(Err(e)) => Some(Err(e)),
            None => None
        })
    }
}

enum Event {
    NewClient(String, ClientTx),
    ClientSendsCommand(String, Box<dyn Command>),
    ClientDisconnected(String)
}

#[derive(Clone)]
enum ClientEvent {
    SendData(String),
    Disconnect
}

#[async_trait]
trait Command : Send {
    async fn execute(self: Box<Self>, core: &mut Core, client: &mut PlayerData) -> Result<(), Box<dyn Error>>;
}

struct SendMessage(String);

#[async_trait]
impl Command for SendMessage {
    async fn execute(self: Box<Self>, core: &mut Core, client: &mut PlayerData) -> Result<(), Box<dyn Error>> {
        for (_, client) in &mut core.clients {
            client.send(ClientEvent::SendData(format!("{}: {}", client.username, self.0))).await?;
        }
        Ok(())
    }
}

struct Kick {
    client: String,
    reason: String
}

impl Kick {
    fn new(client: String, reason: String) -> Self {
        Self {
            client, reason
        }
    }
}

#[async_trait]
impl Command for Kick {
    async fn execute(self: Box<Self>, core: &mut Core, client: &mut PlayerData) -> Result<(), Box<dyn Error>> {
        let cc = core.clients.get_mut(&self.client).cloned();
        if let Some(mut client) = cc {
            client.send(ClientEvent::SendData(format!("You have been kicked; reason: {}", self.reason))).await?;
            for (_, c) in &mut core.clients {
                c.send(ClientEvent::SendData(format!("{} kicked {}; reason: {}", client.username, self.client, self.reason))).await?;
            }
            client.send(ClientEvent::Disconnect).await?;
        } else {
            client.send(ClientEvent::SendData(format!("{} is not online", self.client))).await?;
        }
        Ok(())
    }
}

struct Room {
    is_start: bool,
    name: String,
    description: String,
    exits: std::collections::HashMap<String, String>
}

impl Room {
    fn new(name: &str, description: &str) -> Self {
        Self {
            is_start: false,
            name: name.into(),
            description: description.into(),
            exits: std::collections::HashMap::new()
        }
    }

    fn look(self: &Room) -> String {
        format!("{}:\n{}\n", self.name, self.description)
    }
}

struct Map {
    rooms: std::collections::HashMap<String, Room>
}

impl Map {
    fn new() -> Self {
        Self {
            rooms: std::collections::HashMap::new()
        }
    }

    fn get_room_by_name(self: &Map, name: &str) -> Option<&Room> {
        self.rooms.get(name)
    }

    fn get_first_room(self: &Map) -> Option<String> {
        for (_, room) in &self.rooms {
            if room.is_start {
                return Some(room.name.clone());
            }
        }
        None
    }
}
