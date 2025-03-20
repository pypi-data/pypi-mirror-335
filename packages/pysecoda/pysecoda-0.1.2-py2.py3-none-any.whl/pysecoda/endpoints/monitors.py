class MonitorsEndpoint:
    """
    Handles monitor-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Monitor API.
        """
        self.client = client

    def create_monitor(
        self,
        target: str,
        metric_type: str,
        condition_auto_sensitivity=5,
        condition_manual_min=None,
        condition_manual_max=None,
        is_enabled=True,
        metric_config=None,
        schedule={
            "day": 2,
            "hour": 3,
            "cadence": "daily",
            "frequency": 1
        }
    ):
        """
        Creates a new monitor in the workspace.
        
        :param target: str
            The UUID of the column or table to be monitored.
        :param metric_type: str
            "null_percentage" "row_count" "freshness" "cardinality" "maximum" "minimum" "unique_percentage" "custom_sql" Type of metric to monitor, e.g., percentage of null values.
        :param metric_config: dict
            Configuration for custom SQL if metric_type is custom_sql.
        :param is_enabled: bool
            Flag to enable or disable the monitor.
        :param condition_auto_sensitivity: int
            Auto sensitivity level for learning thresholds.
        :param condition_manual_min: float
            Manually set minimum threshold value if auto sensitivity is null.
        :param condition_manual_max: float
            Manually set maximum threshold value if auto sensitivity is null.
        :param schedule: dict
            Dictionary containing day, hour, cadence, and frequency settings.
        :return: API response from the server.
        """
        data = {
            "target": target,
            "metric_type": metric_type,
            "metric_config": metric_config,
            "is_enabled": is_enabled,
            "condition_auto_sensitivity": condition_auto_sensitivity,
            "condition_manual_min": condition_manual_min,
            "condition_manual_max": condition_manual_max,
            "schedule": schedule,
        }
        return self.client.post("/monitor/monitors/", data=data)

    def get_monitors(self):
        """
        Fetches the list of all monitors in the workspace.
        """
        all_results = []
        endpoint = "/monitor/monitors/"
        while endpoint:
            response = self.client.get(endpoint)
            print(response)
            data = response['results']
            all_results.extend(data)
            if response['meta']['next_page'] is not None:
                endpoint = response['links']['next'].replace(self.client.get_base_url(), '') # Get the next page URL
            else:
                endpoint = None
        return all_results

    def get_monitor_by_id(self, monitor_id: str):
        """
        Fetches a specific monitor by its ID.

        :param monitor_id: str
            The unique identifier of the monitor to retrieve.
        :return: API response containing the monitor details.
        """
        return self.client.get(f"/monitor/monitors/{monitor_id}")

    def get_incidents(self):
        """
        Fetches the list of all monitor incidents in the workspace.
        """
        all_results = []
        endpoint = "/monitor/incidents/"
        while endpoint:
            response = self.client.get(endpoint)
            print(response)
            data = response['results']
            all_results.extend(data)
            if response['meta']['next_page'] is not None:
                endpoint = response['links']['next'].replace(self.client.get_base_url(), '') # Get the next page URL
            else:
                endpoint = None
        return all_results

    def get_incident_by_id(self, incident_id: str):
        """
        Fetches a specific monitor incident by its ID.

        :param incident_id: str
            The unique identifier of the monitor incident to retrieve.
        :return: API response containing the monitor incident details.
        """
        return self.client.get(f"/monitor/incidents/{incident_id}")

    def get_measurements(self):
        """
        Fetches the list of all monitor measurements in the workspace.
        """
        all_results = []
        endpoint = "/monitor/measurements/"
        while endpoint:
            response = self.client.get(endpoint)
            print(response)
            data = response['results']
            all_results.extend(data)
            if response['meta']['next_page'] is not None:
                endpoint = response['links']['next'].replace(self.client.get_base_url(), '') # Get the next page URL
            else:
                endpoint = None
        return all_results

    def update_monitor(self, monitor_id: str, **kwargs):
        """
        Updates a monitor using a PATCH request.
        
        :param monitor_id: str
            The unique identifier of the monitor to update.
        :param kwargs: dict
            The fields to update.
        :return: API response from the server.
        """
        return self.client.patch(f"/monitor/monitors/{monitor_id}", data=kwargs)

    def run_monitors(self, monitor_ids: list):
        """
        Runs all monitors in the workspace.
        """
        return self.client.post("/monitor/monitors/run/")
