import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EMPLOYEE_SERVICE = 'http://fcchc-itprocess.southcentralus.cloudapp.azure.com:5104'
