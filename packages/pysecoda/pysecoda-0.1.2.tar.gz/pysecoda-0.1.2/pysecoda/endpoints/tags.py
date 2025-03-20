class TagsEndpoint:
    """
    Handles tag-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Tags API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client

    def create_tag(self, name: str, description: str, color: str = "#149634"):
        """
        Creates a new tag in the workspace.

        :param name: str
            The name of the tag.
        :param description: str
            A brief description of the tag.
        :param color: str, optional
            The color associated with the tag (e.g., hex code or color name). Defaults to "#149634".
        :return: API response from the server.
        """
        data = {"name": name, "description": description, "color": color}
        return self.client.post("/tag/", data=data)

    def get_tags(self):
        """
        Fetches the list of all tags in the workspace.

        :return: API response containing the tags.
        """
        all_results = []
        endpoint = "/tag/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_tag_by_id(self, tag_id: str):
        """
        Fetches a specific tag by its ID.

        :param tag_id: str
            The unique identifier of the tag to retrieve.
        :return: API response containing the tag details.
        """
        return self.client.get(f"/tag/{tag_id}")

    def update_tag(self, tag_id: str, **kwargs):
        """
        Updates a tag using a PATCH request.

        :param tag_id: str
            The unique identifier of the tag to update.
        :param kwargs: dict
            The fields to update (e.g., name, description, color).
        :return: API response from the server.
        """
        return self.client.patch(f"/tag/{tag_id}", data=kwargs)

    def delete_tag(self, tag_id: str):
        """
        Deletes a tag by its ID.

        :param tag_id: str
            The unique identifier of the tag to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/tag/{tag_id}")
