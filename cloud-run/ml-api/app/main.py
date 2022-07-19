import os
import logging
from flask import Flask, jsonify, request
from transformers import pipeline
from six.moves import http_client
from google.auth import jwt
from torch import cuda
#from transformers import PegasusTokenizer, PegasusForConditionalGeneration
from transformers import BartTokenizer, BartForConditionalGeneration

# Pretrained model can be chosen from https://huggingface.co/models?filter=pytorch&search=pegasus
# git clone https://huggingface.co/google/pegasus-xsum
# https://github.com/huggingface/transformers#quick-tour

logging.basicConfig(format='%(asctime)s %(levelname)-8s:%(message)s', 
                    level=logging.DEBUG, 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()

PRETRAINED = 'bart-large-cnn' # pegasus-xsum
DEVICE = 'cuda' if cuda.is_available() else 'cpu'
USE_LOCAL_MODEL = False

app = Flask(__name__)

def receive_authorized_post_request(request):
    """
    receive_authorized_post_request takes the "Authorization" header from a
    request, decodes it using the google-auth client library, and returns
    back the email from the header to the caller.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header:

        # split the auth type and value from the header.
        auth_type, creds = auth_header.split(" ", 1)

        if auth_type.lower() == "bearer":
            claims = jwt.decode(creds, verify=False)
            logger.info(f"Hello, {claims['email']}!\n")
            return 200

        else:
            logger.error(f"Unhandled header format ({auth_type}).\n")
            return 400
    return 400

@app.route('/api/health_check', methods=['GET'])
def health_check():
    resp = jsonify(success=True)
    return resp

@app.route('/summarize', methods=['POST'])
def summarize():

    if receive_authorized_post_request(request) == 400:
        return jsonify(code=400, message="bad request")

    payload = request.get_json()
    logger.info(f"Received payload {type(payload)} {payload}")

    if USE_LOCAL_MODEL:

        #MODEL = PegasusForConditionalGeneration.from_pretrained(PRETRAINED).to(DEVICE)
        #TOKENIZER = PegasusTokenizer.from_pretrained(PRETRAINED)
        model = BartForConditionalGeneration.from_pretrained(PRETRAINED).to(DEVICE)
        tokenizer = BartTokenizer.from_pretrained(PRETRAINED)

        logger.info(f"Preprocessing input")
        inputs = tokenizer([payload["text"]], max_length=1024*2, return_tensors="pt", truncation=True).to(DEVICE)

        logger.info(f"Transforming input to summary")
        summary_ids = model.generate(inputs["input_ids"], num_beams=4, min_length=10, max_length=1024*2)

        logger.info(f"Decoding summary")
        text = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    else:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        text = summarizer(payload["text"])[0]["summary_text"]

    logger.info({"summary_text": text})

    return jsonify({"summary_text": text}), 201

@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 8081)), debug=True)
