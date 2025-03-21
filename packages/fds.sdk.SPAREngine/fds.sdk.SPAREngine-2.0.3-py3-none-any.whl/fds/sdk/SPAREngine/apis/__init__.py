
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.accounts_api import AccountsApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from fds.sdk.SPAREngine.api.accounts_api import AccountsApi
from fds.sdk.SPAREngine.api.benchmarks_api import BenchmarksApi
from fds.sdk.SPAREngine.api.components_api import ComponentsApi
from fds.sdk.SPAREngine.api.currencies_api import CurrenciesApi
from fds.sdk.SPAREngine.api.documents_api import DocumentsApi
from fds.sdk.SPAREngine.api.frequencies_api import FrequenciesApi
from fds.sdk.SPAREngine.api.spar_calculations_api import SPARCalculationsApi
