from google.oauth2 import service_account
from google.cloud import artifactregistry_v1
from kfp.registry import RegistryClient

class ArtifactHelper():
    '''
    ---------------------------------------------------------
    Description:
        - The following class can be use as an aid to interact
          with the artifact registry in the google cloud
          platform (GCP).


    ----------------------------------------------------------
    author: Thomas Verryne                Last Updated: 2025/02/14
    ----------------------------------------------------------
    '''

    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location


    def check_repository(self, repository_id: str):
        '''
        -------------------------------------------------------
        Description:
            - This function checks if the exisits

        Parameters:
            repository_id (str): The name of the repository.
           
        Return:
            True if the requested repository is found, otherwise false.
        -------------------------------------------------------
        author: Thomas Verryne            Last Updated: 2025/02/14
        -------------------------------------------------------
        '''
        client = artifactregistry_v1.ArtifactRegistryClient()

        parent = f'projects/{self.project_id}/locations/{self.location}'

        repos = client.list_repositories(parent=parent)

        for repo in repos:
            if repository_id in repo.name:
                return True
        return False


    def create_repository(self, repository_id: str, repository_format = 'docker'):
        '''
        -------------------------------------------------------
        Description:
            - This function creates a new repository in this project.

        Parameters:
            repository_id (str): The name of the repository.
            repository_format (str): THe format of the repository. repository_format for docker image
                                     repository is 'docker'. repository_format for kubeflow pipeline
                                     is 'kfp'.

        Additional information:
            Repository IDs must:
                - Be lowercase
                - Start with a letter
                - Contain only letters (a-z), numbers (0-9), and hyphens (-)
                - Be at most 63 characters long
        -------------------------------------------------------
        author: Thomas Verryne            Last Updated: 2025/02/14
        -------------------------------------------------------
        '''
        # Check if the repository already exists

        if self.check_repository(repository_id):
            print(f"Repository '{repository_id}' already exists.")
            return

        client = artifactregistry_v1.ArtifactRegistryClient()

        parent = f'projects/{self.project_id}/locations/{self.location}'

        if repository_format == 'docker':
            format = artifactregistry_v1.Repository.Format.DOCKER
        elif repository_format == 'kfp':
            format = artifactregistry_v1.Repository.Format.KFP
        else:
            raise ValueError(f"Invalid repository format: {repository_format}. Expected 'docker' or 'kfp'.")

        repository = artifactregistry_v1.Repository(
            name = f'{parent}/repositories/{repository_id}',
            format_ = format
        )

        operations = client.create_repository(parent=parent, repository_id=repository_id, repository=repository)

        response = operations.result()
        print(f'Repository created: {response.name}')

   
    
    def list_repositories(self):
        '''
        -------------------------------------------------------
        Description:
            - This function returns a list of all the
                      exisiting repositories in the project.
           
        Return:
            List with the names of the exisiting repositories.
        -------------------------------------------------------
        author: Thomas Verryne            Last Updated: 2025/02/17
        -------------------------------------------------------
        '''
                
        client = artifactregistry_v1.ArtifactRegistryClient()

        parent = f'projects/{self.project_id}/locations/{self.location}'

        repos = client.list_repositories(parent=parent)

        repositories = []

        for repo in repos:
            repositories.add(repo.name)

        return repositories
    
    def upload_file_to_repository(self, repository_id: str, file_path:str, description: str = None, tags: list = None):
        '''
        -------------------------------------------------------
        Description:
            - This function uploads a file by using its file path
              to the specified repository.

        Parameters:
            repository_id (str): The name of the repository that the
                                 file will be send to.
            file_path (str): Path to the file.

           
        Return:
            
        -------------------------------------------------------
        author: Thomas Verryne            Last Updated: 2025/02/17
        -------------------------------------------------------
        '''

        if tags == None:
            tags = []

        host = f"https://{self.location}-kfp.pkg.dev/{self.project_id}/{repository_id}"
        client = RegistryClient(host=host,
                                # auth=self.credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
                                )
        # Note scopes for credentials

        try:
            template_name, version_name = client.upload_pipeline(
                file_name=file_path,
                extra_headers={"description": description},
                tags = tags
            )
            print(f"Successfully uploaded file as '{template_name}', version '{version_name}'.")

        except Exception as e:
            print(f"Error uploading pipeline: {e}")

    


    
