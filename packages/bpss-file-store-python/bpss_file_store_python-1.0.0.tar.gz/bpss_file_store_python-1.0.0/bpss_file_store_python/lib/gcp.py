import datetime
from google.cloud import storage
import os
from .constant import default_expiration_time, default_content_type

default_bucket_name = os.environ.get('BUCKET_NAME')

def gcp_upload(file_path, data, config):
    """
    Uploads a file to Google Cloud Storage.

    Args:
        file_path (str): The path or key under which the file will be stored.
        data (Buffer|Readable|string): The data or contents of the file to be uploaded.
            It can be provided as a Buffer, a Readable stream, or a string.
        config (dict): The configuration object.
            - bucketName (str): The name of the Google Cloud Storage bucket.
            - mimeType (str): The MIME type of the file.

    Returns:
        dict: An object representing the file path, if the upload is successful.

    Raises:
        Exception: If an error occurs during the upload process.
    """
    bucket_name = config.get('bucketName', default_bucket_name)
    mime_type = config.get('mimeType', default_content_type)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.content_type = mime_type

    blob.upload_from_string(data)
    print('File uploaded successfully on gcp')
    return {
        'Key': file_path
    }


def gcp_download(file_path, config):
    """
    Downloads a file from Google Cloud Storage.

    Args:
        file_path (str): The path to the file to download.
        config (dict): The configuration object.
            - bucketName (str): The name of the Google Cloud Storage bucket.

    Returns:
        bytes: The downloaded file data.

    Raises:
        Exception: If an error occurs during the download process.
    """
    bucket_name = config.get('bucketName', default_bucket_name)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    data = blob.download_as_bytes()

    return {
        'ContentType': blob.content_type,
        'Body': data
    }


def delete_gcs_object(config):
    """
    Deletes a GCS object.

    Args:
        config (dict): The configuration object.
            - filePath (str): The path to the file to delete.
            - bucketName (str): The name of the bucket to delete the file from. Defaults to "default_bucket_name".

    Raises:
        Exception: If an error occurs during the deletion process.
    """
    bucket_name = config.get('bucketName', default_bucket_name)
    file_path = config['filePath']

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.delete()

    print(f'File "{file_path}" deleted successfully.')

def get_gcs_presigned_url(config):
    """
    Gets a presigned URL for a GCS object.

    Args:
        config (dict): The configuration object.
            - filePath (str): The path to the file to get a presigned URL for.
            - expirationTime (int): The expiration time for the presigned URL in seconds. Defaults to default_expiration_time.
            - bucketName (str): The name of the bucket to get a presigned URL for. Defaults to "default_bucket_name".

    Returns:
        str: The presigned URL.

    Raises:
        Exception: If an error occurs during the generation of the presigned URL.
    """
    file_path = config['filePath']
    expiration_time = config.get('expirationTime', default_expiration_time)
    bucket_name = config.get('bucketName', default_bucket_name)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(seconds=expiration_time),
        method="GET"
    )

    return url
