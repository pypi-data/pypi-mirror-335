from .api_client import APIClient
from .endpoints.tags import TagsEndpoint
from .endpoints.groups import GroupsEndpoint
from .endpoints.users import UsersEndpoint
from .endpoints.teams import TeamsEndpoint
from .endpoints.documents import DocumentsEndpoint
from .endpoints.lineage import LineageEndpoint
from .endpoints.resources import ResourcesEndpoint
from .endpoints.schemas import SchemasEndpoint
from .endpoints.charts import ChartsEndpoint
from .endpoints.collections import CollectionsEndpoint
from .endpoints.columns import ColumnsEndpoint
from .endpoints.dashboards import DashboardsEndpoint
from .endpoints.databases import DatabasesEndpoint
from .endpoints.monitors import MonitorsEndpoint
from .endpoints.tables import TablesEndpoint
from .endpoints.questions import QuestionsEndpoint
from .endpoints.queries import QueriesEndpoint
from .endpoints.custom_properties import CustomPropertiesEndpoint
from .endpoints.glossary import GlossaryEndpoint
from .endpoints.integrations import IntegrationsEndpoint
from .endpoints.events import EventsEndpoint

REGION_URL = {
    'NA': "https://api.secoda.co/",
    'EU': "https://eapi.secoda.co/",
    'APAC': "https://apac.secoda.co/"
}

class PySecoda(APIClient):
    """
    An API wrapper for the Secoda platform API.
    """
    
    def __init__(self, api_key: str, region='NA'):
        """
        Initializes the Secoda API client.
        
        :param api_key: Bearer token for authentication.
        """

        if region not in REGION_URL:
            raise ValueError("Invalid region. Please use one of 'NA', 'EU', or 'APAC'.")
        self.base_url = REGION_URL[region]

        super().__init__(self.base_url, api_key)
        self.tags = TagsEndpoint(self)
        self.groups = GroupsEndpoint(self)
        self.users = UsersEndpoint(self)
        self.teams = TeamsEndpoint(self)
        self.documents = DocumentsEndpoint(self)
        self.lineage = LineageEndpoint(self)
        self.resources = ResourcesEndpoint(self)
        self.schemas = SchemasEndpoint(self)
        self.charts = ChartsEndpoint(self)
        self.collections = CollectionsEndpoint(self)
        self.columns = ColumnsEndpoint(self)
        self.dashboards = DashboardsEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.monitors = MonitorsEndpoint(self)
        self.tables = TablesEndpoint(self)
        self.questions = QuestionsEndpoint(self)
        self.queries = QueriesEndpoint(self)
        self.custom_properties = CustomPropertiesEndpoint(self)
        self.glossary = GlossaryEndpoint(self)
        self.integrations = IntegrationsEndpoint(self)
        self.events = EventsEndpoint(self)
