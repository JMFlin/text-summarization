import logging
logger = logging.getLogger()

def upload_blob(client, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    logger.info(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

def write_to_bq(client, table, row_to_insert): 
    """ Streaming insert a row to q BigQuery table """
    errors = client.insert_rows_json(table, row_to_insert)
    if errors == []:
        logger.info("Added new row to BQ")
    else:
        logger.error("Encountered errors while inserting rows: {}".format(errors))
