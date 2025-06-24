import sys
import sqlite3
import threading
import json
from tkinter import *
from tkinter import messagebox


settingsDatabasePath = '../database/data/settingsdb.sqlite'

defaultDatabaseConfigPath = './slam-remote-interface/database/models/defaultDatabaseSettings.json'

# Parse the default configurations for diffrent tables out of the json file
def parseDefaultTableConfigs():
    defaultParsedTableConfigs: dict = {}

    f = None

    try:
        with open('test.sqlite') as f:
            defaultParsedTableConfigs = json.load(f)

    except Exception as e:
        print(e)

    finally:
        f.close()
        return defaultParsedTableConfigs


class DatabaseHandler(threading.Thread):
    def __init__(self) -> None:
        pass

    def run(self):
        pass

class DatabaseConnector:
    def __init__(self) -> None:
        self.dbConnection = sqlite3.connect('test.sqlite')
        self.dbCursor = self.dbConnection.cursor()
        self.initiateDB()
        self.initiateNetworkTable()
    
    def initiateDB(self) -> None:
        self.dbCursor.execute('''
            CREATE TABLE IF NOT EXISTS networkTable (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT DEFAULT 'none',
                createdatetime  TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S:%s', 'now', 'localtime') ),
                updatedatetime  TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S:%s', 'now', 'localtime') )
            );
        ''')
        self.dbCursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_networkTable_updatetime
                BEFORE UPDATE
                    ON networkTable
            BEGIN
                UPDATE networkTable
                    SET updatedatetime = strftime('%Y-%m-%d %H:%M:%S:%s', 'now', 'localtime') 
                WHERE id = old.id;
            END;
        ''')

        self.dbConnection.commit()
        # self.dbCursor.close()
    
    def getSqliteVersion(self) -> str:
        try:
            sqlite_select_Query = "SELECT sqlite_version()"
            self.dbCursor.execute(sqlite_select_Query)
            record = self.dbCursor.fetchall()
            return str(record[0][0])

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            pass
            # if self.dbConnection:
            #     self.dbConnection.close()


    # Initiate table records

    def initiateNetworkTable(self) -> None:
        sqlInsertList: list = [
            {'key': 'defaultUrlProtocol', 'value': 'http',},
            {'key': 'defaultUrlDomain', 'value': 'slam-car.local',},
            {'key': 'defaultUrlPort', 'value': 'slam-car.local',},
            {'key': 'defaultBaseControlUrl', 'value': '/controll',},
            {'key': 'defaultBaseTelemetryUrl', 'value': '/telemetry',}
        ]
        # sqlInsertList: list = parseDefaultTableConfigs().get('networkTable')

        sqlQuery = '''
            INSERT INTO networkTable (key, value)
            SELECT '{key}', '{value}'
            WHERE NOT EXISTS (SELECT * FROM networkTable WHERE key = '{key}');
        '''
        
        for i in sqlInsertList:
            self.dbCursor.execute(sqlQuery.format(**i))
        self.dbConnection.commit()


    # Get table Records

    def getNetworkTableRecords(self) -> list:
        sqlQuery = '''
            SELECT * FROM networkTable;
        '''
        self.dbCursor.execute(sqlQuery)
        
        return self.dbCursor.fetchall()


    # Update table records
    def updateNetworkTableRecords(self, newRecordsList) -> bool:
        sqlQuery = '''UPDATE networkTable SET value = '{value}' WHERE key = '{key}';'''

        for i in newRecordsList:
            self.dbCursor.execute(sqlQuery.format(**i))
            self.dbConnection.commit()
            print(self.dbCursor.fetchall)

        return True

    # Close connection to database
    def closeSqliteDatabase(self):
        self.dbCursor.close()
        self.dbConnection.close()


testDBObj = DatabaseConnector()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        testDBObj.closeSqliteDatabase()
        sys.exit()

def fetchData():
    for i in testDBObj.getNetworkTableRecords():
        print(i)
        if i[1] == 'defaultUrlDomain':
            entryFieldDomain.config(text='')
            labelFieldDomain.config(text=i[2])
        if i[1] == 'defaultUrlPort':
            entryFieldPort.config(text='')
            labelFieldPort.config(text=i[2])
    
    updateOverviewTableList()

def updateDomainData():
    print("Running ...")
    testDBObj.updateNetworkTableRecords([{'key': 'defaultUrlDomain', 'value': entryFieldDomain.get()}])
    fetchData()

def updatePortData():
    print("Running ...")
    testDBObj.updateNetworkTableRecords([{'key': 'defaultUrlPort', 'value': entryFieldPort.get()}])
    fetchData()

overviewTableList: list[Label] = []

def prossesNetTable(obj):
    return {obj[1], obj[2]}

def updateOverviewTableList():
    for i in overviewTableList:
        i.destroy()
    overviewTableList.clear()

    overviewTableList.append(Label(root, text="Network Table:"))

    for i in testDBObj.getNetworkTableRecords():
        overviewTableList.append(Label(root, text="{0}: {1}".format(i[1], i[2])))
    
    for j in overviewTableList:
        j.pack()


if __name__=='__main__':
    print("The current Sqlite Version is: {0}".format(testDBObj.getSqliteVersion()))
    root = Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    entryFieldDomain = Entry(root)
    entryFieldPort = Entry(root)

    labelFieldDomain = Label(root)
    labelFieldPort = Label(root)

    submitButtonDomain = Button(root, text="Update Domain", command=updateDomainData)
    submitButtonPort = Button(root, text="Update Port", command=updatePortData)

    submitButtonUpdate = Button(root, text="Update All", command=fetchData)
    
    entryFieldDomain.pack()
    labelFieldDomain.pack()
    submitButtonDomain.pack()
    
    entryFieldPort.pack()
    labelFieldPort.pack()
    submitButtonPort.pack()

    submitButtonUpdate.pack()

    fetchData()

    root.mainloop()