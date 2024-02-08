from peewee import MySQLDatabase

DB = MySQLDatabase(
    'nbastats',
    user='root',
    password='T@yl0r31lax',
    host='localhost',
    port=3306
)

DB.connect()