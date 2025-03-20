import os


class Config:
    def __init__(self):
        self.hub_token = os.getenv("HF_TOKEN")
        self.push_to_hub = True
        self.hub_private_repo = True
        