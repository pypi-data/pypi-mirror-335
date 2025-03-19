
import subprocess
from google.oauth2 import service_account
import platform

class DockerTool():
    """
    A class that handles all operations related to Docker

    ## Attributes:
    

    ## Methods:

    **build_image**: builds a docker image based on a specified dockerfile</br>

    **delete_image**: deletes a docker image</br>

    **run_image**: runs a specific docker image</br>

    **list_images**: lists all of the docker images currently in daemon</br>

    **show_storage**: shows the amount of storage used in the daemon</br>

    **remove_unused**: removes all unused images, containers etc. that will clear up storage</br>

    **upload_image**: upload image to google cloud artifact registry</br>

    ## Example Initialization:
    ```python

    docker = DockerTool()

    ```
    ## Authors:
    - Thomas Verryne
    - Tyron Lambrechts
    """

    def __init__(self):
        self.os = platform.system()

    def build_image(self, image_name: str, dockerfile: str):
        """
        A function that builds a docker image based on a specified dockerfile

        ## Parameters:
        **image_name** (`str`): the name you want to give the image you are about to build</br>
        **dockerfile** (`str`): the dockerfile that specifies how your image should be built

        ## Example Use:
        ```python

        docker = DockerTool()
        docker.build_image(image_name='my-image', dockerfile='Dockerfile')

        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts

        """
        image_tag = f"{image_name}:latest"
        
        if 'Linux' in self.os:
            docker_command = ["sudo", "docker", "build", "-t", image_tag, "-f", dockerfile, "."]
        else:
            docker_command = ["docker", "build", "-t", image_tag, "-f", dockerfile, "."]
        
        try:
            subprocess.run(docker_command, check=True)
            print(f"Successfully built {image_tag}")
        except Exception as e:
            print(f"Docker build error: {e}")
    
    def delete_image(self, image_id: str):
        """
        A function that deletes a specified image using either its ID or Name

        ## Parameters:
        **image_id** (`str`): The image's id can also be the name of the image that you want to delete

        ## Example Usage:
        ```python

        docker = DockerTool()
        docker.delete_image(image_id='3594ifa')

        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts
        """
        try:
            
            if 'Linux' in self.os:
                delete_command = ['sudo', 'docker', 'rmi', f'{image_id}']
            else:
                delete_command = ['docker', 'rmi', f'{image_id}']

            subprocess.run(delete_command, check=True)

        except Exception as e:
            print(e)

    def run_image(self, image_name: str):
        """
        A function that runs a specified image using the image's name

        ## Parameters:
        **image_name** (`str`): the name of the docker image you want to run

        ## Example Usage:
        ```python
        docker = DockerTool()
        docker.run_image(image_name='my-image')
        ```

        ## Authors:
        - Thomas Verryne 
        - Tyron Lambrechts
        
        """
        try:
            
            if 'Linux' in self.os:
                run_command = ['sudo', 'docker', 'run', f'{image_name}']
            else:
                run_command = ['docker', 'run', f'{image_name}']

            subprocess.run(run_command, check=True)

        except Exception as e:
            print(e)

    def list_images(self):
        """
        A function that lists all of the images in the docker daemon

        ## Example Usage:
        ```python 

        docker = DockerTool()
        docker.list_images()

        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts

        """
        try:

            if 'Linux' in self.os:
                list_command = ['sudo', 'docker', 'images']
            else:
                list_command = ['docker', 'images']

            subprocess.run(list_command, check=True)

        except Exception as e:
            print(e)

    def list_containers(self):
        """
        

        """
        try:
            
            if 'Linux' in self.os:
                containers_command = ['sudo', 'docker', 'ps', '-a']
            else:
                containers_command = ['docker', 'ps', '-a']

            subprocess.run(containers_command, check=True)

        except Exception as e:
            print(e)

    def show_storage(self):
        """
        A function that shows the amount of storage used in the Docker daemon

        ## Example Usage:
        ```python

        docker = DockerTool()
        docker.show_storage()

        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts
        """
        try:

            if 'Linux' in self.os:
                storage_command = ['sudo', 'docker', 'system', 'df']
            else:
                storage_command = ['docker', 'system', 'df']

            subprocess.run(storage_command)

        except Exception as e:
            print(e)

    def remove_unused(self):
        """
        A function that removes all of the unused containers, images etc. of the Docker Daemon freeing up space

        ## Example Usage:
        ```python

        docker = DockerTool()
        docker.remove_unused()

        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts
        """
        try:

            if 'Linux' in self.os:
                remove_unused_command = ['sudo', 'docker', 'system', 'prune']
            else:
                remove_unused_command = ['docker', 'system', 'prune']

            subprocess.run(remove_unused_command, check=True)

        except Exception as e:
            print(e)

    def upload_image(self, image_name: str, project_id :str, location: str, repository_id: str, tag: str = "latest"):
        """
        A function that tags and pushes a Docker image to Google Artifact Registry.

        ## Parameters:
        **image_name** (`str`): the name of the docker image you want to run
        **project_id** (`str`): the name of the google cloud project
        **loaction** (`str`): the location of the project
        **repository_id** (`str`): the name of the repository where the image will reside

        ## Example Usage:
        ```python

        docker = DockerTool()
        docker.upload_image(
                image_name="my-image",
                project_id="my-project",
                location="europe-west1",
                repository_id="my-repository"
                )
        ```
        ## Authors:
        - Thomas Verryne
        - Tyron Lambrechts
        """

        repository_url = f"{location}-docker.pkg.dev/{project_id}/{repository_id}"
        full_image_path = f"{repository_url}/{image_name}:{tag}"

        try:
            
            if 'Linux' in self.os:

                # Authenticate Docker with Google Artifact Registry
                subprocess.run(["sudo", "gcloud", "auth", "configure-docker", repository_url.split('/')[0]], check=True)

                # Tag the Docker image
                subprocess.run(["sudo", "docker", "tag", f"{image_name}:{tag}", full_image_path], check=True)

                # Push the image
                subprocess.run(["sudo", "docker", "push", full_image_path], check=True)

                print(f"Successfully pushed image: {full_image_path}")

            else:

                # Authenticate Docker with Google Artifact Registry
                subprocess.run(["gcloud", "auth", "configure-docker", repository_url.split('/')[0]], check=True)

                # Tag the Docker image
                subprocess.run(["docker", "tag", f"{image_name}:{tag}", full_image_path], check=True)

                # Push the image
                subprocess.run(["docker", "push", full_image_path], check=True)

                print(f"Successfully pushed image: {full_image_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error pushing image: {e}")
