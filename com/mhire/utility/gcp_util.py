import os
import logging
from google.cloud import storage
from google.oauth2 import service_account
from com.mhire.utility.zip_util import ZipUtil 
from com.mhire.utility.util import log, log_error

logging.getLogger('google.cloud').setLevel(logging.DEBUG)

class GCPUtil:
    def __init__(self, service_account_key_path=None):
        if service_account_key_path:
            # Use the provided service account key file
            credentials = service_account.Credentials.from_service_account_file(service_account_key_path)
            self.storage_client = storage.Client(credentials=credentials)
        else:
            # Default to ADC if no key file is provided
            self.storage_client = storage.Client()
        self.zip_util = ZipUtil()

    def upload_file_to_gcs(self, local_upload_path, gsutil_url):
        """Uploads a file to Google Cloud Storage at a specified path."""
        log(f"Starting upload of {local_upload_path} to {gsutil_url}")
        try:
            # Validate local file existence
            if not os.path.isfile(local_upload_path):
                log_error(f"Local file {local_upload_path} does not exist.")
                return  # Exit if the file doesn't exist

            # Ensure gsutil URL starts with 'gs://'
            if not gsutil_url.startswith("gs://"):
                log_error("Invalid gs:// URL provided.")
                return

            # Parse the gsutil URL to extract bucket name and blob path
            gs_path = gsutil_url[5:]
            if "/" not in gs_path:
                log_error("Invalid GCS URL format. Expected format: gs://<bucket-name>/<object-path>")
                raise ValueError("Invalid GCS URL format.")
            
            bucket_name, blob_path = gs_path.split("/", 1)

            # Handle cases where the GCS path ends with a slash ("/"), indicating a directory-like path
            if blob_path.endswith('/'):
                blob_path = os.path.join(blob_path, os.path.basename(local_upload_path))

            # Get the GCS bucket and blob (file in GCS)
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_path)

            # Perform the file upload
            log(f"Uploading {local_upload_path} to {gsutil_url}")
            blob.upload_from_filename(local_upload_path)

            # Check if the upload succeeded by verifying if the blob exists
            if blob.exists():
                log(f"File {local_upload_path} successfully uploaded to {gsutil_url}")
            else:
                log_error(f"File {local_upload_path} was uploaded but does not appear in GCS at {gsutil_url}")
        except Exception as e:
            # Log the specific error and raise the exception
            log_error(f"Error during file upload to GCS: {str(e)}")
            raise


    def download_from_gcs(self, gsutil_url, local_download_path):
        """Downloads a file from Google Cloud Storage."""
        logging.info(f"Downloading file from: {gsutil_url} to {local_download_path}")
        try:
            if gsutil_url.startswith("gs://"):
                gs_path = gsutil_url[5:]
                bucket_name, blob_path = gs_path.split("/", 1)
                bucket = self.storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_path)

                # Check if local_download_path is a directory
                if os.path.isdir(local_download_path):
                    # If it's a directory, use the original filename from the GCS path
                    local_download_path = os.path.join(local_download_path, os.path.basename(blob_path))

                # Ensure the directory for the file exists
                os.makedirs(os.path.dirname(local_download_path), exist_ok=True)

                # Download the file
                with open(local_download_path, "wb") as file:
                    blob.download_to_file(file)

                log(f"File downloaded to: {local_download_path}")

                # If the downloaded file is a zip file, extract it
                if local_download_path.endswith('.zip'):
                    extract_to_path = os.path.dirname(local_download_path)
                    self.zip_util.unzip_file(local_download_path, extract_to_path)
            else:
                log_error("Invalid gs:// URL.")
        except Exception as e:
            log_error(f"Error downloading file from GCS: {e}")
            raise