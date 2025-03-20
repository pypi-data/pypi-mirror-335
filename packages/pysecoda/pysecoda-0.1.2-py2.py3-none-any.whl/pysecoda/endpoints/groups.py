class GroupsEndpoint:
    """
    Handles group-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Groups API.

        :param client: An instance of APIClient for making requests.
        """
        self.client = client

    def create_group(self, name: str, description: str, icon='💼', users=[]):
        """
        Creates a new user group in the workspace.

        :param name: str
            The name of the group.
        :param description: str
            A brief description of the group.
        :param icon: str, optional
            The icon representing the group.
        :param users: list of str, optional
            A list of user IDs that are part of this group. Defaults to an empty list.
        :return: API response from the server.
        """
        data = {
            "name": name,
            "icon": icon,
            "description": description,
            "users": users,
        }
        return self.client.post("/auth/group/", data=data)

    def get_groups(self):
        """
        Fetches the list of all groups in the workspace.

        :return: API response containing the groups.
        """
        all_results = []
        endpoint = "/auth/group/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_group_by_id(self, group_id: str):
        """
        Fetches a specific group by its ID.

        :param group_id: str
            The unique identifier of the group to retrieve.
        :return: API response containing the group details.
        """
        return self.client.get(f"/auth/group/{group_id}")

    def update_group(self, group_id: str, **kwargs):
        """
        Updates a group using a PATCH request.

        :param group_id: str
            The unique identifier of the group to update.
        :param kwargs: dict
            The fields to update (e.g., name, icon, description, users).
        :return: API response from the server.
        """
        return self.client.patch(f"/auth/group/{group_id}", data=kwargs)

    def delete_group(self, group_id: str):
        """
        Deletes a group by its ID.

        :param group_id: str
            The unique identifier of the group to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/auth/group/{group_id}")
