# models.py
import datetime
from peewee import *
from app import db, retry_db

class ClassyFireEntity(Model):
    inchikey = TextField(unique=True, index=True)
    responsetext = TextField()
    status = TextField()

    class Meta:
        database = db

class FailCaseDB(Model):
    fullstructure = TextField(unique=True,index=True)
    status = TextField()
    
    class Meta:
        database = retry_db

#Creating the Tables
db.create_tables([ClassyFireEntity], safe=True)
retry_db.create_tables([FailCaseDB], safe=True)
