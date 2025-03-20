# Standard Library
import os

from typing import Dict  # noqa: F401

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcError
from gpc.helpers.session_helper import create_retry_request_session


GPC_GRAPHQL_URL = f"{os.environ.get('GPC_GITLAB_URL', '').rstrip('/')}/api/graphql"
GPC_GITLAB_TOKEN = os.environ.get("GPC_GITLAB_TOKEN", "")


class Singleton(type):
    _instances = {}  # type: Dict[type, type]

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class GraphqlSession:
    def __init__(self):
        self.session = create_retry_request_session()
        self.session.headers.update({"Authorization": "Bearer " + GPC_GITLAB_TOKEN})

    def run_graphql_query(self, query):
        request = self.session.post(
            GPC_GRAPHQL_URL,
            json={"query": query},
        )
        if request.status_code == 200:
            return request.json()

        raise GpcError(f"Unexpected status code returned: {request.status_code}")


class GraphqlSingleton(GraphqlSession, metaclass=Singleton):
    pass
