# szn_pyfastrpc/__init__.py

from .autostart import start_service

# Automatically start the FastRPC service upon package import.
start_service()

# Expose key classes and functions.
from .protocol import FastRPCInteger, FastRPCString, FastRPCDateTime
from .serializer import serialize, deserialize
from .parser import parse_message
