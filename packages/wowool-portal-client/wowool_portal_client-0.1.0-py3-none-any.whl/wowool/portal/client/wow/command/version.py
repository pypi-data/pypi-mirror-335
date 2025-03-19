from wowool.io.console import console
from wowool.portal.client import get_version


def command(**kwargs):
    from wowool.portal.client import Portal
    from wowool.portal.client.environment import apply_environment_host, apply_environment_api_key

    console.print(f"client: {get_version()}")
    local_kwargs = kwargs
    apply_environment_host(local_kwargs)
    apply_environment_api_key(local_kwargs, empty_ok=True)

    api_key = local_kwargs["api_key"] if local_kwargs["api_key"] != None else "dummy"
    host = local_kwargs["host"]
    with Portal(host=host, api_key=api_key) as portal:
        version = portal.version
        console.print(f"portal: {version['major']}.{version['minor']}.{version['patch']}")

    return 0
