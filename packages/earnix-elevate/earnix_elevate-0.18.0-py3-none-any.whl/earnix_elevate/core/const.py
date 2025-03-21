from importlib.metadata import version
from typing import Final

SERVER_TPL: Final[str] = "https://{}.e2.earnix.com"
API_CLIENT_CONF_KEY: Final[str] = "configuration"
PACKAGE_VERSION: Final[str] = version("earnix_elevate")
USER_AGENT: Final[str] = f"EarnixElevateSDK/{PACKAGE_VERSION}"
