import requests
from celery import Celery
import subprocess
import requests
from time import sleep
import json
import os
import redis
from models import ClassyFireEntity, FailCaseDB
from app import db
from app import retry_db
print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='rpc://classyfire-mqrabbit', broker='pyamqp://classyfire-mqrabbit')

#redis_client = redis.Redis(host='classyfire-redis', port=6379, db=0)

url = "http://classyfire.wishartlab.com"
#url = "https://cfb.fiehnlab.ucdavis.edu"

@celery_instance.task()
def record_failure(entity_name):
    FailCaseDB.create(
            fullstructure=entity_name,
            status="FAILED")
    
#test case url entities/fullstructure?entity_name=CN1C=NC2=C1C(=O)N(C(=O)N2C)C
@celery_instance.task(trail=True, rate_limit="8/m")
def classify_full_structure(smiles, inchikey, return_format="json", label=""): 
    """Given the smiles or InChI string for an unseen
    structure, launch a new query"""

    #query to get the id of the structure
    r = requests.post(url + '/queries.json', data='{"label": "%s", ''"query_input": "%s", "query_type": "STRUCTURE"}'% (label, smiles),headers={"Content-Type": "application/json"}) 
    query_id = r.json()['id'] 
    entity_name = "%s.%s" % (smiles, return_format)
    
    #actually get the info associated with the structure
    r = requests.get('%s/queries/%s.%s' % (url,query_id, return_format))
    full_response = json.loads(r.content)
    print(full_response, flush=True)

    # Always wait 10 seconds
    sleep(10)

    # Trying to get the inchi back now
    get_entity(inchikey)

    return None


@celery_instance.task(rate_limit="8/m")
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

    db_record = None
    
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
        if db_record is None:
            ClassyFireEntity.create(
                inchikey=entity_name,
                responsetext="",
                status="ERROR"
            )
        open("/data/error_keys.txt", "a").write(inchikey + "\n")
        raise

    if len(r.text) < 10:
        raise Exception
    
    try:
        db_record.responsetext = r.text
        db_record.status = "DONE"
        db_record.save()
    except:
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
