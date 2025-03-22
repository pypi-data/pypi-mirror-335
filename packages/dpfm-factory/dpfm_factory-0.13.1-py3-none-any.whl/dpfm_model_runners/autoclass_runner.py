from transformers import AutoImageProcessor, AutoModel
import torch
from dotenv import load_dotenv
from huggingface_hub import login
import os
import logging

logger = logging.getLogger()

#Load environment variables from .env file
load_dotenv()

# Access the HUGGINGFACE_TOKEN
huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

# Log in to Hugging Face using the token
if huggingface_token:
    login(huggingface_token)
    logger.info("Successfully authenticated with Hugging Face.")
else:
    logger.warning("HUGGINGFACE_TOKEN not found. Please check your .env file.")



class AutoclassLoader:
    def __init__(self, model_name, use_fast=True,  trust_remote_code=True):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoImageProcessor.from_pretrained(model_name, use_fast=use_fast,  trust_remote_code=trust_remote_code)
        self.model = AutoModel.from_pretrained(model_name,  trust_remote_code=trust_remote_code).to(self.device)

    def get_processor_and_model(self):
        return self.processor, self.model

    def get_image_embedding(self, image, processor, model, device):
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            embeddings = model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings.cpu().numpy().flatten()