import requests

from celery import Celery
import subprocess
import requests
from time import sleep
import json
import os

print("Before Celery App")
celery_instance = Celery('cytoscape_tasks', backend='redis://classyfire-redis', broker='redis://classyfire-redis')

#@celery_instance.task(rate_limit="5/m")
@celery_instance.task(rate_limit="60/m")
def get_entity(inchikey, return_format="json"):
    #url = "http://classyfire.wishartlab.com"
    url = "https://cfb.fiehnlab.ucdavis.edu"

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
    inchikey = inchikey.replace('InChIKey=', '')
    r = requests.get('%s/entities/%s.%s' % (url, inchikey, return_format),
                     headers={
                         "Content-Type": "application/%s" % return_format})
    r.raise_for_status()
    return r.text
