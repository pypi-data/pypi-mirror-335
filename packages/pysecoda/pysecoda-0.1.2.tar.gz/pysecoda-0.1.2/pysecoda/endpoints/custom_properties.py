class CustomPropertiesEndpoint:
    """
    Handles custom properties-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the CustomProperties API.
        """
        self.client = client

    def create_custom_property(self, name: str, entity_types: list, value_type: str):
        """
        Creates a new custom property.

        :param name: str
            The name of the custom property.
        :param entity_types: list
            The entity types the property applies to.
        :param value_type: str
            The type of value the property holds.
        :return: API response from the server.
        """
        data = {
            "name": name,
            "entity_types": entity_types,
            "value_type": value_type,
        }
        return self.client.post("/resource/all_v2/custom_properties/", data=data)

    def get_custom_properties(self):
        """
        Fetches all custom properties.

        :return: API response containing a list of custom properties.
        """
        return self.client.get(f"/resource/all_v2/custom_properties/")

    def get_custom_property(self, custom_property_id: str):
        """
        Fetches a specific custom property by its ID.

        :param custom_property_id: str
            The unique identifier of the custom property to retrieve.
        :return: API response containing the custom property details.
        """
        return self.client.get(f"/resource/all_v2/custom_properties/{custom_property_id}")

    def update_custom_property(self, custom_property_id: str, **kwargs):
        """
        Updates a custom property using a PATCH request.

        :param custom_property_id: str
            The unique identifier of the custom property to update.
        :param kwargs: dict
            The fields to update (e.g., name, entity_types, value_type).
        :return: API response from the server.
        """
        return self.client.patch(f"/resource/all_v2/custom_properties/{custom_property_id}", data=kwargs)

    def update_entity_custom_property_value(self, entity_id: str, custom_property_id: str, value: str):
        """
        Updates the value of a custom property for a specific entity.

        :param entity_id: str
            The unique identifier of the entity to update.
        :param custom_property_id: str
            The unique identifier of the custom property to update.
        :param value: str
            The new value for the custom property.
        :return: API response from the server.
        """
        data = {
            "value": value
        }
        return self.client.patch(f"/resource/all_v2/custom_properties/{custom_property_id}/{entity_id}", data=data)

    def delete_custom_property(self, custom_property_id: str):
        """
        Deletes a custom property by its ID.

        :param custom_property_id: str
            The unique identifier of the custom property to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/resource/all_v2/custom_properties/{custom_property_id}")