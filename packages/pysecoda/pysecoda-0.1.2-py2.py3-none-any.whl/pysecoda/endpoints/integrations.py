class IntegrationsEndpoint:
    """
    Handles integrations-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Integrations API.
        """
        self.client = client

    def create_integration(self, name: str, type: str, teams=[], credentials={}):
        """
        Creates a new integration.

        :param name: str
            The name of the integration data source or tool.
        :param type: str
            The type of integration (e.g., "custom").
        :param teams: list
            A list of team IDs associated with this integration.
        :param credentials: dict
            If adding a custom integration, this should always be an empty dictionary.
        :return: API response from the server.
        """
        data = {
            "name": name,
            "type": type,
            "teams": teams,
            "credentials": credentials,
        }
        return self.client.post("/integration/integrations", data=data)

    def get_integrations(self):
        """
        Fetches the list of all integrations in the workspace.

        :return: API response containing the integrations.
        """
        all_results = []
        endpoint = "/integration/integrations/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_integration(self, integration_id: str):
        """
        Grabs a specific integration by its ID.

        :param integration_id: str
            The unique identifier of the integration to get.
        :return: API response from the server.
        """
        return self.client.get(f"/integration/integrations/{integration_id}")

    def upload_integration_metadata_csv(self, integration_id: str, file: str):
        """
        Uploads a metadata CSV file for an integration.

        :param integration_id: str
            The unique identifier of the integration to upload metadata for.
        :param file: str
            The path to the metadata CSV file.
        :return: API response from the server.
        """
        data = {
            "file": file
        }
        return self.client.post(f"/integration/integrations/{integration_id}/import_metadata", data=data)

    def upload_integration_metadata_jsonl(self, integration_id: str, resources_file: str, lineages_file):
        """
        Uploads metadata JSONL files for an integration.

        :param integration_id: str
            The unique identifier of the integration to upload metadata for.
        :param resources_file: str
            The path to the resources JSONL file.
        :param lineages_file: str
            The path to the lineages JSONL file.
        :return: API response from the server.
        """
        data = {
            "resources_file": resources_file,
            "lineages_file": lineages_file
        }
        return self.client.post(f"/integration/integrations/{integration_id}/import_metadata", data=data)

    def upload_dbt_core_artifacts(self, integration_id: str, run_results: str, manifest: str):
        """
        Uploads dbt core artifacts for an integration.

        :param integration_id: str
            The unique identifier of the integration to upload dbt core artifacts for.
        :param run_results: str
            The path to the run_results.json file.
        :param manifest: str
            The path to the manifest.json file.
        :return: API response from the server.
        """
        data = {
            "run_results": run_results,
            "manifest": manifest
        }
        return self.client.post(f"/integration/dbt/{integration_id}/upload_artifacts", data=data)

    def trigger_dbt_core_sync(self, integration_id: str):
        """
        Triggers a dbt core sync for an integration.

        :param integration_id: str
            The unique identifier of the integration to trigger a dbt core sync for.
        :return: API response from the server.
        """
        return self.client.post(f"/integration/dbt/{integration_id}/trigger")

    def get_entities_with_failing_tests(self, integration_id: str):
        """
        Fetches entities with failing tests for an integration.

        :param integration_id: str
            The unique identifier of the integration to get entities with failing tests for.
        :return: API response from the server.
        """
        return self.client.get(f"/integration/dbt/{integration_id}/failing_tests")

    def delete_integration(self, integration_id: str):
        """
        Deletes an integration by its ID.

        :param integration_id: str
            The unique identifier of the integration to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/integration/integrations/{integration_id}")


