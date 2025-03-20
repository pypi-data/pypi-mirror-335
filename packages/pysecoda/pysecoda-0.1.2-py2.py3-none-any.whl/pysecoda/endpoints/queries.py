import json
import urllib.parse

from .resources import ResourcesEndpoint

class QueriesEndpoint:
    """
    Handles question-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Question API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def get_queries(self):
        """
        Fetches the list of all queries in the workspace.

        :return: API response containing the queries.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"query"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_query_by_id(self, query_id: str):
        """
        Fetches a specific query by its ID.

        :param query_id: str
            The unique identifier of the query to retrieve.
        :return: API response containing the query details.
        """
        return self.client.get(f"/query/queries/{query_id}")
