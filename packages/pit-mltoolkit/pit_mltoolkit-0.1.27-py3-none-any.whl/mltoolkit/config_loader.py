from google.cloud import storage
from google.oauth2 import service_account
from yaml import safe_load, YAMLError
from json import load, JSONDecodeError


class ConfigLoader():

    '''
    ----------------------------------------------------------------
    Description:
        - The following class can be used for all functions relevant
          to the handling of config files, it supports yaml, yml and 
          json file types 
        
    ----------------------------------------------------------------
    author: Tyron Lambrechts                Last Updated: 2025/02/11
    ----------------------------------------------------------------
    '''

    def __init__(self):
        self.client = storage.Client()
    
    def load_from_bucket(self, bucket_name: str, file_name: str):

        '''
        -----------------------------------------------------------------
        Description:
            - The following function is used to load a config file from
              a GCP bucket and load it

        bucket_name (str) - the name of the bucket where the config file 
                            is situated at

        file_name (str) - the name of the config file, that is stored in 
                          the bucket
        -----------------------------------------------------------------
        author: Tyron Lambrechts                 Last Updated: 2025/02/11
        -----------------------------------------------------------------
        '''

        # Acquiring file from GCP bucket
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        file = blob.download_as_text()

        # Loading the file and returning it

        if '.yaml' or '.yml' in file_name:
            config = safe_load(file)

        elif '.json' in file_name:
            config = load(file)
        
        return config
    
    def load_from_artifact(self, config_path: str):
        """
        -----------------------------------------------------------------
        Description:
            - Loads a config file from a Kubeflow Artifact.

        Parameters:
            config_path (str): Path to the config file, provided as 
                            Input[Artifact].path.

        Returns:
            dict: Parsed configuration file.

        Raises:
            ValueError: If the file format is unsupported.
            RuntimeError: If an error occurs while reading the file.
                                
        -----------------------------------------------------------------
        author: Thomas Verryne                Last Updated: 2025/02/13
        -----------------------------------------------------------------
        """
        try:
            with open(config_path, 'r') as file:
                content = file.read()

            # Try YAML first
            try:
                return safe_load(content)
            except YAMLError:
                pass  # If YAML fails, try JSON

            # Try JSON
            try:
                return load(content)
            except JSONDecodeError:
                raise ValueError(f"Unsupported or invalid file format: {config_path}")

        except FileNotFoundError:
            raise RuntimeError(f"Config file not found: {config_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {config_path}: {str(e)}")