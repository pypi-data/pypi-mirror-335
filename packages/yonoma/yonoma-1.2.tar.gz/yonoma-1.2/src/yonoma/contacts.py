class Contacts:
    def __init__(self, client):
        self.client = client

    def create(self, list_id, data):
        """Create a new contact."""
        return self.client.request("POST", f"/contacts/{list_id}/create", data)

    def unsubscribe(self, list_id, contact_id, data):
        """Unsubscribe a contact."""
        return self.client.request("POST", f"/contacts/{list_id}/status/{contact_id}", data)

    def addtag(self, contact_id, data):
        """Label a contact with a tag."""
        return self.client.request("POST", f"/contacts/tags/{contact_id}/add", data)

    def removetag(self, contact_id, data):
        """Remove a tag from a contact."""
        return self.client.request("POST", f"/contacts/tags/{contact_id}/remove", data)
