import json
import urllib.parse

from .resources import ResourcesEndpoint

class DatabasesEndpoint:
    """
    Handles database-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Database API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_database(
        self,
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
        Creates a new database in the workspace.
        
        :param title: str
            The title of the database.
        :param integration: str
            The integration ID associated with the database, if applicable.
        :param description: str
            A brief description of the database.
        :param entity_type: str
            The type of the database entity.
        :param definition: str
            Markdown documentation associated with the database.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the database contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the database has been marked as verified.
        :param published: bool
            Determines if the database is visible to viewers.
        :param teams: list
            A list of team IDs associated with the database.
        :param owners: list
            A list of user IDs who own the database.
        :param owners_groups: list
            A list of group IDs who own the database.
        :param collections: list
            A list of collection IDs the database belongs to.
        :param tags: list
            A list of tag IDs associated with the database.
        :param subscribers: list
            A list of user IDs subscribed to the database for notifications.
        :return: API response from the server.
        """
        data = {
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
        return self.client.post("/database/databases/", data=data)

    def get_databases(self):
        """
        Fetches the databases.

        :return: API response containing the databases.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"database"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_database_by_id(self, database_id: str):
        """
        Fetches the database.

        :return: API response containing the database.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{database_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_database(self, database_id: str, **kwargs):
        """
        Updates a database using a PATCH request.
        
        :param database_id: str
            The unique identifier of the database to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, definition).
        :return: API response from the server.
        """
        return self.client.patch(f"/database/databases/{database_id}", data=kwargs)

    def delete_database(self, database_id: str):
        """
        Deletes a database by its ID.
        
        :param database_id: str
            The unique identifier of the database to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/database/databases/{database_id}")
