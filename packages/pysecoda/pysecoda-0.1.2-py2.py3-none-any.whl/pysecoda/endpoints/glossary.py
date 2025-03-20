import json
import urllib.parse

from .resources import ResourcesEndpoint

class GlossaryEndpoint:
    """
    Handles glossary-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Glossary API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def get_glossary(self):
        """
        Fetches the glossary.

        :return: API response containing the glossary.
        """
        filter_dict = {"operator":"exact", "field":"entity_type", "value":"glossary"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)
