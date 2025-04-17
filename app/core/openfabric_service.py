import logging
import base64
import os
import requests
from typing import Dict, Any, Optional, Tuple
from core.stub import Stub  # Ensure Stub is imported
from core.remote import Remote

class OpenfabricService:
    """
    Service to handle Openfabric API integrations for text-to-image and image-to-3D conversions.
    """
    
    # App IDs for the Openfabric services
    # TEXT_TO_IMAGE_APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
    # IMAGE_TO_3D_APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"

    TEXT_TO_IMAGE_APP_ID = "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network"
    IMAGE_TO_3D_APP_ID = "f0b5f319156c4819b9827000b17e511a.node3.openfabric.network"
    
    def __init__(self, stub: Stub):
        """
        Initialize the Openfabric service.
        
        Args:
            stub: The Openfabric Stub instance for API calls
        """
        self.stub = stub
        self.images_dir = "datastore/images"
        self.models_dir = "datastore/models"
        
        # Create directories if they don't exist
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    def text_to_image(self, prompt: str, user_id: str = "super-user") -> Optional[str]:
        """
        Convert text prompt to image using Openfabric.
        
        Args:
            prompt (str): The enhanced text prompt
            user_id (str): User identifier for the API call
            
        Returns:
            Optional[str]: Path to the saved image file or None if failed
        """
        try:

            remote = Remote("wss://c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network").connect()
            image_response = remote.execute(
                    inputs={
                    "prompt": prompt,
                    "negative_prompt": "poor quality, blurry, low resolution",
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                },
                    uid="super-user"
                )
            
            
            
            # Make the API call
            logging.info(f"Sending text-to-image request with prompt: {prompt}")
            
            print(image_response)

            result = remote.get_response(image_response)
            if not result or "result" not in result:
                logging.error("Failed to get valid response from text-to-image API")
                return None
            
            # Save the image to disk
            image_data = result["result"]  # Assuming the API returns base64 encoded image
            image_path = self._save_base64_image(image_data, "text2img")
            
            return image_data
            
        except Exception as e:
            logging.error(f"Error in text-to-image conversion: {e}")
            return None
    
    def image_to_3d(self, image_path: str, user_id: str = "super-user") -> Optional[str]:
        """
        Convert image to 3D model using Openfabric.
        
        Args:
            image_path (str): Path to the input image
            user_id (str): User identifier for the API call
            
        Returns:
            Optional[str]: Path to the saved 3D model file or None if failed
        """
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                logging.error(f"Image file not found: {image_path}")
                return None
            
            # Get input schema for image-to-3D app
            input_schema = self.stub.schema(self.IMAGE_TO_3D_APP_ID, 'input')
            
            # Read image and convert to base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            remote = Remote("wss://f0b5f319156c4819b9827000b17e511a.node3.openfabric.network").connect()
            image_response = remote.execute(
                    inputs={
                    "image": image_data
                },
                    uid="super-user"
                )
                
            logging.info(f"Sending image-to-3D request for image: {image_path}")

            print(image_response)

            result = remote.get_response(image_response)
            if not result or "result" not in result:
                logging.error("Failed to get valid response from image-to-3D API")
                return None
            
            # Save the image to disk
            image_data = result["result"]  # Assuming the API returns base64 encoded image
            
            
            # Save the 3D model to disk
            model_data = result["result"]  # Assuming the API returns base64 encoded 3D model
            model_path = self._save_base64_file(model_data, "model", extension=".glb")
            
            return model_path
            
        except Exception as e:
            logging.error(f"Error in image-to-3D conversion: {e}")
            return None
    
    def _save_base64_image(self, base64_data: str, prefix: str = "image") -> str:
        """
        Save base64 encoded image data to a file.
        
        Args:
            base64_data (str): Base64 encoded image data
            prefix (str): Prefix for the filename
            
        Returns:
            str: Path to the saved image file
        """
        try:
            # Determine the image format (usually jpeg or png)
            if "data:image/" in base64_data:
                # Remove data URL prefix if present
                header, data = base64_data.split(",", 1)
                image_format = header.split(";")[0].split("/")[1]
                base64_data = data
            else:
                # Default to png if format not specified
                image_format = "png"
            
            # Decode base64 data
            image_bytes = base64.b64decode(base64_data)
            
            # Generate filename with timestamp
            timestamp = int(os.path.getmtime(self.images_dir)) if os.path.exists(self.images_dir) else 0
            filename = f"{prefix}_{timestamp}.{image_format}"
            filepath = os.path.join(self.images_dir, filename)
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            logging.info(f"Saved image to {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving base64 image: {e}")
            return ""
    
    def _save_base64_file(self, base64_data: str, prefix: str = "file", extension: str = ".bin") -> str:
        """
        Save base64 encoded data to a file.
        
        Args:
            base64_data (str): Base64 encoded data
            prefix (str): Prefix for the filename
            extension (str): File extension
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Remove data URL prefix if present
            if ";base64," in base64_data:
                base64_data = base64_data.split(";base64,")[1]
            
            # Decode base64 data
            file_bytes = base64.b64decode(base64_data)
            
            # Generate filename with timestamp
            timestamp = int(os.path.getmtime(self.models_dir)) if os.path.exists(self.models_dir) else 0
            filename = f"{prefix}_{timestamp}{extension}"
            filepath = os.path.join(self.models_dir, filename)
            
            # Save to file
            with open(filepath, "wb") as f:
                f.write(file_bytes)
            
            logging.info(f"Saved file to {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Error saving base64 file: {e}")
            return "" 