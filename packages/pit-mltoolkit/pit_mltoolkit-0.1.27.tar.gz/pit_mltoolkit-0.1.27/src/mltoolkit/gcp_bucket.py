from google.cloud import storage
from google.oauth2 import service_account
from json import loads


class GCPBucket():

    """
    A class for handling various operations within **Google Cloud**.

    ## Attributes:
    - **project_id** (`str`): The unique identifier for your Google Cloud project.
    - **location** (`str`): The region where your project is located (e.g., `europe-west1`).
    - **bucket_name** (`str`): The name of the bucket you want to work in

    ## Methods:
    - **Buckets**(`bucket_name`): Handles all operations related to Google Cloud Storage buckets.

    ## Example Usage:

    ```python

    bucket_tool = gcpBuckets(project_id='my-project',
              location='europe-west1')

    ```
    
    ## Notes:
    - Replace `'my-project'` with your actual Google Cloud project ID.
    """

    def __init__(self, project_id: str, location: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.location = location
        self.client = storage.Client(project=self.project_id)

    def local_file_upload(self, file_path: str, destination_blob: str):

            """
            Uploads a local file to a specified Google Cloud Storage bucket.

            ## Parameters:
            - **file_path** (`str`): The local path to the file you want to upload.
            - **destination_blob** (`str`): The destination path (including the blob name) in the Google Cloud Storage bucket.

            ## Example Usage:
            ```python
            bucket = Buckets(gcp, 'my-bucket')
            bucket.local_file_upload('local_file.txt', 'uploads/destination_blob.txt')
            ```

            ## Notes:
            - Ensure the file at `file_path` exists before attempting to upload.
            - The `destination_blob` should include the file name and any folder structure in the bucket.
            - This function assumes that the `Buckets` class has already been initialized and the client is properly authenticated.
            - In case of failure, an exception is raised and the error message will be printed.
            """

            try:

                bucket = self.client.get_bucket(self.bucket_name)
                file_upload = bucket.blob(destination_blob).upload_from_filename(file_path)
                print(f'File Has Successfully Been Uploaded to Bucket: {self.bucket_name}')
                
            except Exception as e:

                print(e)
    
    def delete_file_from_bucket(self, blob_path: str):
        """
        Deletes a file or object from a specified Google Cloud Storage bucket.

        ## Parameters:
        - **blob_path** (`str`): The file path of the file or object to delete from the bucket.

        ## Example Usage:
        ```python
        gcp = GCP(project_id='my-project',
                    location='europe-west1')

        bucket_tool = Buckets('my-bucket')
        bucket_tool.delete_file_from_bucket('uploads/old_file.txt')
        ```

        ## Notes:
        - The `blob_path` should include the complete path of the file or object within the bucket.
        - If the specified file does not exist, an exception will be raised.
        - This operation is irreversible—once deleted, the file cannot be recovered.
        - Ensure proper permissions are set to delete files from the bucket.
        """
        try:

            bucket = self.client.get_bucket(self.bucket_name)
            delete_file_op = bucket.delete_blob(blob_path)
            print(f'File {blob_path} has been succesfully deleted')

        except Exception as e:
            print(e)

    def download_file_from_bucket(self, file_path: str, local_path: str):

        """
        A function that downloads a file from a Google Cloud Storage bucket to a local destination.

        ## Parameters:
        - **file_path** (`str`): The path (blob name) of the file within the bucket.
        - **local_path** (`str`): The local file path where the downloaded file will be saved.

        ## Example Usage:
        ```python
        # Downloads 'data/file.txt' from the bucket to a local file 'local_file.txt'
        storage_instance.download_file_from_bucket('data/file.txt', 'local_file.txt')
        ```

        ## Notes:
        - Ensure that the specified `file_path` exists in the bucket.
        - The provided `local_path` must be a valid, writable file path on your local system.
        - Appropriate permissions are required to access and download files from the bucket.
        """
        
        try:

            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(file_path)

            with open(local_path, "wb") as file_obj:  
                blob.download_to_file(file_obj)
                print(f'{file_path} was successfully downloaded from bucket {self.bucket_name}')

        except Exception as e:
            print(e)

    def create_folder_in_bucket(self, folder_path: str):
        """
        Creates a folder in a Google Cloud Storage bucket by simulating a directory.

        Google Cloud Storage does not have a true hierarchical filesystem.
        Instead, "folders" are represented by blob names that end with a slash.
        This method creates an empty blob with the specified folder path to simulate a folder.

        ## Parameters:
        - **folder_path** (`str`): The folder path to create in the bucket. 
        Typically, this should end with a slash (e.g., 'new_folder/' or 'folder/subfolder/').

        ## Example Usage:
        ```python

        gcp = GCP(project_id='my-project',
                    location='europe-west1')

        bucket_tool = gcp.Buckets('my-bucket')
        bucket.create_folder_in_bucket('new_folder/')
        ```

        ## Notes:
        - Ensure that the folder path ends with a slash to indicate a folder.
        - This operation creates an empty blob, effectively simulating a folder structure.
        - Verify that you have the necessary permissions to write to the bucket.
        """
        try:

            bucket = self.client.get_bucket(self.bucket_name)
            create_folder_op = bucket.blob(folder_path)
            create_folder_op.upload_from_string('')
            print(f'The folder {folder_path} has been successfully created')
        
        except Exception as e:
            print(e)

    def create_bucket(self, bucket_name: str):
        """
        A function that creates a new Google Cloud Storage bucket.

        ## Parameters:
        - **bucket_name** (`str`): The desired name for the new bucket. 
        Note that this name must be globally unique across all Google Cloud Storage buckets.

        ## Example Usage:
        ```python
        # Create a new bucket named 'my-unique-bucket'
        gcp = GCP(project_id='my-project',
                    location='europe-west1')

        bucket_tool = gcp.Buckets('my-bucket')
        bucket.create_bucket('my-unique-bucket')

        ```
        ## Notes:
        - The bucket creation uses the location and project details from the associated GCP configuration.
        - Ensure that you have the necessary permissions to create buckets in your Google Cloud project.
        - Bucket names must adhere to Google Cloud Storage naming guidelines.
        """
        try:
            create_bucket_op = self.client.create_bucket(bucket_name, location=self.location, project=self.project_id)
            print(f'{bucket_name} has been created on project {self.project_id} in location/region {self.location}')
            
        except Exception as e:
            print(e)

    def delete_bucket(self, bucket_name: str):
        """
        A function deletes a Google Cloud Storage bucket.

        ## Parameters:
        - **bucket_name** (`str`): The name of the bucket to be deleted. This bucket must exist and be accessible.

        ## Example Usage:
        ```python
        gcp = GCP(project_id='my-project',
                    location='europe-west1')

        bucket_tool = gcp.Buckets('my-bucket')
        bucket.delete_bucket('my-unique-bucket')
        ```

        ## Notes:
        - The deletion operation is irreversible.
        - The method uses a force delete option, which should remove the bucket and all its contents.
        - Ensure you have the necessary permissions to delete the bucket in your Google Cloud project.
        """
        try:

            bucket = self.client.get_bucket(bucket_name)
            delete_op = bucket.delete(force=True)
            print(f'{bucket_name} has been successfully deleted')

        except Exception as e:
            print(e)