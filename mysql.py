import MySQLdb as mdb

class   Mysql():
    def __init__(self, address, db, name, password):
        self.ok = True
        try:
            self.con = mdb.connect(address, name, password, db)
            cur = self.con.cursor()
            cur.execute("select version()")
            ver = cur.fetchone()
        except mdb.Error:
            self.ok = False

    def getEntry(self, command):
        if not self.ok:
            yield None
        cur = self.con.cursor(mdb.cursors.DictCursor)
        cur.execute(command)
        for i in range(cur.rowcount):
            yield cur.fetchone()

    def writeEntry(self, command):
        if not self.ok:
            return
        cur = self.con.cursor()
        try:
            cur.execute(command)
            self.con.commit()
        except:
            self.con.rollback()
