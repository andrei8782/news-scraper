from google.cloud.sql.connector import connector
import sqlalchemy
import pg8000
import csv
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="credentials.json"

class DatabaseController:
    def __init__(self) -> None:
        self.pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
        self.insert_sql = f"INSERT INTO scraped_articles values ({0}, {1}, {2}, {3}, {4}, {5}, {6}) ON CONFLICT DO NOTHING;"
    
    def append_to_db(self, csv_path):
        with open(csv_path, 'r') as f:
            csv_data = csv.DictReader(f)
            for row in csv_data:
                with pool.connect() as conn:
                    insert = self.insert_sql.format(row[])
                    conn.execute(insert)
    
    def getconn(self) -> pg8000.Connection:
        conn: pg8000.Connection = connector.connect(
            "eastern-clock-341917:us-central1:pulanewsdata",
            "pg8000",
            user="editor",
            password="editor1",
            db="newsdata"
        )
        return conn