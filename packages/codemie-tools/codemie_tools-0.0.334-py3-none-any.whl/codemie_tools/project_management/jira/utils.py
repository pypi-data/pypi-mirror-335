import logging
import re

from atlassian import Jira

from langchain_core.tools import ToolException

logger = logging.getLogger(__name__)


def validate_jira_creds(jira: Jira):
    if jira.url is None or jira.url == "":
        logger.error("Jira URL is required. Seems there no Jira credentials provided.")
        raise ToolException("Jira URL is required. Seems there no Jira credentials provided.")


def clean_json_string(json_string):
    """
    Extract JSON object from a string, removing extra characters before '{' and after '}'.

    Args:
    json_string (str): Input string containing a JSON object.

    Returns:
    str: Cleaned JSON string or original string if no JSON object found.
    """
    pattern = r'^[^{]*({.*})[^}]*$'
    match = re.search(pattern, json_string, re.DOTALL)
    if match:
        return match.group(1)
    return json_string
