import sqlite3
import datetime

def safeguard(conn):
    def decorator(meth):
        def wrapper(*args):
            try:
                result = meth(*args)
                return result
            except sqlite3.Error as error:
                print("Database Error")
                print(error)
        return wrapper
    return decorator

class SafeGuardAll(type):
    def __new__(metaclass, classname, superclass, attr):
        all_meths = [i for i in attr.keys() if not i.startswith("__") and not i == "conn"]
        for i in all_meths:
            attr[i] = safeguard(attr["conn"])(attr[i])
        return type.__new__(metaclass, classname, superclass, attr)

class App_database(metaclass = SafeGuardAll):
    conn = None
    def __init__(self):
        try:
            App_database.conn = sqlite3.connect("_tube_.db",check_same_thread = False)
            self.cursor = App_database.conn.cursor()
        except sqlite3.Error as e:
            if App_database.conn:
                print("Database Error")
                print(e)
                App_database.conn.close()

    def create_table(self):
            if App_database.conn:
                table_header = """CREATE TABLE IF NOT EXISTS Youtube(id integer PRIMARY KEY,
               name text NOT NULL, location text NOT NULL, time text NOT NULL );"""
                self.cursor.execute(table_header)

    def insert_row(self, element):
        if App_database.conn:
            time = datetime.datetime.now().strftime("%d-%m-%y")
            sql_header = "INSERT INTO Youtube(name, location, time) VALUES(?,?,?)"
            element.append(time)
            print(element[0], element[1], element[2], sep=" * ")
            self.cursor.execute(sql_header, element)
            App_database.conn.commit()
            return self.cursor.lastrowid

    def get(self):
        if App_database.conn:
            self.cursor.execute("SELECT * FROM Youtube")
            rows = self.cursor.fetchall()
            return rows

if __name__ == "__main__":
    app = App_database()
    #app.create_table()
    #app.insert_row(["bobo2", "c://smart"])
    print(app.get())