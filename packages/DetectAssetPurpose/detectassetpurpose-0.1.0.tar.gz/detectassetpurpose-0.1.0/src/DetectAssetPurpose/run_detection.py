from DetectAssetPurpose import detect_image
from DetectAssetPurpose import detect_video
from pathlib import Path
from google.cloud import storage
import dotenv
dotenv.load_dotenv()


def get_blob(gs_path):
    client = storage.Client()
    bucket_name = gs_path.split("/")[2]
    file_name =  "/".join(gs_path.split("/")[3:])
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob
    
    
def get_purpose_image(gs_path: str):
    """
    Reads an image file from Google Cloud Storage using gsutil.
    Args:
        gs_path: GCS URI of the video file (e.g., gs://bucket-name/image.png or jpg).
    Returns:
        The detected purpose of the image ad.
    """
    blob = get_blob(gs_path)
    img_bytes = blob.download_as_bytes()
    result = detect_image.detect_image_objectives(img_bytes)
    purpose = result['purpose'].value if hasattr(result['purpose'], 'value') else result['purpose']
    return purpose


def get_purpose_video(gs_path: str):
    """
    Reads a video file from Google Cloud Storage and detects its purpose.
    Args:
        gs_path: GCS URI of the video file (e.g., gs://bucket-name/video.mp4).
    Returns:
        The detected purpose of the video ad.
    """
    # Pass the URI directly to detect_video_objectives
    result = detect_video.detect_video_objectives(video_uri=gs_path)
    purpose = result['purpose'].value if hasattr(result['purpose'], 'value') else result['purpose']
    return purpose

