import requests

from celery import Celery
import subprocess
import requests
from time import sleep
import json
import os
import redis
from models import ClassyFireEntity
from app import db

#import requests_cache
#requests_cache.install_cache('/data/request_cache')

print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='rpc://classyfire-mqrabbit', broker='pyamqp://classyfire-mqrabbit')

#redis_client = redis.Redis(host='classyfire-redis', port=6379, db=0)

url = "http://classyfire.wishartlab.com"
#url = "https://cfb.fiehnlab.ucdavis.edu"

@celery_instance.task(rate_limit="8/s")
#@celery_instance.task()
def get_entity(inchikey, return_format="json"):
    """Given a InChIKey for a previously queried structure, fetch the
     classification results.
    :param inchikey: An InChIKey for a previously calculated chemical structure
    :type inchikey: str
    :param return_format: desired return format. valid types are json, csv or sdf
    :type return_format: str
    :return: query information
    :rtype: str
    >>> get_entity("ATUOYWHBWRKTHZ-UHFFFAOYSA-N", 'csv')
    >>> get_entity("ATUOYWHBWRKTHZ-UHFFFAOYSA-N", 'json')
    >>> get_entity("ATUOYWHBWRKTHZ-UHFFFAOYSA-N", 'sdf')
    """
    entity_name = "%s.%s" % (inchikey, return_format)
    
    try:
        db_record = ClassyFireEntity.get(ClassyFireEntity.inchikey == entity_name)
        if db_record.status == "DONE":
            return db_record.responsetext
    except:
        print("entry in DB not found")

    inchikey = inchikey.replace('InChIKey=', '')
    r = requests.get('%s/entities/%s.%s' % (url, inchikey, return_format),
                    headers={
                        "Content-Type": "application/%s" % return_format})

    try:
        r.raise_for_status()
    except:
        ClassyFireEntity.create(
            inchikey=entity_name,
            responsetext="",
            status="ERROR"
        )
        open("/data/error_keys.txt", "a").write(inchikey + "\n")
        raise

    #TODO: will need to update rather than create if already exists
    ClassyFireEntity.create(
        inchikey=entity_name,
        responsetext=r.text,
        status="DONE"
    )

    return r.text

@celery_instance.task()
def populate_batch_task(query_id, return_format="json"):
    r = requests.get('%s/queries/%s.%s' % (url, query_id, return_format))

    r.raise_for_status()

    all_entities = r.json()["entities"]
    total_number_of_pages = r.json()["number_of_pages"]

    for page in range(2, total_number_of_pages + 1):
        while True:
            r = requests.get('%s/queries/%s.%s?page=%d' % (url, query_id, return_format, page))
            try:
                r.raise_for_status()
            except KeyboardInterrupt:
                raise
            except:
                if r.status_code == 429:
                    print("Retrying timeout")
                    sleep(1)
                    continue
                else:
                    raise
            break

        print(page, len(all_entities))
        all_entities += r.json()["entities"]
        
    populate_entities(all_entities)


@celery_instance.task()
def populate_entities(entities_list):
    with db.atomic():
        for i, entity in enumerate(entities_list):
            try:
                entity_name = "{}.{}".format(entity["inchikey"].replace("InChIKey=", ""), "json")
                if i % 100 == 0:
                    print(entity_name, "populating", i)
                ClassyFireEntity.get_or_create(
                    inchikey=entity_name,
                    responsetext=json.dumps(entity),
                    status="DONE"
                )
            except KeyboardInterrupt:
                raise
            except:
                print("ERROR", entity)

@celery_instance.task()
def get_entities_batch(key_list):
    output_entities = []
    for key in key_list:
        db_entry = ClassyFireEntity.get(ClassyFireEntity.inchikey == key)
        output_entities.append(json.loads(db_entry.responsetext))
    return output_entities


@celery_instance.task()
def get_all_keys():
    output_keys = []
    for entry in ClassyFireEntity.select().dicts():
        output_keys.append(entry["inchikey"])

    return output_keys
