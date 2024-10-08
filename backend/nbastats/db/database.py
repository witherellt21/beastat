import os
import sys
import time

from peewee import InterfaceError, OperationalError, PostgresqlDatabase

from .settings import DB_URL

# print("SYSTEM  ", os.system("pg_isready -U nbastats -d nbastats"))
print(f"Connecting to database at {DB_URL}")

# while True:
# try:
DB = PostgresqlDatabase(DB_URL)
DB.connect()
# break
# except:
#     print("not connected")
#     time.sleep(2)
# except InterfaceError as e:
#     DB = None
#     print(e)
# except OperationalError as oe:
#     DB = None
#     print(oe)
print("CONNECTED")
