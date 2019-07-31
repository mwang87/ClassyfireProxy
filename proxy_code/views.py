# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response
#from flask_cache import Cache

from app import app
from classyfire_tasks import get_entity

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

redis_client = redis.Redis(host='classyfire-redis', port=6379, db=0)

@app.route('/entities/<entity_name>', methods=['GET'])
def entities(entity_name):
    block = True

    if "nonblock" in request.values:
        block = False

    inchi_key = entity_name.split(".")[0]
    return_format = entity_name.split(".")[1]
    result = redis_client.get(entity_name)
    
    if result == None:
        result = get_entity.delay(inchi_key, return_format=return_format)

        if block == False:
            return "{}"

        while(1):
            if result.ready():
                break
            sleep(0.1)
        result = result.get()
    
    return result

@app.route('/keycount', methods=['GET'])
def keycount():
    key_count = 0
    for k in redis_client.keys('*'):
        key_count += 1
    return str(key_count)