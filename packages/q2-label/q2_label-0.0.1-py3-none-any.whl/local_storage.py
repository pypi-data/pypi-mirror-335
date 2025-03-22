import os
import zipfile

from .container_manipulations import list_container_files

class LocalStorageDirectory:
    
    def upload_file(self, local_directory, file_to_upload, container_client, container_folder = ""):
        name = container_folder + "/" + file_to_upload if container_folder != "" else file_to_upload

        file_path = os.path.join(local_directory, file_to_upload)
        
        already_uploaded = list_container_files(container_client)
        if file_to_upload not in already_uploaded:
            with open(file_path, 'rb') as data:
                container_client.upload_blob(name = name, data = data)
        else:
            print(f'Already uploaded {file_to_upload}!')

    def upload_dir(self, local_directory, container_client, container_folder):
        files_in_directory = os.listdir(local_directory)
        total_files = len(files_in_directory)
        
        i = 0
        for file_name in files_in_directory:
            file_path = os.path.join(local_directory, file_name)
            
            with open(file_path, 'rb') as data:
                container_client.upload_blob(name = container_folder + "/" + file_name, data = data)
            
            i += 1   
            print(f'Uploaded {file_name} - {i}/{total_files}')
            
    
    def upload_dir_unique(self, local_directory, container_client, container_folder):
        '''upload files while checking if file exists in datalake'''
        files_in_directory = os.listdir(local_directory)
        total_files = len(files_in_directory)
        i = 0
        already_uploaded = list_container_files(container_client)
        for file_name in os.listdir(local_directory):
            file_path = os.path.join(local_directory, file_name)
            
            i += 1   
            if file_name not in already_uploaded:
                with open(file_path, 'rb') as data:
                    container_client.upload_blob(name = container_folder + "/" + file_name, data = data)
                print(f'Uploaded {file_name} - {i}/{total_files}')
            else:
                print(f'Already uploaded {file_name} - {i}/{total_files}')

    def download_file(self, local_directory, container_client, file_name):
        file_path = os.path.join(local_directory,file_name)
        blob_client = container_client.get_blob_client(file_name)   

        with open(file = file_path, mode="wb") as sample_blob:
            download_stream = blob_client.download_blob()
            sample_blob.write(download_stream.readall())

        print(f"Downloaded {file_path.split('/')[-1]}")
    
    def download_annotations(self, local_directory, container_client, file_name):
        file_name = file_name + ".zip"
        self.download_file(local_directory, container_client, file_name)
        
        zip_file = os.path.join(local_directory, file_name)
        default_annotations_file = os.path.join(local_directory, 'annotations.xml')
        new_annotations_filename = os.path.join(local_directory, file_name.replace(".zip",".xml"))

        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(local_directory)

        os.rename(default_annotations_file, new_annotations_filename)
        os.remove(zip_file)
        
    def download_dir(self, local_directory, container_client, datalake_directory):
        datalake_directory = datalake_directory if datalake_directory.endswith("/") else datalake_directory + "/"
        for blob_list in container_client.list_blobs(name_starts_with = datalake_directory):
            blob_file = container_client.get_blob_client(blob_list.name)

            file_name = blob_list.name.split('/')[-1]
            file_path = os.path.join(local_directory,file_name)
            
            with open(file = file_path, mode="wb") as sample_blob:
                download_stream = blob_file.download_blob()
                sample_blob.write(download_stream.readall())
                print(f'Downloaded {file_name} from {datalake_directory}.')
            