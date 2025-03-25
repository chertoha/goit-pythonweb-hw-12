"""
Module for handling file uploads to Cloudinary.

This module contains services related to uploading files to Cloudinary, a cloud
storage platform. The provided functionality allows uploading user files (such as
profile images) and generates URLs to access the uploaded files.

Classes:
    - UploadFileService: Handles the file upload process to Cloudinary.

Methods:
    - upload_file: Uploads a file to Cloudinary and generates a URL for the uploaded file.
"""

import cloudinary
import cloudinary.uploader

class UploadFileService:
    """
        Service for uploading files to Cloudinary.

        This service allows files to be uploaded to Cloudinary, storing them under a
        unique public ID. The file URL is then generated with resizing options.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
                Initializes the UploadFileService with Cloudinary configuration.

                Args:
                    cloud_name (str): Cloudinary cloud name.
                    api_key (str): Cloudinary API key.
                    api_secret (str): Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
                Uploads a file to Cloudinary and returns the generated URL.

                The file is uploaded under a unique public ID, which includes the username
                to ensure uniqueness. After uploading, the function generates and returns
                a URL for the uploaded file.

                Args:
                    file: The file to be uploaded.
                    username (str): The username to be included in the file's public ID.

                Returns:
                    str: The generated URL for the uploaded file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
