# models.py
import datetime
from peewee import *
from app import db

class ClassyFireEntity(Model):
    inchikey = TextField(unique=True, index=True)
    responsetext = TextField()
    status = TextField()

    class Meta:
        database = db

#Creating the Tables
db.create_tables([ClassyFireEntity], safe=True)