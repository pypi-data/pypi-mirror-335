import json
import logging
import re
import traceback
from json import JSONDecodeError
from typing import Type, Dict, Any, Optional

from atlassian import Jira
from pydantic import BaseModel, Field
from langchain_core.tools import ToolException

from codemie_tools.base.codemie_tool import CodeMieTool
from codemie_tools.project_management.jira.tools_vars import GENERIC_JIRA_TOOL
from codemie_tools.project_management.jira.utils import validate_jira_creds, clean_json_string

logger = logging.getLogger(__name__)


class JiraInput(BaseModel):
    method: str = Field(
        ...,
        description="The HTTP method to use for the request (GET, POST, PUT, DELETE, etc.). Required parameter."
    )
    relative_url: str = Field(
        ...,
        description="""
        Required parameter: The relative URI for JIRA REST API V2.
        URI must start with a forward slash and '/rest/api/2/...'.
        Do not include query parameters in the URL, they must be provided separately in 'params'.
        For search/read operations, you MUST always get "key", "summary", "status", "assignee", "issuetype" and 
        set maxResult, until users ask explicitly for more fields.
        """
    )
    params: Optional[str] = Field(
        default="",
        description="""
        Optional JSON of parameters to be sent in request body or query params. MUST be string with valid JSON. 
        For search/read operations, you MUST always get "key", "summary", "status", "assignee", "issuetype" and 
        set maxResult, until users ask explicitly for more fields.
        """
    )


def parse_payload_params(params: Optional[str]) -> Dict[str, Any]:
    if params:
        try:
            return json.loads(clean_json_string(params))
        except JSONDecodeError:
            stacktrace = traceback.format_exc()
            logger.error(f"Jira tool: Error parsing payload params: {stacktrace}")
            raise ToolException(f"JIRA tool exception. Passed params are not valid JSON. {stacktrace}")
    return {}


def get_issue_field(issue, field, default=None):
    field_value = issue.get("fields", {}).get(field, default)
    # Additional verification. In some cases key is present, but value is None. Need to return default value
    return field_value if field_value else default


def get_additional_fields(issue, additional_fields):
    additional_data = {}
    for field in additional_fields:
        if field not in additional_data:  # Avoid overwriting any main fields
            additional_data[field] = get_issue_field(issue, field)
    return additional_data


def process_issue(jira_base_url, issue, payload_params: Dict[str, Any] = None):
    issue_key = issue.get('key')
    jira_link = f"{jira_base_url}/browse/{issue_key}"

    parsed_issue = {
        "key": issue_key,
        "url": jira_link,
        "summary": get_issue_field(issue, "summary", ""),
        "assignee": get_issue_field(issue, "assignee", {}).get("displayName", "None"),
        "status": get_issue_field(issue, "status", {}).get("name", ""),
        "issuetype": get_issue_field(issue, "issuetype", {}).get("name", "")
    }

    process_payload(issue, payload_params, parsed_issue)
    return parsed_issue


def process_payload(issue, payload_params, parsed_issue):
    fields_list = extract_fields_list(payload_params)

    if fields_list:
        update_parsed_issue_with_additional_data(issue, fields_list, parsed_issue)


def extract_fields_list(payload_params):
    if payload_params and 'fields' in payload_params:
        fields = payload_params['fields']
        if isinstance(fields, str) and fields.strip():
            return fields.split(",")
        elif isinstance(fields, list) and fields:
            return fields
    return []


def update_parsed_issue_with_additional_data(issue, fields_list, parsed_issue):
    additional_data = get_additional_fields(issue, fields_list)
    for field, value in additional_data.items():
        if field not in parsed_issue and value:
            parsed_issue[field] = value


def process_search_response(jira_url, response, payload_params: Dict[str, Any] = None):
    if response.status_code != 200:
        return response.text

    processed_issues = []
    json_response = response.json()

    for issue in json_response.get('issues', []):
        processed_issues.append(process_issue(jira_url, issue, payload_params))

    return str(processed_issues)


class GenericJiraIssueTool(CodeMieTool):
    jira: Jira
    name: str = GENERIC_JIRA_TOOL.name
    description: str = GENERIC_JIRA_TOOL.description
    args_schema: Type[BaseModel] = JiraInput
    # Regular expression to match /rest/api/[any number]/search
    issue_search_pattern: str = r'/rest/api/\d+/search'

    def execute(self, method: str, relative_url: str, params: Optional[str] = "", *args):
        validate_jira_creds(self.jira)
        payload_params = parse_payload_params(params)
        if method == "GET":
            response = self.jira.request(
                method=method,
                path=relative_url,
                params=payload_params,
                advanced_mode=True
            )
            self.jira.raise_for_status(response)
            if re.match(self.issue_search_pattern, relative_url):  # Check if the URL matches the search endpoint
                response_text = process_search_response(self.jira.url, response, payload_params)
            else:  # For all other GET requests, including different search endpoints
                response_text = response.text
        else:
            response = self.jira.request(
                method=method,
                path=relative_url,
                data=payload_params,
                advanced_mode=True
            )
            self.jira.raise_for_status(response)
            response_text = response.text
        response_string = f"HTTP: {method} {relative_url} -> {response.status_code} {response.reason} {response_text}"
        logger.debug(response_string)
        return response_string
