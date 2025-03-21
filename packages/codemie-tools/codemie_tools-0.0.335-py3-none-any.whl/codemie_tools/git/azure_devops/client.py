from typing import Optional

from azure.devops.v7_0.git.git_client import GitClient
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel, ConfigDict

from codemie_tools.base.codemie_tool import logger


class AzureDevOpsCredentials(BaseModel):
    """
    Azure DevOps Credentials model with required fields
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    organization_url: str
    project: str
    repository_id: str
    token: str
    base_branch: str = "main"
    active_branch: Optional[str] = None


class AzureDevOpsClient:
    """Azure DevOps client class for repository operations"""

    def __init__(self, credentials: AzureDevOpsCredentials):
        self.organization_url = credentials.organization_url
        self.project = credentials.project
        self.repository_id = credentials.repository_id
        self.base_branch = credentials.base_branch
        self.active_branch = credentials.active_branch if credentials.active_branch else credentials.base_branch

        # Initialize the client
        auth = BasicAuthentication("", credentials.token)
        self.client = GitClient(base_url=self.organization_url, creds=auth)

        # Verify connection
        try:
            self.client.get_repository(self.repository_id)
        except Exception as e:
            logger.error(f"Failed to connect to Azure DevOps: {e}")

    def branch_exists(self, branch_name):
        """
        Check if a branch exists in the repository
        """
        try:
            branch = self.client.get_branch(
                repository_id=self.repository_id,
                name=branch_name,
                project=self.project
            )
            return branch is not None
        except Exception as e:
            logger.error(f"Failed to check if branch exists: {branch_name}, {str(e)}")
            return False
