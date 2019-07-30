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

r = redis.Redis(host='classyfire-redis', port=6379, db=0)

@app.route('/entities/<entity_name>', methods=['GET'])
#@cache.cached()
def entities(entity_name):
    inchi_key = entity_name.split(".")[0]
    return_format = entity_name.split(".")[1]
    result = r.get(entity_name)
    
    if result == None:
        result = get_entity.delay(inchi_key, return_format=return_format)
        while(1):
            if result.ready():
                break
            sleep(3)
        result = result.get()

        #TODO: Check that the response is ok

        r.set(entity_name, result)
    
    return result