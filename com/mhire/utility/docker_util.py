import docker
from docker.errors import DockerException
from com.mhire.utility.util import log
from com.mhire.utility.gcp_util import GCPUtil

class DockerUtil():
    def __init__(self):
        # Initialize the Docker client
        self.gcp_util = GCPUtil()
        self.client = docker.from_env()

    # Build and push Docker image directly to the registry
    def build_docker_image(self, full_image_name):
        # Full image path for the registry
        log(f"Building Docker image: {full_image_name}")
        
        try:
            # Build the Docker image and tag it directly for the registry
            image, logs = self.client.images.build(
                path="/LLM_Util/llm-utility", 
                dockerfile="Dockerfile", 
                tag=full_image_name, 
                nocache=True
            )
            # Log the build output
            for log_line in logs:
                log(log_line.get('stream', '').strip())

            log(f"Docker image {full_image_name} built successfully.")

            # Push the Docker image to the registry
            self.push_docker_image(full_image_name)  # <-- Passing image_name and tag here

        except DockerException as e:
            self.gcp_util.handle_error(f"Error building Docker image {full_image_name}: {str(e)}")

    def push_docker_logs(self, push_logs):
        for log_line in push_logs:
            if 'errorDetail' in log_line:
                log(f"Error pushing image: {log_line['errorDetail']['message']}")
                self.gcp_util.handle_error(f"Push failed: {log_line['errorDetail']['message']}")
                return False  # Stop execution if an error is found
            log(log_line.get('status', ''))
        return True

    # Push Docker image to Google Artifact Registry
    def push_docker_image(self, full_image_name):
        log(f"Pushing Docker image {full_image_name} to registry")
        try:
            # Push the Docker image and handle logs
            push_logs = self.client.images.push(full_image_name, stream=True, decode=True)
            if self.push_docker_logs(push_logs):  # Calling the push_docker_logs method
                log(f"Docker image {full_image_name} pushed to registry successfully.")
        except DockerException as e:
            self.gcp_util.handle_error(f"Error pushing Docker image {full_image_name}: {str(e)}")