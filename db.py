import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host, user, password, database):
        self.myDB = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
    def esegui_query(self, query):
        try:
            if self.myDB.is_connected():
                # print("Query:", query)
                cursor = self.myDB.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                # print("Risultato della query:", result)
                self.myDB.commit()
                return result
            else:
                print("Errore durante l'esecuzione della query")
                return None
        except Error as e:
            print("Errore: ", e)
            return None