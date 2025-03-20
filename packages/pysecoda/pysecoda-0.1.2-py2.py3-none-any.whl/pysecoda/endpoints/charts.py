import json
import urllib.parse

from .resources import ResourcesEndpoint

class ChartsEndpoint:
    """
    Handles chart-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Charts API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client
        self.resources = ResourcesEndpoint(client)

    def create_chart(
        self,
        native_type: str,
        group: str,
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
        Creates a new chart in the workspace.
        
        :param native_type: str
            The native type of the chart as referenced in the integration.
        :param group: str
            The name of the group associated with the chart.
        :param url: str
            The URL of the chart.
        :param title: str
            The title of the chart.
        :param integration: str
            The integration ID associated with the chart, if applicable.
        :param description: str
            A brief description of the chart.
        :param entity_type: str
            The type of the chart entity.
        :param definition: str
            Markdown documentation associated with the chart.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the chart contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the chart has been marked as verified.
        :param published: bool
            Determines if the chart is visible to viewers.
        :param teams: list
            A list of team IDs associated with the chart.
        :param owners: list
            A list of user IDs who own the chart.
        :param owners_groups: list
            A list of group IDs who own the chart.
        :param collections: list
            A list of collection IDs the chart belongs to.
        :param tags: list
            A list of tag IDs associated with the chart.
        :param subscribers: list
            A list of user IDs subscribed to the chart for notifications.
        :return: API response from the server.
        """
        data = {
            "native_type": native_type,
            "group": group,
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
        return self.client.post("/dashboard/charts/", data=data)

    def get_charts(self):
        """
        Fetches the charts.

        :return: API response containing the charts.
        """
        filter_dict = {"operator":"exact", "field":"type", "value":"chart"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def get_chart_by_id(self, chart_id: str):
        """
        Fetches the chart.

        :return: API response containing the chart.
        """
        filter_dict = {"operator":"exact", "field":"id", "value":f"{chart_id}"}
        
        # serialize the filter parameters
        json_string = json.dumps(filter_dict)
        encoded_string = urllib.parse.quote(json_string)
        filter = f"filter={encoded_string}"

        return self.resources.get_resources(filter=filter)

    def update_chart(self, chart_id: str, **kwargs):
        """
        Updates a chart using a PATCH request.

        :param chart_id: str
            The unique identifier of the chart to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, group, url).
        :return: API response from the server.
        """
        return self.client.patch(f"/dashboard/charts/{chart_id}", data=kwargs)

    def delete_chart(self, chart_id: str):
        """
        Deletes a chart by its ID.

        :param chart_id: str
            The unique identifier of the chart to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/dashboard/charts/{chart_id}")
