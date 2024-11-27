"""remotetypes server application."""

import logging

import Ice

from remotetypes.factory import Factory


class Server(Ice.Application):
    """Ice.Application para el servidor."""

    def __init__(self) -> None:
        """Inicializa el servidor."""
        super().__init__()
        self.logger = logging.getLogger(__file__)
        self.factory = None

    def run(self, args: list[str]) -> int:
        """Ejecuta las acciones principales del servidor."""
        self.factory = Factory()
        adapter = self.communicator().createObjectAdapter("remotetypes")
        proxy = adapter.add(self.factory, self.communicator().stringToIdentity("factory"))
        self.logger.info('Proxy: "%s"', proxy)

        adapter.activate()
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
