import pymysql

class   Mysql():
    def __init__(self, address, db, name, password):
        self.ok = True
        try:
            self.con = pymysql.connect(host=address, user=name, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
            with self.con.cursor() as cur:
                cur.execute("select version()")
                ver = cur.fetchone()
        except pymysql.Error:
            self.ok = False

    def getEntry(self, command):
        if not self.ok:
            yield None
        with self.con.cursor() as cur:
            cur.execute(command)
            for i in range(cur.rowcount):
                yield cur.fetchone()

    def writeEntry(self, command):
        if not self.ok:
            return
        try:
            with self.con.cursor() as cur:
                cur.execute(command)
                self.con.commit()
        except:
            self.con.rollback()
