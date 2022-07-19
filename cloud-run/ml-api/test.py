import os
import json
import base64
import logging
from datetime import datetime
import urllib
import google.auth.transport.requests
import google.oauth2.id_token
import google.auth


logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

ENDPOINT="https://text-summarization-ml-api-axswvbmypa-ew.a.run.app/summarize"
AUDIENCE="https://text-summarization-ml-api-axswvbmypa-ew.a.run.app"




def make_authorized_post_request(endpoint, audience, data):
    """
    make_authorized_post_request makes a POST request to the specified HTTP endpoint
    by authenticating with the ID token obtained from the google-auth client library
    using the specified audience value.
    """

    # Cloud Run uses your service's hostname as the `audience` value
    # audience = 'https://my-cloud-run-service.run.app/'
    # For Cloud Run, `endpoint` is the URL (hostname + path) receiving the request
    # endpoint = 'https://my-cloud-run-service.run.app/my/awesome/url'

    data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data)

    try:
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    except:
        creds, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        id_token = creds.token

    req.add_header("Authorization", f"Bearer {id_token}")
    req.add_header("Content-Type", "application/json")

    response = urllib.request.urlopen(req).read().decode('UTF-8')

    return json.loads(response)



def test_health_check():
    print(f"==========================")
    print("Testing health_check route")
    print(f"==========================\n")

    import requests

    creds, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    id_token = creds.token

    headers = {
        "Authorization": f"Bearer {id_token}",
        'Content-Type': 'application/json',
    }
    url = AUDIENCE + "/api/health_check"
    #url = "http://127.0.0.1:5000/api/health_check"
    r = requests.get(url=url, headers=headers)
    print(r)
    print(f"{r.json()}\n")

#test_health_check()

#data = {
#    "text": "He did something or something else. He did something or something else. He did something or something else "
#}
#
## Call ml api
#response = make_authorized_post_request(
#    endpoint=ENDPOINT,
#    audience=AUDIENCE,
#    data=data)
#
#print(response)
