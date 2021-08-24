import os
from dotenv import load_dotenv

load_dotenv()
ENV = os.getenv("ENV")
DATABASE_URL = os.getenv("DATABASE_URL")
EMPLOYEE_SERVICE = 'http://9854-190-236-251-178.ngrok.io' if ENV == "development" else 'http://fcchc-itprocess.southcentralus.cloudapp.azure.com:5104'
