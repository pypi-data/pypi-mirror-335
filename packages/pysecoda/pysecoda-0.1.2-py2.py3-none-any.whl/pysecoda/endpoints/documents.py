class DocumentsEndpoint:
    """
    Handles document-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Documents API.

        :param client: APIClient
            An instance of APIClient for making requests.
        """
        self.client = client

    def create_document(
        self,
        title: str,
        description: str,
        entity_type='document',
        definition='',
        icon="🗂",
        integration=None,
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
        Creates a new document in the workspace.

        :param icon: str
            The icon of the document.
        :param title: str
            The title of the resource.
        :param integration: str, optional
            The integration ID associated with the resource, if one exists.
        :param description: str
            A description of the resource.
        :param entity_type: str
            The type of the resource.
        :param definition: str, optional
            Markdown documentation to be added to the resource.
        :param parent: str, optional
            The ID of the parent resource.
        :param pii: bool
            Indicates whether the resource contains personally identifiable information (PII).
        :param verified: bool
            Indicates whether the resource has been set as verified.
        :param published: bool
            Indicates if the resource is visible to viewers or not.
        :param teams: list of str, optional
            A list of team IDs that the resource belongs to.
        :param owners: list of str, optional
            A list of owner user IDs for the resource.
        :param owners_groups: list of str, optional
            A list of owner group IDs for the resource.
        :param collections: list of str, optional
            A list of collection IDs the resource belongs to.
        :param tags: list of str, optional
            A list of tag IDs associated with the resource.
        :param subscribers: list of str, optional
            A list of user IDs subscribed to the resource.
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
        return self.client.post("/document/", data=data)

    def get_documents(self):
        """
        Fetches the list of all documents in the workspace.

        :return: API response containing the documents.
        """
        all_results = []
        endpoint = "/document/"
        while endpoint:
            response = self.client.get(endpoint)
            data = response['results']
            all_results.extend(data)
            endpoint = response['links']['next']  # Get the next page URL
        return all_results

    def get_document_by_id(self, document_id: str):
        """
        Fetches a specific document by its ID.

        :param document_id: str
            The unique identifier of the document to retrieve.
        :return: API response containing the document details.
        """
        return self.client.get(f"/document/{document_id}")

    def update_document(self, document_id: str, **kwargs):
        """
        Updates a document using a PATCH request.

        :param document_id: str
            The unique identifier of the document to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, verified, etc.).
        :return: API response from the server.
        """
        return self.client.patch(f"/document/{document_id}", data=kwargs)

    def delete_document(self, document_id: str):
        """
        Deletes a document by its ID.

        :param document_id: str
            The unique identifier of the document to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/document/{document_id}")
