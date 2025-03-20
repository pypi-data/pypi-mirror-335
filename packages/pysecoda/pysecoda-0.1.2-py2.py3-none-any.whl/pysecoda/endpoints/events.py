import json
import urllib.parse

from .resources import ResourcesEndpoint

class EventsEndpoint:
    """
    Handles event-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Events API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_event_category(self, title: str, integration=None, teams=[]):
        """
        Creates a new event category in the workspace.

        :param title: str
            The title of the event category.
        :param integration: str
            The integration ID associated with the event category, if applicable.
        :param teams: list
            A list of team IDs associated with the event category.
        :return: API response from the server.
        """
        data = {
            "title": title,
            "integration": integration,
            "teams": teams,
        }
        return self.client.post("/event/category", data=data)

    def get_event_categories(self):
        """
        Fetches the list of all event categories in the workspace.

        :return: API response containing the event categories.
        """
        all_results = []
        endpoint = "/event/category/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_event_category_by_id(self, event_category_id: str):
        """
        Fetches a specific event category by its ID.

        :param event_category_id: str
            The unique identifier of the event category to retrieve.
        :return: API response containing the event category details.
        """
        return self.client.get(f"/event/category/{event_category_id}")

    def create_event(
        self,
        title: str,
        description: str,
        entity_type: str,
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
        Creates a new event in the workspace.

        :param title: str
            The title of the event.
        :param integration: str
            The integration ID associated with the event, if applicable.
        :param description: str
            A brief description of the event.
        :param entity_type: str
            The type of the event entity.
        :param definition: str
            Markdown documentation associated with the event.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the event contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the event has been marked as verified.
        :param published: bool
            Determines if the event is visible to viewers.
        :param teams: list
            A list of team IDs associated with the event.
        :param owners: list
            A list of user IDs who own the event.
        :param owners_groups: list
            A list of group IDs who own the event.
        :param collections: list
            A list of collection IDs the event belongs to.
        :param tags: list
            A list of tag IDs associated with the event.
        :param subscribers: list
            A list of user IDs subscribed to the event for notifications.
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
        return self.client.post("/event/events", data=data)

    def get_events(self):
        """
        Fetches the list of all events in the workspace.

        :return: API response containing the events.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"event"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_event_by_id(self, event_id: str):
        """
        Fetches a specific event by its ID.

        :param event_id: str
            The unique identifier of the event to retrieve.
        :return: API response containing the event details.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{event_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_event(self, event_id: str, **kwargs):
        """
        Updates an event with the specified ID.

        :param event_id: str
            The unique identifier of the event to update
        :param kwargs:
            Additional fields to update in the event.
        :return: API response from the server.
        """
        return self.client.patch(f"/event/events/{event_id}", data=kwargs)

    def delete_event(self, event_id: str):
        """
        Deletes an event by its ID.

        :param event_id: str
            The unique identifier of the event to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/event/events/{event_id}")

    def create_event_property(
        self,
        type: str,
        title: str,
        description: str,
        enum: str = None,
        is_required: bool = False,
        integration: str = None,
        entity_type: str = '',
        definition: str = '',
        parent: str = None,
        pii: bool = False,
        verified: bool = False,
        published: bool = True,
        teams: list = [],
        owners: list = [],
        owners_groups: list = [],
        collections: list = [],
        tags: list = [],
        subscribers: list = []
    ):
        """
        Creates a new event property in the workspace.
        :param type: str
            The type of property associated with the event.
        :param enum: str
            If the property type is enum, this field indicates the various enum values.
        :param is_required: bool
            Set this to true if the property is required.
        :param title: str
            The title of the resource.
        :param integration: str
            The integration ID associated with the resource, if one exists.
        :param description: str
            A description of the resource.
        :param entity_type: str
            The type of the resource.
        :param definition: str
            Markdown documentation to be added to the resource.
        :param parent: str
            The ID of the parent resource.
        :param pii: bool
            Indicates whether the resource contains personally identifiable information (PII).
        :param verified: bool
            Indicates whether the resource has been set as verified.
        :param published: bool
            Indicates if the resource is visible to viewers or not.
        :param teams: list
            A list of team IDs that the resource belongs to.
        :param owners: list
            A list of owner user IDs for the resource.
        :param owners_groups: list
            A list of owner group IDs for the resource.
        :param collections: list
            A list of collection IDs the resource belongs to.
        :param tags: list
            A list of tag IDs associated with the resources.
        :param subscribers: list
            A list of user IDs that have been subscribed to the resource.
        :return: API response from the server.
        """
        data = {
            "type": type,
            "enum": enum,
            "is_required": is_required,
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
        return self.client.post("/event/property", data=data)

    def get_event_properties(self):
        """
        Fetches the list of all event properties in the workspace.

        :return: API response containing the event properties.
        """
        all_results = []
        endpoint = "/event/event_properties/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_event_property_by_id(self, event_property_id: str):
        """
        Fetches a specific event property by its ID.

        :param event_property_id: str
            The unique identifier of the event category to retrieve.
        :return: API response containing the event category details.
        """
        return self.client.get(f"/event/category/{event_property_id}")

    def update_event(self, event_property_id: str, **kwargs):
        """
        Updates an event with the specified ID.

        :param event_property_id: str
            The unique identifier of the event property to update
        :param kwargs:
            Additional fields to update in the event.
        :return: API response from the server.
        """
        return self.client.patch(f"/event/event_properties/{event_property_id}", data=kwargs)

    def delete_event(self, event_property_id: str):
        """
        Deletes an event property by its ID.

        :param event_property_id: str
            The unique identifier of the event property to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/event/event_properties/{event_property_id}")
