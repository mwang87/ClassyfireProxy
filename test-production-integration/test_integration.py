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
    
def test_caffeine():
    url = f"https://{PRODUCTION_URL}/entities/RYYVLZVUVIJVGH-UHFFFAOYSA-N.json"
    r  = requests.get(url)
    r.raise_for_status()
