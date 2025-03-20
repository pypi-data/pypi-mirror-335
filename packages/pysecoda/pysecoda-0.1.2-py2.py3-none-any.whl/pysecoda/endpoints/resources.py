class ResourcesEndpoint:
    """
    Handles resource-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Resources API.
        """
        self.client = client

    def create_resource(
        self,
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
        Creates a new resource in the workspace.
        """
        data = {
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
        return self.client.post("/resource/catalog", data=data)
    
    def get_resources(self, filter=None):
        """
        Fetches the list of all resources in the workspace.
        """
        all_results = []
        page_num = 1

        # set url params
        if filter is not None:
            endpoint = "/resource/catalog/?"+filter+"&page=1"
        else:
            endpoint = "/resource/catalog/?page=1"

        while endpoint:
            response = self.client.get(endpoint)
            print(response['links']['next'])
            data = response['results']
            all_results.extend(data)
            if response['meta']['next_page'] is not None:
                page_num += 1
                if filter is not None:
                    endpoint = "/resource/catalog/?"+filter+"&page="+str(page_num)
                else:
                    endpoint = "/resource/catalog/?page="+str(page_num)
            else:
                endpoint = None

        return all_results

    def get_resource_by_id(self, resource_id: str):
        """
        Fetches a specific resource by its ID.

        :param resourse_id: str
            The unique identifier of the resourse to retrieve.
        :return: API response containing the resourse details.
        """
        return self.client.get(f"/resource/all/{resource_id}")

    def update_resource(self, resource_id: str, **kwargs):
        """
        Updates a resource using a PATCH request.

        :param resource_id: str
            The unique identifier of the resource to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, verified).
        :return: API response from the server.
        """
        return self.client.patch(f"/resource/all/{resource_id}", data=kwargs)

    def delete_resource(self, resource_id: str):
        """
        Deletes a resource by its ID.

        :param resource_id: str
            The unique identifier of the resource to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/resource/all/{resource_id}")
