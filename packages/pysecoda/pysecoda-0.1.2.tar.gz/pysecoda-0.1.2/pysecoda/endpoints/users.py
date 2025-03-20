class UsersEndpoint:
    """
    Handles user-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Users API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        role: str,
        teams=[],
        user_groups=[]
    ):
        """
        Creates a new user in the workspace.

        :param first_name: str
            The first name of the user.
        :param last_name: str
            The last name of the user.
        :param email: str
            The email ID of the user.
        :param role: str
            The role of the user. Values can be: Admin, Editor, Viewer, Guest.
        :param teams: list of str, optional
            List of team IDs. Mandatory if the role is Guest.
        :param user_groups: list of str, optional
            List of group IDs the user belongs to.
        :return: API response from the server.
        """
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "teams": teams,
            "user_groups": user_groups,
        }
        return self.client.post("/user/", data=data)

    def get_users(self):
        """
        Fetches the list of all users in the workspace.

        :return: API response containing the users.
        """
        all_results = []
        endpoint = "/user/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_user_by_id(self, user_id: str):
        """
        Fetches a specific user by their ID.

        :param user_id: str
            The unique identifier of the user to retrieve.
        :return: API response containing the user details.
        """
        return self.client.get(f"/user/{user_id}")

    def update_user(self, user_id: str, **kwargs):
        """
        Updates a user's details using a PATCH request.

        :param user_id: str
            The unique identifier of the user to update.
        :param kwargs: dict
            The fields to update (e.g., first_name, last_name, email, role, teams, user_groups).
        :return: API response from the server.
        """
        return self.client.patch(f"/user/{user_id}", data=kwargs)

    def delete_user(self, user_id: str):
        """
        Deletes a user by their ID.

        :param user_id: str
            The unique identifier of the user to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/user/{user_id}")
