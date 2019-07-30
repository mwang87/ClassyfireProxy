import json
import requests
import sys


def get_entity(inchikey, return_format="json"):
    url = "http://localhost:5057"

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


all_structures = json.loads(open(sys.argv[1]).read())
for structure in all_structures:
    inchikey = structure["inchi_key_rdkit"]
    print(inchikey)
    get_entity(inchikey)