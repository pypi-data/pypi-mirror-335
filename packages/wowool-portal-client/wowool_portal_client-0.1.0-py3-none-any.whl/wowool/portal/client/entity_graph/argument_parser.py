from wowool.tools.entity_graph.cli import parser_add_tool_entity_graph_arguments

from wowool.portal.client.argument_parser import (
    ArgumentParser as ArgumentParserBase,
)
from wowool.portal.client.defines import (
    WOWOOL_PORTAL_API_KEY_ENV_NAME,
    WOWOOL_PORTAL_HOST_ENV_NAME,
)

# fmt: off
class ArgumentParser(ArgumentParserBase):
    def __init__(self):
        """
        EyeOnText Wowool Portal Entity Graph
        """
        super(ArgumentParserBase, self).__init__(prog="entity_graph", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file"   ,  help="Folder or file to process")
        self.add_argument("-k", "--api-key",  help=f"API key, available via the Portal. Environment variable: {WOWOOL_PORTAL_API_KEY_ENV_NAME}")
        self.add_argument("-i", "--text"   ,  help="Input text to process")
        self.add_argument("-e","--encoding",  help="Encoding of the files to process, use 'auto' if you do not know the encoding", default="utf8")
        self.add_argument("--host"    ,       help=f"URL to the Portal. Environment variable: {WOWOOL_PORTAL_HOST_ENV_NAME}")
        self.add_argument("--version"      ,  help="Version information", default=False, action="store_true")

        parser_add_tool_entity_graph_arguments( self )

# fmt: on
