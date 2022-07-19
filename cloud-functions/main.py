import os
import json
import base64
import logging
from datetime import datetime
from PIL import Image
from utils import upload_blob, write_to_bq
from flask import Flask, request, jsonify, escape
import urllib

import functions_framework

# Clients
from google.cloud import storage
from google.cloud import bigquery
from google.cloud import vision
from google.cloud import translate_v2 as translate

import google.auth.transport.requests
import google.oauth2.id_token


logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

# Set urls for make_authorized_post_request to authenticate with google-auth
ENDPOINT="https://text-summarization-ml-api-axswvbmypa-ew.a.run.app/summarize"
AUDIENCE="https://text-summarization-ml-api-axswvbmypa-ew.a.run.app"

# Initialize clients
STORAGE_CLIENT = storage.Client()
BIGQUERY_CLIENT = bigquery.Client()
TRANSLATE_CLIENT = translate.Client()
VISION_CLIENT = vision.ImageAnnotatorClient()

# Set GCP specific variables
BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
TARGET_LANG = os.environ["TARGET_LANG"]
INSERT_TABLE = os.environ["INSERT_TABLE"]

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

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)

    req.add_header("Authorization", f"Bearer {id_token}")
    req.add_header("Content-Type", "application/json")

    response = urllib.request.urlopen(req).read().decode('UTF-8')

    return json.loads(response)

@functions_framework.http
def summarize_text(request):
    """Cloud Function triggered by HTTP request.
        Detect the language of the source text previously extracted by ocr.
    Args:
        id: Unique image id by taking hash of file.
        image: base64 encoded image.
    Returns:
        Summary of the text in the image.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'image' in request_json:
        base64_img = request_json['image']
    else:
        return "Correct image parameter not found", 404

    if request_json and 'id' in request_json:
        id = request_json['id']
    else:
        return "Correct id parameter not found", 404

    try:
        image = base64.b64decode(base64_img)
        with open("/tmp/image.png", 'wb') as f:
            f.write(image)
    except Exception as err:
        logging.error(f'Failed to decode image: {type(err)}: {err}')
        return "Unable to decode base64 image", 500

    logger.info("Uploading image to storage")

    upload_blob(
        client=STORAGE_CLIENT,
        bucket_name=BUCKET,
        source_file_name="/tmp/image.png",
        destination_blob_name=id + ".png"
    )

    image_loc = "gs://" + BUCKET + "/" + id + ".png"
    logger.info("Looking for text in image {}".format(image_loc))
    text = detect_text(image)

    if not text:
        return 404

    source_language = detect_language(text)
    logger.info("Detected language {} form text.".format(source_language))

    if source_language != TARGET_LANG:
        text = translate_text(text, source_language, TARGET_LANG)

    data = {
        "text": text
    }

    # Call ml api
    response = make_authorized_post_request(
        endpoint=ENDPOINT,
        audience=AUDIENCE,
        data=data)


#    #ENDPOINT="http://localhost:8081/summarize"
#    data = json.dumps(data).encode("utf-8")
#    req = urllib.request.Request(ENDPOINT, data=data)
#
#    auth_req = google.auth.transport.requests.Request()
#    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
#
#    req.add_header("Authorization", f"Bearer {id_token}")
#    req.add_header("Content-Type", "application/json")
#
#    response = urllib.request.urlopen(req).read().decode('UTF-8')
#
#    response = json.loads(response)

    logger.info(f"ML API response: {response}")

    write_to_bq(
        client=BIGQUERY_CLIENT,
        table=INSERT_TABLE,
        row_to_insert=[
            {
                u"ID": id, 
                u"INPUT_TEXT": text,
                u"OUTPUT_TEXT": response["summary_text"],
                u"IMAGE_FILE_LOCATION": image_loc,
                u"SOURCE_LANGUAGE": source_language,
                u"TARGET_LANGUAGE": TARGET_LANG,
                u"INSERT_TIME": str(datetime.now())
            }
        ]
    )

    return jsonify({"text": response["summary_text"]}), 200


def detect_language(text):

    detect_language_response = TRANSLATE_CLIENT.detect_language(text)
    source_language = detect_language_response["language"]

    return source_language

def detect_text(image):

#    image = vision.types.Image(content=image)
    image = vision.Image(content=image)

    text_detection_response = VISION_CLIENT.text_detection(image=image)

    annotations = text_detection_response.text_annotations

    if len(annotations) > 0:
        text = annotations[0].description
    else:
        return None

    return text


def translate_text(text, source_language, target_language):
    """Translate text from source to target language."""

    logger.info("Translating text from {} to {}.".format(source_language, target_language))
    translated_text = TRANSLATE_CLIENT.translate(
        text, target_language=target_language, source_language=source_language
    )

    return translated_text["translatedText"]