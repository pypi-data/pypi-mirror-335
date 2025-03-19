from typing import List, Optional, Any, Dict

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.code.sonar.config import SonarToolConfig
from codemie_tools.code.sonar.tools import SonarTool
from codemie_tools.code.sonar.tools_vars import SONAR_TOOL


class SonarToolkitUI(ToolKit):
    toolkit: ToolSet = ToolSet.CODEBASE_TOOLS
    tools: List[Tool] = [
        Tool.from_metadata(SONAR_TOOL, settings_config=True),
    ]


class SonarToolkit(BaseToolkit):
    sonar_creds: Optional[SonarToolConfig] = None

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.CODEBASE_TOOLS,
            tools=[
                Tool.from_metadata(SONAR_TOOL),
            ]
        ).model_dump()

    def get_tools(self):
        tools = [
            SonarTool(conf=self.sonar_creds)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        sonar_creds = SonarToolConfig(**configs)
        return SonarToolkit(
            sonar_creds=sonar_creds
        )
