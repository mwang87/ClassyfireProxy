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

r = redis.Redis(host='redis', port=6379, db=0)

@app.route('/entities/', methods=['GET'])
#@cache.cached()
def entities():
    inchi_key = request.values["inchikey"]
    result = r.get(inchi_key)
    if result == None:
        result = get_entity.delay(inchi_key)
        while(1):
            if result.ready():
                break
            sleep(3)
        result = result.get()

        r.set(inchi_key, result)
    
    return result