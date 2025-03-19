class Email:
    def __init__(self, client):
        self.client = client

    def send(self, data):
        """Send your email"""
        return self.client.request("POST", "/email/send", data)