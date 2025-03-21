from typing import List, Optional

from anyscale._private.sdk import sdk_command
from anyscale.service_account._private.service_account_sdk import (
    PrivateServiceAccountSDK,
)
from anyscale.service_account.models import ServiceAccount


_SERVICE_ACCOUNT_SDK_SINGLETON_KEY = "service_account_sdk"

_CREATE_EXAMPLE = """
import anyscale

api_key = anyscale.service_account.create(
    name="my-service-account",
)
"""

_CREATE_DOCSTRINGS = {"name": "Name for the service account."}

_CREATE_API_KEY_EXAMPLE = """
import anyscale

api_key = anyscale.service_account.create_api_key(
    name="my-service-account",
)
"""

_CREATE_API_KEY_DOCSTRINGS = {
    "email": "Email of the service account to create the new key for.",
    "name": "Name of the service account to create the new key for.",
}

_LIST_EXAMPLE = """
import anyscale

anyscale.service_account.list(
    max_items=20,
)
"""

_LIST_DOCSTRINGS = {
    "max_items": "Maximum number of items to return.",
}

_DELETE_EXAMPLE = """
import anyscale

anyscale.service_account.delete(
    name="my-service-account",
)
"""

_DELETE_DOCSTRINGS = {
    "email": "Email of the service account to delete.",
    "name": "Name of the service account to delete.",
}

_ROTATE_API_KEYS_EXAMPLE = """
import anyscale

anyscale.service_account.rotate_api_keys(
    name="my-service-account",
)
"""

_ROTATE_API_KEYS_DOCSTRINGS = {
    "email": "Rotate API keys for the service account with this email.",
    "name": "Rotate API keys for the service account with this name.",
}


@sdk_command(
    _SERVICE_ACCOUNT_SDK_SINGLETON_KEY,
    PrivateServiceAccountSDK,
    doc_py_example=_CREATE_EXAMPLE,
    arg_docstrings=_CREATE_DOCSTRINGS,
)
def create(name: str, *, _sdk: PrivateServiceAccountSDK) -> str:
    """Create a service account and return the API key.
    """
    return _sdk.create(name)


@sdk_command(
    _SERVICE_ACCOUNT_SDK_SINGLETON_KEY,
    PrivateServiceAccountSDK,
    doc_py_example=_CREATE_API_KEY_EXAMPLE,
    arg_docstrings=_CREATE_API_KEY_DOCSTRINGS,
)
def create_api_key(
    email: Optional[str] = None,
    name: Optional[str] = None,
    *,
    _sdk: PrivateServiceAccountSDK
) -> str:
    """Create an API key for the service account and return the API key.
    """
    return _sdk.create_api_key(email, name)


@sdk_command(
    _SERVICE_ACCOUNT_SDK_SINGLETON_KEY,
    PrivateServiceAccountSDK,
    doc_py_example=_LIST_EXAMPLE,
    arg_docstrings=_LIST_DOCSTRINGS,
)
def list(  # noqa: A001
    max_items: int = 20, *, _sdk: PrivateServiceAccountSDK
) -> List[ServiceAccount]:
    """List service accounts. """
    return _sdk.list(max_items)


@sdk_command(
    _SERVICE_ACCOUNT_SDK_SINGLETON_KEY,
    PrivateServiceAccountSDK,
    doc_py_example=_DELETE_EXAMPLE,
    arg_docstrings=_DELETE_DOCSTRINGS,
)
def delete(
    email: Optional[str] = None,
    name: Optional[str] = None,
    *,
    _sdk: PrivateServiceAccountSDK
):
    """Delete a service account.
    """
    return _sdk.delete(email, name)


@sdk_command(
    _SERVICE_ACCOUNT_SDK_SINGLETON_KEY,
    PrivateServiceAccountSDK,
    doc_py_example=_ROTATE_API_KEYS_EXAMPLE,
    arg_docstrings=_ROTATE_API_KEYS_DOCSTRINGS,
)
def rotate_api_keys(
    email: Optional[str] = None,
    name: Optional[str] = None,
    *,
    _sdk: PrivateServiceAccountSDK
) -> str:
    """Rotate all api keys of a service account and return the new API key.
    """
    return _sdk.rotate_api_keys(email, name)
