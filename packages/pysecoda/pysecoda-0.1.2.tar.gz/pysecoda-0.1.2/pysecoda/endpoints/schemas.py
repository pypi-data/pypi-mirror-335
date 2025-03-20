import json
import urllib.parse

from .resources import ResourcesEndpoint

class SchemasEndpoint:
    """
    Handles schema-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Schemas API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_schema(
        self,
        native_type: str,
        database: str,
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
        Creates a new schema in the workspace.
        
        :param native_type: str
            The native type of the schema as referenced in the integration.
        :param database: str
            The name of the database that contains the schema.
        :param title: str
            The title of the schema.
        :param integration: str
            The integration ID associated with the schema, if applicable.
        :param description: str
            A brief description of the schema.
        :param entity_type: str
            The type of the schema entity.
        :param definition: str
            Markdown documentation associated with the schema.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the schema contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the schema has been marked as verified.
        :param published: bool
            Determines if the schema is visible to viewers.
        :param teams: list
            A list of team IDs associated with the schema.
        :param owners: list
            A list of user IDs who own the schema.
        :param owners_groups: list
            A list of group IDs who own the schema.
        :param collections: list
            A list of collection IDs the schema belongs to.
        :param tags: list
            A list of tag IDs associated with the schema.
        :param subscribers: list
            A list of user IDs subscribed to the schema for notifications.
        :return: API response from the server.
        """
        data = {
            "native_type": native_type,
            "database": database,
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
        return self.client.post("/database/schemas/", data=data)

    def get_schemas(self):
        """
        Fetches the schemas.

        :return: API response containing the schemas.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"schema"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_schema_by_id(self, schema_id: str):
        """
        Fetches the schema.

        :return: API response containing the schema.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{schema_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_schema(self, schema_id: str, **kwargs):
        """
        Updates a schema using a PATCH request.

        :param schema_id: str
            The unique identifier of the tag to update.
        :param kwargs: dict
            The fields to update (e.g., teams, definition).
        :return: API response from the server.
        """
        return self.client.patch(f"/tag/{schema_id}", data=kwargs)
