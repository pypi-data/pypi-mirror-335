class TeamsEndpoint:
    """
    Handles team-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Teams API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client

    def create_team(self, name: str, description: str, members=[]):
        """
        Creates a new team in the workspace.

        :param name: str
            The name of the team.
        :param description: str
            A brief description of the team.
        :param members: list of str, optional
            A list of user IDs that are part of this team. Defaults to an empty list.
        :return: API response from the server.
        """
        data = {"name": name, "description": description, "members": members}
        return self.client.post("/auth/teams/", data=data)

    def get_teams(self):
        """
        Fetches the list of all teams in the workspace.

        :return: API response containing the teams.
        """
        all_results = []
        endpoint = "/auth/teams/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_team_by_id(self, team_id: str):
        """
        Fetches a specific team by its ID.

        :param team_id: str
            The unique identifier of the team to retrieve.
        :return: API response containing the team details.
        """
        return self.client.get(f"/auth/teams/{team_id}")

    def update_team(self, team_id: str, **kwargs):
        """
        Updates a team using a PATCH request.

        :param team_id: str
            The unique identifier of the team to update.
        :param kwargs: dict
            The fields to update (e.g., name, description, members).
        :return: API response from the server.
        """
        return self.client.patch(f"/auth/teams/{team_id}", data=kwargs)

    def delete_team(self, team_id: str):
        """
        Deletes a team by its ID.

        :param team_id: str
            The unique identifier of the team to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/auth/teams/{team_id}")