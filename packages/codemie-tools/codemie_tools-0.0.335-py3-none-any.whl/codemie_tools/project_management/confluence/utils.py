import logging

from atlassian import Confluence
from langchain_core.tools import ToolException

logger = logging.getLogger(__name__)


def validate_creds(confluence: Confluence):
    if confluence.url is None or confluence.url == "":
        logger.error("Confluence URL is required. Seems there no Confluence credentials provided.")
        raise ToolException("Confluence URL is required. Seems there no Confluence credentials provided.")
