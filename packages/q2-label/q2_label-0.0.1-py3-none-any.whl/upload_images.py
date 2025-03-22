from azure.storage.blob import ContainerClient
from .local_storage import LocalStorageDirectory

class ImageDirectoryUpload(LocalStorageDirectory):
    # wrapper class to upload image_directory
    
    def __init__(self, sas_url):
        self.container_client = ContainerClient.from_container_url(container_url=sas_url)

    def upload_directory(self, local_directory, project_name):
        self.upload_dir(local_directory, self.container_client, project_name + "_images_initial")