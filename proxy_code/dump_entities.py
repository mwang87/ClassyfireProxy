#!/usr/bin/python3

import sys
import json
from classyfire_tasks import get_entities_batch
from classyfire_tasks import get_all_keys


def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

#output_folder = sys.argv[1]
page_size = 10000

all_keys = get_all_keys()
all_lists = list(divide_chunks(all_keys, page_size))

for i in range(len(all_lists)):
    print(i, len(all_lists))
    output_filename = "/data/dump/%d_dump.json" % (i)
    output_entities = get_entities_batch(all_lists[i])
    open(output_filename, "w").write(json.dumps(output_entities))

