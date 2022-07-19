import os
import uuid

import requests
import google.auth.transport.requests
import google.oauth2.id_token
import google.auth

import urllib

import google.auth.transport.requests
import google.oauth2.id_token

import subprocess


PROJECT_ID = subprocess.run(["gcloud", "config", "get-value", "project"],
                            stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip("\n")

creds, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
id_token = creds.token

headers = {
    "Authorization": f"Bearer {id_token}",
    'Content-Type': 'application/json',
}

req = urllib.request.Request(f"https://europe-west1-{PROJECT_ID}.cloudfunctions.net/text-summarization")

auth_req = google.auth.transport.requests.Request()
id_token = google.oauth2.id_token.fetch_id_token(auth_req, f"https://europe-west1-{PROJECT_ID}.cloudfunctions.net")

req.add_header("Authorization", f"Bearer {id_token}")
response = urllib.request.urlopen(req)

def test_args():
    BASE_URL = f"https://europe-west1-{PROJECT_ID}.cloudfunctions.net"

    name = str(uuid.uuid4())
    res = requests.post(
      '{}/text-summarization'.format(BASE_URL),
      headers=headers,
      json={
        "id": name,
        "image": "DJFHDJKFHB89327489327"
      }
    )
    print(res)

test_args()

