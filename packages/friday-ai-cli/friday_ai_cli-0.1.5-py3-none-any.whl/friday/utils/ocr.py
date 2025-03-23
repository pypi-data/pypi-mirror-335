from google.oauth2 import service_account
from google.cloud import vision

credentials_path: str = (
    "/home/dockeruser/friday-echo/neuralwave-portal-c73819b1ca4e.json"
)

credentials = service_account.Credentials.from_service_account_file(credentials_path)
cloud_vision_client = vision.ImageAnnotatorClient(credentials=credentials)


def detect_text_vision_cloud(path, path_is_base_64=False):
    try:
        """Detects text in the file."""
        if path_is_base_64:
            content = path
        else:
            with open(path, "rb") as image_file:
                content = image_file.read()

        image = vision.Image(content=content)

        response = cloud_vision_client.text_detection(image=image)
        texts = response.text_annotations
        print("Texts:")

        whole_image_text = texts[0].description
        return whole_image_text.strip()
    except Exception as e:
        print(
            "FAILED TO EXTRACT TEXT FROM THE IMAGE USING GOOGLE CLOUD VISION, Error: "
            + str(e)
        )
        return None
