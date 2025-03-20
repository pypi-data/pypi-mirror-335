import json
import urllib.parse

from .resources import ResourcesEndpoint

class TablesEndpoint:
    """
    Handles table-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Table API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_table(
        self,
        native_type: str,
        database: str,
        schema: str,
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
        Creates a new table in the workspace.
        
        :param native_type: str
            The native type of the table.
        :param database: str
            The name of the database the table belongs to.
        :param schema: str
            The name of the schema the table belongs to.
        :param title: str
            The title of the table.
        :param integration: str
            The integration ID associated with the table, if applicable.
        :param description: str
            A brief description of the table.
        :param entity_type: str
            The type of the table entity.
        :param definition: str
            Markdown documentation associated with the table.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the table contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the table has been marked as verified.
        :param published: bool
            Determines if the table is visible to viewers.
        :param teams: list
            A list of team IDs associated with the table.
        :param owners: list
            A list of user IDs who own the table.
        :param owners_groups: list
            A list of group IDs who own the table.
        :param collections: list
            A list of collection IDs the table belongs to.
        :param tags: list
            A list of tag IDs associated with the table.
        :param subscribers: list
            A list of user IDs subscribed to the table for notifications.
        :return: API response from the server.
        """
        data = {
            "native_type": native_type,
            "database": database,
            "schema": schema,
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
        return self.client.post("/table/tables/", data=data)

    def get_tables(self):
        """
        Fetches the list of all tables in the workspace.

        :return: API response containing the tables.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"table"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_table_by_id(self, table_id: str):
        """
        Fetches the table.

        :return: API response containing the table.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{table_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_table(self, table_id: str, **kwargs):
        """
        Updates a table using a PATCH request.

        :param table_id: str
            The unique identifier of the table to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, schema).
        :return: API response from the server.
        """
        return self.client.patch(f"/table/tables/{table_id}", data=kwargs)

    def delete_table(self, table_id: str):
        """
        Deletes a table by its ID.

        :param table_id: str
            The unique identifier of the table to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/table/tables/{table_id}")
