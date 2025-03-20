class CollectionsEndpoint:
    """
    Handles collection-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Collections API.
        """
        self.client = client

    def create_collection(
        self,
        title: str,
        description: str,
        entity_type='glossary',
        icon='🗂',
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
        Creates a new collection in the workspace.
        
        :param icon: str
            Graphical or visual representation of the collection.
        :param title: str
            The title of the collection.
        :param integration: str
            The integration ID associated with the collection, if applicable.
        :param description: str
            A brief description of the collection.
        :param entity_type: str
            The type of the collection entity.
        :param definition: str
            Markdown documentation associated with the collection.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the collection contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the collection has been marked as verified.
        :param published: bool
            Determines if the collection is visible to viewers.
        :param teams: list
            A list of team IDs associated with the collection.
        :param owners: list
            A list of user IDs who own the collection.
        :param owners_groups: list
            A list of group IDs who own the collection.
        :param collections: list
            A list of collection IDs the collection belongs to.
        :param tags: list
            A list of tag IDs associated with the collection.
        :param subscribers: list
            A list of user IDs subscribed to the collection for notifications.
        :return: API response from the server.
        """
        data = {
            "icon": icon,
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
        return self.client.post("/collection/collections/", data=data)

    def get_collections(self):
        """
        Fetches the list of all collections in the workspace.

        :return: API response containing the collections.
        """
        all_results = []
        endpoint = "/collection/collections/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_collection_by_id(self, collection_id: str):
        """
        Fetches a specific collection by its ID.

        :param collection_id: str
            The unique identifier of the collection to retrieve.
        :return: API response containing the collection details.
        """
        return self.client.get(f"/collection/collections/{collection_id}")


    def update_collection(self, collection_id: str, **kwargs):
        """
        Updates a collection using a PATCH request.

        :param collection_id: str
            The unique identifier of the collection to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, icon).
        :return: API response from the server.
        """
        return self.client.patch(f"/collection/collections/{collection_id}", data=kwargs)

    def delete_collection(self, collection_id: str):
        """
        Deletes a collection by its ID.

        :param collection_id: str
            The unique identifier of the collection to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/collection/collections/{collection_id}")
