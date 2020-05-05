# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
#from flask_cache import Cache

from app import app
from classyfire_tasks import get_entity, web_query
from classyfire_tasks import populate_batch_task

from werkzeug.utils import secure_filename
import os
import glob
import json
import requests
import random
import shutil
import urllib
from time import sleep
import redis
from models import ClassyFireEntity
#redis_client = redis.Redis(host='classyfire-redis', port=6379, db=0)


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/entities/<input_type>', methods=['GET'])
def entities(input_type):
    #url encode the actual smiles/inchi/inhcikey
    entity_name = request.args.get('entity_name', '')   
    block = False

    if "block" in request.values:
        block = True
    
    #in the event we've been given an inchikey
    if input_type == "inchikey":
        inchi_key = entity_name.split(".")[0]
        return_format = entity_name.split(".")[1]

        #Reading from Database
        try:
            db_record = ClassyFireEntity.get(ClassyFireEntity.inchikey == entity_name)
            if db_record.status == "DONE":
                return db_record.responsetext
        except:
            print("entry in DB not found")
    
        #Querying Server
        result = get_entity.delay(inchi_key, return_format=return_format)

	#if the full strucutre is provided as an inchi/smiles
    if input_type == "fullstructure": 
        classyfire_info =  web_query(entity_name)
        if classyfire_info == "Classification failed":
            print("Classification failed", flush=True)
            abort(404)
        else: 
            #return classfication information
            return(classyfire_info)
    
    if block == False:
        abort(404)

    while(1):
        if result.ready():
            break
        sleep(0.1)
    result = result.get() 
    return result

@app.route('/keycount', methods=['GET'])
def keycount():
    return str(ClassyFireEntity.select().count())

@app.route('/keycounterror', methods=['GET'])
def keycounterror():
    return str(ClassyFireEntity.select().where(ClassyFireEntity.status == "ERROR").count())

### TODO: Fix
@app.route('/errorkeys.json', methods=['GET'])
def errorkeysjson():
    output_keys = []
    for entry in ClassyFireEntity.select().where(ClassyFireEntity.status == "ERROR"):
        output_keys.append(entry.inchikey.replace(".json", ""))

    return json.dumps(output_keys)

### TODO: Fix
@app.route('/errorkeys.txt', methods=['GET'])
def errorkeystxt():
    output_keys = []
    for entry in ClassyFireEntity.select().where(ClassyFireEntity.status == "ERROR"):
        output_keys.append(entry.inchikey.replace(".json", ""))

    return "\n".join(output_keys)


@app.route('/populatebatch', methods=['GET'])
def populatebatch():
    batch_id = request.values["id"]
    populate_batch_task.delay(batch_id)

    return "queued"
