import os
import traceback
import logging
import requests
from com.mhire.utility.metadata_util import MetadataHelper
from com.mhire.utility.util import clear_storage, log, log_error, log_file, gsutil_url_log
from com.mhire.utility.gcp_util import GCPUtil
from com.mhire.utility.docker_util import DockerUtil
from com.mhire.fine_tuning.fine_tuning import FineTuneModel
from com.mhire.fine_tuning.quantize import quantize

def fetch_and_validate_metadata():

    project_id = requests.get("http://metadata.google.internal/computeMetadata/v1/project/project-id", headers={"Metadata-Flavor": "Google"}).text
    vm_zone = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/zone", headers={"Metadata-Flavor": "Google"}).text.split('/')[-1]  # Extract only the zone name
    vm_instance = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/name", headers={"Metadata-Flavor": "Google"}).text
    
    # Initialize utility instances
    metaDataHelper = MetadataHelper(project_id, vm_zone, vm_instance)
    gcp_util = GCPUtil()
    """Fetches metadata and ensures that all necessary variables are available."""
    log("Fetching metadata from instance...")
    
    metaData = metaDataHelper.read_all_metadata()
    
    model_path = metaData.get("model_path")
    dataset_path = metaData.get("dataset_path")
    model_save_name = metaData.get("model_save_name")
    full_docker_image_name = metaData.get("docker_image")
    fine_tuning_id = metaData.get("fine_tuning_id")
    #status = metaData.get("status")

    # Check that required metadata fields are present
    if not all([model_path, dataset_path, model_save_name, fine_tuning_id, full_docker_image_name]):
        log_error("One or more required metadata variables are empty.")
    
    log("Metadata fetched successfully.")
    return model_path, dataset_path, model_save_name, fine_tuning_id, full_docker_image_name

def main():

    gcp_util = GCPUtil(service_account_key_path="/tmp/service_account_key.json")
    fine_tuning = FineTuneModel()
    docker_util = DockerUtil()

    """Main function to handle the startup process for fine-tuning."""
    log("Starting fine-tuning startup script")
    
    try:
        # Fetch and validate metadata
        model_path, dataset_path, model_save_name, fine_tuning_id, full_docker_image_name = fetch_and_validate_metadata()

        # Clear any existing storage
        clear_storage()
        log("Storage cleared.")

        working_directory = "/llm-utility/"

        # Download data and model.zip in instance and unzip the model
        # Download and unzip the model from Google Cloud Storage
        log(f"Downloading the model from: {model_path}")
        gcp_util.download_from_gcs(model_path, working_directory)
        #log(f"Model downloaded successfully.")

        # Download the dataset from Google Cloud Storage
        log(f"Downloading dataset to Google Cloud Storage: {dataset_path}")
        gcp_util.download_from_gcs(dataset_path, working_directory)
        log("Dataset downloaded successfully.")    

        # Perform fine-tuning and save in instance's local path
        # Define paths for the fine-tuning process
        model_local_path = working_directory  # Path where the model is located
        dataset_local_path = os.path.join(working_directory, os.path.basename(dataset_path))  # Path to the downloaded dataset

        # Perform fine-tuning using the specified paths
        fine_tuning.fine_tune_model(model_local_path, dataset_local_path)

        log("Fine-tuning completed successfully.")

        # Zip fine-tuned model and upload in Cloud storage

        # Quantize the model and save the gguf file in instance 

        # Build, tag docker image
        docker_util.build_docker_image(full_docker_image_name)

        # Push Docker image (Assuming the full image name includes registry)
        docker_util.push_docker_image(full_docker_image_name)  # Pass registry URL
    
        # Create model directory first

        log_file_path = os.path.join(working_directory, f"{fine_tuning_id}.txt")
        if os.path.exists(log_file):
            os.rename(log_file, log_file_path)
            log(f"Log file renamed to: {log_file_path}")
        else:
            log_error("Log file not found for renaming.")
            raise FileNotFoundError(f"Log file {log_file} not found.")

        # Upload the renamed log file to Cloud Storage
        gcp_util.upload_file_to_gcs(log_file_path, gsutil_url_log)

    except Exception as e:
        log_error(f"Error encountered during fine-tuning setup: {traceback.format_exc()}")
        log_error(f"Exception: {str(e)}")
    except ModuleNotFoundError as e:
        log_error(f"No module named 'llm_utility': {str(e)}")

if __name__ == "__main__":
    main()