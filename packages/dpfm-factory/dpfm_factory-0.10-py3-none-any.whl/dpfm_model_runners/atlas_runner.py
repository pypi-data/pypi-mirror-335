import httpx
import json
import time
global apigee_auth
global last_auth_time
import numpy as np
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger()


atlas_base_url = 'https://staging.internal.mcc.api.mayo.edu/genai-digipath-atlas'
apigee_auth = None


#Load environment variables from .env file
load_dotenv()
APIGEE_CLIENT_KEY = os.getenv("APIGEE_CLIENT_KEY")
APIGEE_CLIENT_SECRET = os.getenv("APIGEE_CLIENT_SECRET")
if APIGEE_CLIENT_KEY is None:
    raise EnvironmentError("You must define APIGEE_CLIENT_KEY in your .env file!")
if APIGEE_CLIENT_SECRET is None:
    raise EnvironmentError("You must define APIGEE_CLIENT_SECRET in your .env file!")

def request_apigee_auth(
    apigee_key: str = "",
    apigee_secret: str = "",
    url: str = 'https://staging.internal.mcc.api.mayo.edu/oauth/token',
) -> dict:
    """
    Authenticates with Apigee using your 'key' and 'secret'.
    Returns a response which includes the necessary access token.
    """
    assert apigee_key != "" and apigee_secret != "", "apigee_key and apigee_secret required"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': apigee_key,
        'client_secret': apigee_secret
    }
    with httpx.Client() as client:
        response = client.post(url, headers=headers, data=data)
    json_response: dict = json.loads(response.text)
    assert "access_token" in json_response, f"failed to get access token: {response.text}"
    return json_response


def atlas_inference(
        apigee_access_token: str,
        data: bytes,
        input_img_size: int,
        target_img_size: int = 224,
        read_timeout_sec: int = 180):
    """
    Sends a request to the Atlas model HTTP API and returns the response object.
    The input image must be square. The API will resize your image if you specify a target_img_size
    that is different from the input_img_size.

    Args:
        apigee_access_token (str)
        data (bytes): The RGB bytes of an image, values in the range 0-255.
        input_img_size (int): The number of pixels of one dimension of the input image (which must be square).
        target_img_size (int): The desired number of pixels to resize the input image to, before being passed into the Atlas model.
        read_timeout_sec (int): Connection read timeout value
    """
    url = f'{atlas_base_url}?input_img_size={input_img_size}&target_img_size={target_img_size}'
    headers = {
        'Authorization': f'Bearer {apigee_access_token}',
        'Content-Type': 'application/octet-stream'
    }
    transport = httpx.HTTPTransport(retries=3)
    with httpx.Client(transport=transport) as client:
        response = client.post(url, headers=headers, content=data, timeout=read_timeout_sec)
    return response


def robust_atlas_inference(
        data: bytes,
        input_img_size: int,
        target_img_size: int = 224,
        read_timeout_sec: int = 180,
        max_retries: int = 3
) -> (str, int):
    """
    A wrapper that gracefully handles transient API failures and rate limits
    by retrying with backoff, and periodically refreshing Apigee access token
    to prevent auth errors.
    Returns the a tuple of the response text and HTTP status code.
    """
    # Apigee auth tokens expire after one hour,
    # so we refresh the auth token periodically in a threadsafe manner.
    global apigee_auth
    global last_auth_time

    if apigee_auth is None:  # request access token for first time
        last_auth_time = time.time()
        apigee_auth = request_apigee_auth(APIGEE_CLIENT_KEY, APIGEE_CLIENT_SECRET)
        assert 'access_token' in apigee_auth, "failed to obtain apigee access token"
    else:  # refresh access token
        current_time = time.time()
        elapsed_time = current_time - last_auth_time
        if elapsed_time > 60 * 15:
            apigee_auth = request_apigee_auth(APIGEE_CLIENT_KEY, APIGEE_CLIENT_SECRET)
            last_auth_time = time.time()
            assert 'access_token' in apigee_auth, "failed to refresh apigee access token"

    apigee_access_token = apigee_auth['access_token']

    retries = max_retries
    sleep = 2
    while retries > 0:
        try:
            response = atlas_inference(
                apigee_access_token, data, input_img_size, target_img_size, read_timeout_sec
            )
            if response.status_code != 200:
                raise Exception(response.text)
            return response.text, response.status_code
        except Exception as e:
            retries -= 1
            if retries == 0:
                print("Atlas HTTP API request failed (max retries exceeded):", e)
                return str(e), 500
            else:
                print("Atlas HTTP API error (retrying):", e)
                time.sleep(sleep)
                sleep = sleep * 2
                continue


class AtlasLoader:
    def __init__(self, model_name="mayo/ATLAS", image_size=224):
        self.image_size = image_size
        self.device = None

        # Initialize the model with proper layers and activation
        self.model = None

        # Setup the preprocessing transforms
        self.processor = None

    def get_processor_and_model(self):
        return self.processor, self.model


    # Function to get image embedding
    def get_image_embedding(self, image, processor=None, model=None, device=None):
        img = image.resize((self.image_size, self.image_size), resample=0)
        rgb_image = img.convert('RGB')
        atlas_response, status_code = robust_atlas_inference(rgb_image.tobytes(), input_img_size=self.image_size)

        if status_code != 200:
            logger.warning(f'Warning! received status code {status_code}')
        response_dict = json.loads(atlas_response)
        return np.squeeze(response_dict['cls_token'])



