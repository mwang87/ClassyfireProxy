# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
#from flask_cache import Cache

from app import app
from classyfire_tasks import get_entity, classify_full_structure, record_failure
from classyfire_tasks import populate_batch_task

from werkzeug.utils import secure_filename
import os
import glob
import json
import requests
import random
import shutil
import urllib
import urllib.parse
from time import sleep
import redis
from models import ClassyFireEntity
#redis_client = redis.Redis(host='classyfire-redis', port=6379, db=0)


@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/entities/<entity_name>', methods=['GET'])
def entities(entity_name):
    block = False

    #if "block" in request.values:
    #    block = True

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

    # Checking if we have inchi or smiles in the url, so we can ship it over to their server to classify
    if "smiles" in request.values:
        smiles = request.values.get("smiles")
        #classyfire_info =  classify_full_structure.delay(smiles, inchi_key)
    elif "inchi" in request.values:
        conversion_url = "https://gnps-structure.ucsd.edu/smiles?inchi={}".format(urllib.parse.quote(request.values.get("inchi")))
        r = requests.get(conversion_url)
        smiles = r.text
        #classyfire_info =  classify_full_structure.delay(smiles, inchi_key)

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
