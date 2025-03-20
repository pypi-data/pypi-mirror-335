import json
import urllib.parse

from .resources import ResourcesEndpoint

class ColumnsEndpoint:
    """
    Handles column-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Columns API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_column(
        self,
        native_type: str,
        title: str,
        description: str,
        entity_type='glossary',
        integration=None,
        definition='',
        parent=None,
        pii=False,
        verified=False,
        published=True,
        teams=[],
        owners=[],
        owners_groups=[],
        collections=[],
        tags=[],
        subscribers=[]
    ):
        """
        Creates a new column in the workspace.
        
        :param native_type: str
            The native type of the column as it's referred to in the integration.
        :param title: str
            The title of the column.
        :param integration: str
            The integration ID associated with the column, if applicable.
        :param description: str
            A brief description of the column.
        :param entity_type: str
            The type of the column entity.
        :param definition: str
            Markdown documentation associated with the column.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the column contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the column has been marked as verified.
        :param published: bool
            Determines if the column is visible to viewers.
        :param teams: list
            A list of team IDs associated with the column.
        :param owners: list
            A list of user IDs who own the column.
        :param owners_groups: list
            A list of group IDs who own the column.
        :param collections: list
            A list of collection IDs the column belongs to.
        :param tags: list
            A list of tag IDs associated with the column.
        :param subscribers: list
            A list of user IDs subscribed to the column for notifications.
        :return: API response from the server.
        """
        data = {
            "native_type": native_type,
            "title": title,
            "integration": integration,
            "description": description,
            "entity_type": entity_type,
            "definition": definition,
            "parent": parent,
            "pii": pii,
            "verified": verified,
            "published": published,
            "teams": teams,
            "owners": owners,
            "owners_groups": owners_groups,
            "collections": collections,
            "tags": tags,
            "subscribers": subscribers,
        }
        return self.client.post("/table/column/", data=data)

    def get_columns(self):
        """
        Fetches the columns.

        :return: API response containing the columns.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"column"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_column_by_id(self, column_id: str):
        """
        Fetches the column.

        :return: API response containing the column.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{column_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_column(self, column_id: str, **kwargs):
        """
        Updates a column using a PATCH request.

        :param column_id: str
            The unique identifier of the column to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, native_type).
        :return: API response from the server.
        """
        return self.client.patch(f"/table/column/{column_id}", data=kwargs)

    def delete_column(self, column_id: str):
        """
        Deletes a column by its ID.

        :param column_id: str
            The unique identifier of the column to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/table/column/{column_id}")
