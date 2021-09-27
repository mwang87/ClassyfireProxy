import requests

PRODUCTION_URL = "gnps-classyfire.ucsd.edu"

def test_url(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        return r
    except:
        print("Timeout", url)
        return None

def test_production():
    url = f"https://{PRODUCTION_URL}/heartbeat"
    r = test_url(url)
    r.raise_for_status()
    
def test_keycount():
    url = f"https://{PRODUCTION_URL}/keycount"
    r  = test_url(url)
    r.raise_for_status()
    
def test_caffeine():
    url = f"https://{PRODUCTION_URL}/entities/RYYVLZVUVIJVGH-UHFFFAOYSA-N.json"
    r  = test_url(url)
    r.raise_for_status()
