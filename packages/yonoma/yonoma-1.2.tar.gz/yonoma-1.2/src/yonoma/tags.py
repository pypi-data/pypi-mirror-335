class Tags:
    def __init__(self, client):
        self.client = client

    def list(self):
        """Retrieve all tags."""
        return self.client.request("GET", "/tags/list")

    def create(self, data):
        """Create a new tag."""
        return self.client.request("POST", "/tags/create", data)

    def update(self, tag_id, data):
        """Update an existing tag."""
        return self.client.request("POST", f"/tags/{tag_id}/update", data)

    def retrieve(self, tag_id):
        """Retrieve a specific tag."""
        return self.client.request("GET", f"/tags/{tag_id}")

    def delete(self, tag_id):
        """Delete a tag."""
        return self.client.request("DELETE", f"/tags/{tag_id}/delete")
