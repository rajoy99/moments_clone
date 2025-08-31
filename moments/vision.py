import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
from dotenv import load_dotenv
load_dotenv()


# Load credentials from environment variables
endpoint = os.getenv("AZURE_COMPUTERVISION_ENDPOINT")
key = os.getenv("AZURE_COMPUTERVISION_KEY")

if not endpoint or not key:
    raise ValueError("Please set the environment variables")

# Authenticate client
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(endpoint=endpoint, credentials=credentials)

def generate_image_metadata(source_path):
    """
    Analyze an image (from URL or file) and extract a caption and tags.

    Parameters
    ----------
    source_path : str
        Path to a local image file OR a URL pointing to an image.

    Returns
    -------
    tuple
        A tuple (caption, tags)

    """
    try:
        # Check if the input is a URL
        if source_path.startswith("http://") or source_path.startswith("https://"):
            # Use API client methods for URL input
            desc_output = client.describe_image(
                source_path,
                max_descriptions=1,
                language="en"
            )
            tag_output = client.tag_image(source_path)
        else:
            # Otherwise, open as a local file in binary mode
            with open(source_path, "rb") as file_obj:
                desc_output = client.describe_image_in_stream(
                    file_obj,
                    max_descriptions=1,
                    language="en"
                )
                file_obj.seek(0)  
                tag_output = client.tag_image_in_stream(file_obj)

        # Extract caption
        image_caption = "Invalid"
        if desc_output.captions:
            image_caption = desc_output.captions[0].text

        # Extract tags from response
        image_tags = [item.name for item in tag_output.tags]

        return image_caption, image_tags

    except Exception as err:
        
        return f"Failed to extract image info: {str(err)}", []