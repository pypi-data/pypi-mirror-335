def list_container_files(container_client):
    ''' List all files in container: excluding relative path! 
    Returns list of filenames
    
    Args:
        container_client: azure container client
    '''
    directory_blob_files = container_client.list_blobs()
    filename = [x.name.split('/')[-1]  for x in directory_blob_files]
    return filename

def list_container_full_file_names(container_client):
    ''' 
    List all files in container including folder.

    Args:
        container_client: azure container client

    Returns 
        list of folder/filenames
    '''
    directory_blob_files = container_client.list_blobs()
    full_filename = [x.name for x in directory_blob_files]
    return full_filename