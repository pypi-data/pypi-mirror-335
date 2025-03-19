from .client import YonomaClient
from .contacts import Contacts
from .lists import Lists
from .tags import Tags
from .email import Email

class Yonoma:
    def __init__(self, api_key):
        self.client = YonomaClient(api_key)
        self.contacts = Contacts(self.client)
        self.lists = Lists(self.client)
        self.tags = Tags(self.client)
        self.email = Email(self.client)
