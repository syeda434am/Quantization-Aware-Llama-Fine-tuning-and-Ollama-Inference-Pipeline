import os
import zipfile
import logging
from datetime import datetime

class ZipUtil:
    def zip_model_files(self, output_dir, model_name):
        """Zips all model files in a directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file_name = f"{model_name}_{timestamp}.zip"
        zip_file_path = os.path.join(output_dir, zip_file_name)

        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, output_dir))
                    
        logging.info(f"Model files zipped into: {zip_file_name}")
        return zip_file_path

    def unzip_file(self, zip_file_path, extract_to_path=None):
        """Unzips a file to the given directory."""
        if extract_to_path is None:
            extract_to_path = os.path.dirname(zip_file_path)

        os.makedirs(extract_to_path, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
            
        logging.info(f"Extracted {zip_file_path} to {extract_to_path}")