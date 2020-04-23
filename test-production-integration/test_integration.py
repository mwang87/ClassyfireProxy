import requests

PRODUCTION_URL = "gnps-classyfire.ucsd.edu"

def test_production():
    url = f"https://{PRODUCTION_URL}/heartbeat"
    r = requests.get(url)
    r.raise_for_status()
    
def test_keycount():
    url = f"https://{PRODUCTION_URL}/keycount"
    r  = requests.get(url)
    r.raise_for_status()
    
def test_inchi_key():
    url = f"https://{PRODUCTION_URL}/entities/inchikey?entity_name=RYYVLZVUVIJVGH-UHFFFAOYSA-N.json"
    r  = requests.get(url)
    r.raise_for_status()

def test_inchi():
    url = f"https://{PRODUCTION_URL}/entities/inchi?entity_name=InChI=1S/C8H10N4O2/c1-10-4-9-6-5(10)7(13)12(3)8(14)11(6)2/h4H,1-3H3.json"
    r = requests.get(url)
    r.raise_for_status()

def test_smiles():
    url = f"https://{PRODUCTION_URL}/entities/smiles?entity_name=CN1C=NC2=C1C(=O)N(C(=O)N2C)C.json"
    r = requests.get(url)
    r.raise_for_status()


