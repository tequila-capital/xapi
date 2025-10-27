import os

from dotenv import load_dotenv


class ExampleBase:
    def __init__(self):
        load_dotenv()
        self.server = os.getenv('SERVER')
        self.user = os.getenv('USER')
        self.domain = os.getenv('DOMAIN')
        self.password = os.getenv('PASSWORD')
        self.locale = os.getenv('LOCALE')
        self.account = os.getenv('ACCOUNT')
        self.route = os.getenv('ROUTE')
        self.port = os.getenv('PORT')

        self.pem_path = r'roots.pem'
