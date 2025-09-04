import os
import shutil
from datetime import datetime

# Function to clear storage
def clear_storage():
    for root, dirs, files in os.walk("/llm-utility/"):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

# Function to ensure the log file exists
def ensure_log_file_exists():
    if not os.path.exists(log_file):
        # Create the log file if it does not exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "w") as log_f:
            log_f.write("Log File Created\n")

# Function to log messages with timestamps
def log(message):
    ensure_log_file_exists()
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(log_file, "a") as log_f:
        log_f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

# Function to log errors with timestamps
def log_error(message):
    ensure_log_file_exists()
    timestamp = datetime.now().strftime("%H:%M:%S")
    error_message = f"{timestamp} ERROR: {message}"
    with open(log_file, "a") as log_f:
        log_f.write(f"{error_message}\n")
    print(error_message)

# Path for the log file
log_file = f"/llm-utility/logs.txt"
gsutil_url_log = "gs://fine_tuning_llm_testing/logs/"