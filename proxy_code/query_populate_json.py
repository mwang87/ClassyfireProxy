#!/usr/bin/python3

import sys
import os
import requests
from time import sleep
import glob
import json
from classyfire_tasks import populate_entities

all_json_files = glob.glob(os.path.join(sys.argv[1], "**/*.json"), recursive=True)
for json_filename in all_json_files:
    try:
        print(os.path.basename(json_filename))
        dump_json = json.loads(open(json_filename, encoding='ascii',errors='ignore').read())

        #This is the same format as the dump
        populate_entities(dump_json)

        # if "entities" in entry:
        #     all_entities = dump_json["entities"]
        #     populate_entities(all_entities)
        # else:
        #     populate_entities([dump_json])
    except KeyboardInterrupt:
        raise
    except:
        raise
        print(json_filename, "failed")




