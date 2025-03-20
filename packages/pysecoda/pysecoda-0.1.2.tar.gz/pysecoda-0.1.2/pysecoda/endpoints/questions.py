class QuestionsEndpoint:
    """
    Handles question-related API requests.
    """

    def __init__(self, client):
        """
        Initializes the Question API.
        """
        self.client = client

    def create_question(
        self,
        assigned_to: str,
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
        Creates a new question in the workspace.
        
        :param assigned_to: str
            The user ID to whom the question is assigned.
        :param title: str
            The title of the question.
        :param integration: str
            The integration ID associated with the question, if applicable.
        :param description: str
            A brief description of the question.
        :param entity_type: str
            The type of the question entity.
        :param definition: str
            Markdown documentation associated with the question.
        :param parent: str
            The ID of the parent resource in the hierarchy.
        :param pii: bool
            Indicates if the question contains personally identifiable information (PII).
        :param verified: bool
            Indicates if the question has been marked as verified.
        :param published: bool
            Determines if the question is visible to viewers.
        :param teams: list
            A list of team IDs associated with the question.
        :param owners: list
            A list of user IDs who own the question.
        :param owners_groups: list
            A list of group IDs who own the question.
        :param collections: list
            A list of collection IDs the question belongs to.
        :param tags: list
            A list of tag IDs associated with the question.
        :param subscribers: list
            A list of user IDs subscribed to the question for notifications.
        :return: API response from the server.
        """
        data = {
            "assigned_to": assigned_to,
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
        return self.client.post("/question/questions/", data=data)

    def get_questions(self):
        """
        Fetches the list of all questions in the workspace.
        """
        all_results = []
        endpoint = "/question/questions/"
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

    def get_question_by_id(self, question_id: str):
        """
        Fetches a specific question by its ID.

        :param question_id: str
            The unique identifier of the question to retrieve.
        :return: API response containing the question details.
        """
        return self.client.get(f"/question/questions/{question_id}")

    def update_question(self, question_id: str, **kwargs):
        """
        Updates a question using a PATCH request.

        :param question_id: str
            The unique identifier of the question to update.
        :param kwargs: dict
            The fields to update (e.g., title, description, assigned_to).
        :return: API response from the server.
        """
        return self.client.patch(f"/question/questions/{question_id}", data=kwargs)

    def delete_question(self, question_id: str):
        """
        Deletes a question by its ID.

        :param question_id: str
            The unique identifier of the question to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/question/questions/{question_id}")

    def create_question_reply(
        self,
        definition: str,
        parent: str,
        accepted_answer=False,
        owners=[]
    ):
        """
        Creates a reply to a question.

        :param definition: str
            The answer of the reply.
        :param accepted_answer: bool
            Indicates if the answer is accepted or not.
        :param parent: str
            The unique identifier of the parent question.
        :param owners: list
            A list of user IDs who own the reply.
        :return: API response from the server.
        """
        data = {
            "definition": definition,
            "accepted_answer": accepted_answer,
            "parent": parent,
            "owners": owners,
        }
        return self.client.post("/question/replies/", data=data)

    def get_question_replies(self):
        """
        Fetches the list of all question replies in the workspace.
        """
        all_results = []
        endpoint = "/question/replies/"
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

    def get_question_reply_by_id(self, question_reply_id: str):
        """
        Fetches a specific question reply by its ID.

        :param question_reply_id: str
            The unique identifier of the question reply to retrieve.
        :return: API response containing the question details.
        """
        return self.client.get(f"/question/replies/{question_reply_id}")

    def update_question_reply(self, question_reply_id: str, **kwargs):
        """
        Updates a question reply using a PATCH request.

        :param reply_id: str
            The unique identifier of the reply to update.
        :param kwargs: dict
            The fields to update (e.g., definition, accepted_answer).
        :return: API response from the server.
        """
        return self.client.patch(f"/question/replies/{question_reply_id}", data=kwargs)

    def delete_question_reply(self, question_reply_id: str):
        """
        Deletes a question reply by its ID.

        :param reply_id: str
            The unique identifier of the reply to delete.
        :return: API response from the server.
        """
        return self.client.delete(f"/question/replies/{question_reply_id}")
