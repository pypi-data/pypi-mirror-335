class LineageEndpoint:
    """
    Handles lineage-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Lineage API.
        """
        self.client = client

    def create_lineage(self, from_entity: str, to_entity: str, direction: str):
        """
        Creates a new lineage record.
        """
        data = {
            "from_entity": from_entity,
            "to_entity": to_entity,
            "direction": direction
        }
        return self.client.post("/lineage/manual/", data=data)

    def get_lineage(self):
        """
        Fetches the list of all lineage records in the workspace.
        """
        all_results = []
        endpoint = "/lineage/manual/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']
        return all_results

    def get_lineage_by_id(self, lineage_id: str):
        """
        Fetches a specific lineage record by its ID.
        """
        return self.client.get(f"/lineage/manual/{lineage_id}")

    def delete_lineage(self, lineage_id: str):
        """
        Deletes a lineage record by its ID.
        """
        return self.client.delete(f"/lineage/manual/{lineage_id}")
