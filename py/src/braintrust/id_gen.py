import os
import secrets
from abc import ABC, abstractmethod

from uuid_utils import uuid7


def get_id_generator():
    """Factory function that creates a new ID generator instance each time.

    This eliminates global state and makes tests parallelizable.
    Each caller gets their own generator instance.
    """
    use_otel = os.getenv("BRAINTRUST_OTEL_COMPAT", "false").lower() == "true"
    return OTELIDGenerator() if use_otel else UUIDGenerator()


class IDGenerator(ABC):
    """Abstract base class for ID generators."""

    @abstractmethod
    def get_span_id(self):
        pass

    @abstractmethod
    def get_trace_id(self):
        pass

    @abstractmethod
    def share_root_span_id(self):
        """Return True if the generator should use span_id as root_span_id for backwards compatibility."""
        pass


class UUIDGenerator(IDGenerator):
    """ID generator that uses UUIDv7 for both span and trace IDs."""

    def get_span_id(self):
        return str(uuid7())

    def get_trace_id(self):
        return str(uuid7())

    def share_root_span_id(self):
        return True


class OTELIDGenerator(IDGenerator):
    """ID generator that generates OpenTelemetry-compatible IDs. We use this to have ids that can
    seamlessly flow between Braintrust and OpenTelemetry.
    """

    def get_span_id(self):
        # Generate 8 random bytes and convert to hex
        return secrets.token_hex(8)

    def get_trace_id(self):
        # Generate 16 random bytes and convert to hex
        return secrets.token_hex(16)

    def share_root_span_id(self):
        return False
