import json
import logging
from typing import Type, Optional

import requests
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.vcs.tools_vars import GITHUB_TOOL, GITLAB_TOOL

logger = logging.getLogger(__name__)

class JsonInput(BaseModel):
    query: str = Field(description="""
        Accepts valid json ONLY! No comments allowed! PRIVATE-TOKEN will be provided separately"""
    )


class GithubTool(CodeMieTool):
    name: str = GITHUB_TOOL.name
    description: str = GITHUB_TOOL.description
    args_schema: Type[BaseModel] = JsonInput
    access_token: Optional[str] = None

    def execute(self, query: str, *args):
        if not self.access_token:
            logger.error("No Git credentials found for this repository")
            raise ToolException("No Git credentials found for repository. Provide Git credentials in 'User Settings'")
        request_json = json.loads(query)
        return requests.request(
            method=request_json.get('method'),
            url=request_json.get('url'),
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.access_token}"
            },
            data=json.dumps(request_json.get('method_arguments'))
        ).json()


class GitlabInput(JsonInput):
    query: str = """
        Accepts valid json ONLY! No comments allowed! PRIVATE-TOKEN will be provided separately
        json object which MUST contain: 'method', 'url', 'method_arguments', 'header' that later will be 
        passed to python requests library. 'url' MUST always start with /api/v4/.
        all parameters MUST be generated based on the Gitlab Public REST API specification.
        Request MUST be a valid JSON object that will pass json.loads validation.
    """


class GitlabTool(CodeMieTool):
    name: str = GITLAB_TOOL.name
    args_schema: Type[BaseModel] = GitlabInput
    base_url: Optional[str] = None
    access_token: Optional[str] = None
    description: str = GITLAB_TOOL.description

    def execute(self, query: str, *args):
        if not self.access_token:
            logger.error("No Git credentials found for this repository")
            raise ToolException("No Git credentials found for repository. Provide Git credentials in 'User Settings'")
        request_json = json.loads(query)
        method = request_json.get('method')
        url = f"{self.base_url}/{request_json.get('url')}"
        method_args = json.dumps(request_json.get('method_arguments'))
        if method == 'GET':
            response = requests.request(
                method=method,
                url=url,
                headers={"Content-Type": "application/json", "PRIVATE-TOKEN": f"{self.access_token}"},
                params=method_args
            )
        else:
            response = requests.request(
                method=method,
                url=url,
                headers={"Content-Type": "application/json", "PRIVATE-TOKEN": f"{self.access_token}"},
                data=method_args
            )
        response_string = f"HTTP: {method} {url} -> {response.status_code} {response.reason} {response.text}"
        logger.debug(response_string)
        return response_string
