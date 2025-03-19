class Lists:
    def __init__(self, client):
        self.client = client

    def list(self):
        """Retrieve all lists."""
        return self.client.request("GET", "/lists/list")

    def create(self, data):
        """Create a new list."""
        return self.client.request("POST", "/lists/create", data)

    def update(self, list_id, data):
        """Update an existing list."""
        return self.client.request("POST", f"/lists/{list_id}/update", data)

    def retrieve(self, list_id):
        """Retrieve a specific list."""
        return self.client.request("GET", f"/lists/{list_id}")

    def delete(self, list_id):
        """Delete a list."""
        return self.client.request("DELETE", f"/lists/{list_id}/delete")


