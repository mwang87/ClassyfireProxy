#!/usr/bin/python3

import sys
import requests
from time import sleep
import requests_cache
requests_cache.install_cache('/data/request_cache')

def retreieve_query(query_id, return_format="json"):
    url = "http://classyfire.wishartlab.com"
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
        

    print(len(all_entities))

    return all_entities

query_id = sys.argv[1]
all_entities = retreieve_query(query_id)

from classyfire_tasks import populate_entities
populate_entities(all_entities)
