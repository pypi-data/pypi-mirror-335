from argparse import Namespace
import sys

from wowool.tools.entity_mapper.cli import CLI as BaseCLI

from wowool.portal.client import Pipeline, Portal, get_version
from wowool.portal.client.environment import apply_environment_variables
from wowool.portal.client.error import ClientError

from .argument_parser import ArgumentParser


# fmt: off
def parse_arguments(*argv):
    """
    EyeOnText Wowool Portal Entity Mapper
    usage: entity-mapper [options]
    example : entity-mapper -f test.txt -p english-entities -k [api-key]
    """
    parser = ArgumentParser()
    return parser.parse_args(*argv)
# fmt: on


class CLI(BaseCLI):
    def __init__(self, arguments: Namespace):
        super(CLI, self).__init__(dict(arguments._get_kwargs()))
        try:
            apply_environment_variables(arguments)
            api_key = arguments.api_key
            host = arguments.host
            assert api_key, "api key is required. pass it with -k option or set the environment variable 'WOWOOL_PORTAL_API_KEY' "
            self.portal = Portal(host=host, api_key=api_key)
            self.pipeline = Pipeline(portal=self.portal, name=arguments.pipeline)
        except Exception as ex:
            raise RuntimeError(f"Exception: {ex}")

    def run_pipeline(self, ip):
        doc = self.pipeline(ip)
        return doc

    def run(self):
        BaseCLI.run(self)


def main(*argv):
    arguments = parse_arguments(*argv)
    if arguments.version:
        print(f"version: {get_version()}")
        return

    try:
        driver = CLI(arguments)
        driver.run()
    except ClientError as error:
        sys.stderr.write(f"Error: {error}\n")


if "__main__" == __name__:
    main(sys.argv[1:])
