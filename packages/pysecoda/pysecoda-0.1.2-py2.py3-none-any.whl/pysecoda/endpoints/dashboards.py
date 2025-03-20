import json
import urllib.parse

from .resources import ResourcesEndpoint

class DashboardsEndpoint:
    """
    Handles dashboard-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Dashboard API.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_dashboard(
        self,
        url: str,
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
        Creates a new dashboard in the workspace.
        
        :param url: str
            The URL of the dashboard.
        :param title: str
            The title of the dashboard.
        :param integration: str
            The integration ID associated with the dashboard, if applicable.
        :param description: str
            A brief description of the dashboard.
        :param entity_type: str
            The type of the dashboard entity.
        :param definition: str
            Markdown documentation associated with the dashboard.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the dashboard contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the dashboard has been marked as verified.
        :param published: bool
            Determines if the dashboard is visible to viewers.
        :param teams: list
            A list of team IDs associated with the dashboard.
        :param owners: list
            A list of user IDs who own the dashboard.
        :param owners_groups: list
            A list of group IDs who own the dashboard.
        :param collections: list
            A list of collection IDs the dashboard belongs to.
        :param tags: list
            A list of tag IDs associated with the dashboard.
        :param subscribers: list
            A list of user IDs subscribed to the dashboard for notifications.
        :return: API response from the server.
        """
        data = {
            "url": url,
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
        return self.client.post("/dashboard/dashboards/", data=data)

    def get_dashboards(self):
        """
        Fetches the dashboards.

        :return: API response containing the dashboards.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"dashboard"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_dashboard_by_id(self, dashboard_id: str):
        """
        Fetches the dashboard.

        :return: API response containing the dashboard.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{dashboard_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_dashboard(self, dashboard_id: str, **kwargs):
        """
        Updates a dashboard using a PATCH request.

        :param dashboard_id: str
            The unique identifier of the dashboard to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, url).
        :return: API response from the server.
        """
        return self.client.patch(f"/dashboard/dashboards/{dashboard_id}", data=kwargs)

    def delete_dashboard(self, dashboard_id: str):
        """
        Deletes a dashboard by its ID.

        :param dashboard_id: str
            The unique identifier of the dashboard to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/dashboard/dashboards/{dashboard_id}")