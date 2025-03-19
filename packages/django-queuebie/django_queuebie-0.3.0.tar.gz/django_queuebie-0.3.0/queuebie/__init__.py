"""Simple message queue for commands and events (CQRS)"""

__version__ = "0.3.0"

from queuebie.registry import MessageRegistry

# Create global message registry
message_registry = MessageRegistry()
