import cloudinary
import cloudinary.api
import cloudinary.uploader
from app.main.core.config import Config
import requests
from tempfile import NamedTemporaryFile
from fastapi import UploadFile, HTTPException



# Configure Cloudinary
coudinary_config = cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET,
    secure=Config.CLOUDINARY_API_SECURE
)





def download_and_save_file(file_secure_url: str) -> UploadFile:
    # Télécharger le fichier
    try:
        response = requests.get(file_secure_url)
        print("Downloading-file",response)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download file")
        
        # Créer un fichier temporaire pour simuler UploadFile
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(response.content)
        temp_file.seek(0)

        # Définir le nom du fichier à partir de l'URL
        filename = file_secure_url.split("/")[-1]

        # Créer un objet UploadFile simulé
        upload_file = UploadFile(filename=filename, file=temp_file)
        print("Uploading-file", upload_file)
        return upload_file
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download and save file: {e}")


def upload_to_cloudinary(file_path: str, public_id: str):
    """Upload the file to Cloudinary and return the response."""
    return cloudinary.uploader.upload(file_path, public_id=public_id, resource_type="auto")

def get_file_url(public_id: str) -> str:
    """Generate a secure URL for the file in Cloudinary."""
    url, _ = cloudinary.utils.cloudinary_url(public_id)
    return url

def get_access_control(public_id: str):
    try:
        resource = cloudinary.api.resource(public_id)
        print('RESOURCES1: %s' % resource)
        access_control = resource.get('resource', {}).get('access_control', {})
        return access_control
    except Exception as e:
        print("Error retrieving access control:", e)
        raise e

def update_access_control(public_id: str, access_control: dict):
    try:
        response = cloudinary.api.update(public_id = public_id,access_control=access_control)
        print("Access control updated:", response)
    except Exception as e:
        print("Error updating access control:", e)
        raise e

# cloudinary.utils.cloudinary_api_download_url()