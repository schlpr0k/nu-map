"""Interfaces for USB physical layers used by nümap."""

from __future__ import annotations

import abc
from typing import Any


class PhyInterface(abc.ABC):
    """Abstract base class for physical layer implementations."""

    def __init__(self, app: Any, name: str) -> None:
        self.app = app
        self.name = name
        self.logger = getattr(app, 'logger', None)

    @abc.abstractmethod
    def send_on_endpoint(self, ep_num: int, data: bytes) -> None:
        """Send *data* to the host on endpoint ``ep_num``."""

    @abc.abstractmethod
    def stall_ep0(self) -> None:
        """Stall control endpoint 0."""

    @abc.abstractmethod
    def run(self) -> None:
        """Run the PHY request loop."""
