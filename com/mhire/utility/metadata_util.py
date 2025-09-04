import logging
from googleapiclient import discovery
from googleapiclient.errors import HttpError

class MetadataHelper:
    def __init__(self, project_id, zone, instance_name):
        self.compute = discovery.build('compute', 'v1')
        self.project_id = project_id
        self.zone = zone
        self.instance_name = instance_name

    def get_instance_info(self):
        """Fetches existing instance metadata."""
        try:
            return self.compute.instances().get(
                project=self.project_id,
                zone=self.zone,
                instance=self.instance_name
            ).execute()
        except HttpError as e:
            logging.error(f"Error fetching instance information: {e}")
            raise

    def read_all_metadata(self):
        """Fetches all instance metadata as a dictionary."""
        try:
            instance_metadata = self.get_instance_info()
            metadata_items = instance_metadata['metadata'].get('items', [])
            return {item['key']: item['value'] for item in metadata_items}
        except HttpError as e:
            logging.error(f"Error fetching instance metadata: {e}")
            raise

    def update_metadata(self, key, value):
        """Updates a specific metadata key."""
        try:
            instance_metadata = self.get_instance_info()
            fingerprint = instance_metadata['metadata']['fingerprint']
            metadata_items = instance_metadata['metadata'].get('items', [])
            
            updated = False
            for item in metadata_items:
                if item['key'] == key:
                    item['value'] = value
                    updated = True
                    break
            if not updated:
                metadata_items.append({'key': key, 'value': value})

            metadata = {"fingerprint": fingerprint, "items": metadata_items}
            return self.compute.instances().setMetadata(
                project=self.project_id,
                zone=self.zone,
                instance=self.instance_name,
                body=metadata
            ).execute()
        except HttpError as e:
            logging.error(f"Error updating instance metadata: {e}")
            raise