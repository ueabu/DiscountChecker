import os

from dotenv import load_dotenv
load_dotenv()

class Config(object):
    DATABASE_URL = os.getenv('DATABASE_URL')
    TWILO_ACCOUNT_SID = os.getenv('TWILO_ACCOUNT_SID')
    TWILO_AUTH_TOKEN = os.getenv('TWILO_AUTH_TOKEN')
    TWILO_FROM_NUMBER = os.getenv('TWILO_FROM_NUMBER')
    TWILO_TO_NUMBER = os.getenv('TWILO_TO_NUMBER')
    SERVICE_ACCOUNT = os.getenv('SERVICE_ACCOUNT')
    DEBUG = os.getenv("DEBUG") or False