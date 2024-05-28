from dotenv import load_dotenv
from os import path, environ


base_dir = path.dirname(path.dirname(path.abspath(__file__)))
load_dotenv(path.join(base_dir, ".env"))

class Config:

    """ Call Environment """

    BASE_DIR = base_dir

    def get_secret_key():
        return environ.get("SECRET_KEY")


    
    

