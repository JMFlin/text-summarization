import os
import logging
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from google.cloud import storage
from PIL import Image
import base64
from io import BytesIO
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

# https://stackoverflow.com/questions/67200980/how-do-i-trigger-http-google-cloud-functions-that-are-private


def create_encoded_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue())
    return encoded_image

def create_image_id(string):
    return hashlib.md5(string.encode('utf_8')).hexdigest()

def main():

    st.title('Text summarizer')
    st.markdown('#')

    st.sidebar.markdown(body = """
    ## App Info
    
    ### Instructions
    Upload an image with text from your local files and have it be summarized.
    The file must be in .png format.

    ### Model
    Model is from Huggingface

    """)

    uploaded_file = st.file_uploader(label="Choose a file", type=['png'], accept_multiple_files=False, key=None)

    if uploaded_file is not None:

        logger.info(f'File named {uploaded_file.name} was uploaded by user to application')

        image = Image.open(uploaded_file)

        st.image(image, caption='Image uploaded by user')

        id = create_image_id(uploaded_file.name)
        encoded_image = create_encoded_image(image)

        data = {
            "id": id,
            "image": encoded_image
        }

        with st.spinner('Waiting for summarization...'):
            response = requests.post(URL, json=data, headers=HEADERS).json()
            st.success(f'{response["text"]}')

        logger.info(f"API response {response}")


main()
