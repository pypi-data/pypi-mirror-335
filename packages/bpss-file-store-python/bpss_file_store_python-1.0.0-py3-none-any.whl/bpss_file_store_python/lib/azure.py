import os
import datetime
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas, ContentSettings
from .constant import default_content_type, default_expiration_time

connection_string = os.environ.get('AZURE_BLOB_STORAGE_CONNECTION_STRING')
default_container_name = os.environ.get('BUCKET_NAME')

def azure_upload(file_path, data, config):
    """
    Uploads a file to Azure Blob Storage using the Azure Storage SDK.

    Args:
        file_path (str): The path or key under which the file will be stored.
        data (Buffer|Readable|string): The data or contents of the file to be uploaded.
            It can be provided as a Buffer, a Readable stream, or a string.
        config (dict): An optional configuration object.
            - bucketName (str): The name of the Azure Blob Storage container.
            - mimeType (str): The MIME type of the file being uploaded.

    Returns:
        dict: An object representing the file path, if the upload is successful.

    Raises:
        Exception: If an error occurs during the upload.
    """
    container_name = config.get('bucketName', default_container_name)
    mime_type = config.get('mimeType', default_content_type)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    block_blob_client = container_client.get_blob_client(file_path)

    upload_options = {
        'blob_type': 'BlockBlob',
        'max_concurrency': 20
    }

    upload_options['content_settings'] = ContentSettings(content_type=mime_type)

    block_blob_client.upload_blob(data, **upload_options)
    print('File uploaded successfully on azure')
    return {
        'Key': file_path
    }


def azure_download(file_name, config):
    """
    Downloads a file from Azure Blob Storage using the Azure Storage SDK.

    Args:
        file_name (str): The name of the file to download.
        config (dict): An optional configuration object.
            - bucketName (str): The name of the Azure Blob Storage container.

    Returns:
        bytes: The file content as a byte string.

    Raises:
        Exception: If an error occurs during the download.
    """
    container_name = config.get('bucketName', default_container_name)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    block_blob_client = container_client.get_blob_client(file_name)

    download_stream = block_blob_client.download_blob()
    content = download_stream.readall()
    properties = block_blob_client.get_blob_properties()
    content_settings = properties.get('content_settings', {})
    content_type = content_settings.get('content_type')
    return {
        'ContentType': content_type,
        'Body': content
    }


def delete_azure_blob(config):
    """
    Deletes an Azure blob.

    Args:
        config (dict): The configuration object.
            - bucketName (str): The name of the Azure blob container.
            - filePath (str): The name of the Azure blob file.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the deletion.
    """
    container_name = config.get('bucketName', default_container_name)
    file_path = config['filePath']

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    block_blob_client = container_client.get_blob_client(file_path)

    block_blob_client.delete_blob()

    print(f'File "{file_path}" deleted successfully.')


def get_azure_blob_presigned_url(config):
    """
    Gets a presigned URL for an Azure blob.

    Args:
        config (dict): The configuration object.
            - filePath (str): The path to the file to get a presigned URL for.
            - expirationTime (int): The expiration time for the presigned URL in seconds. Defaults default_expiration_time.
            - bucketName (str): The name of the bucket to get a presigned URL for. Defaults to "default_bucket_name".

    Returns:
        str: The presigned URL.

    Raises:
        Exception: If an error occurs during the generation of the presigned URL.
    """
    container_name = config.get('bucketName', default_container_name)
    expiration_time = config.get('expirationTime',default_expiration_time)
    file_path = config['filePath']

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(file_path)

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=file_path,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.datetime.utcnow() + datetime.timedelta(seconds=expiration_time)
    )

    presigned_url = blob_client.url + '?' + sas_token

    return presigned_url
