"""This module contains the Server class for running the API using Uvicorn."""

import uvicorn

from lightly_purple.server.app import app


class Server:
    """This class represents a server for running the API using Uvicorn."""

    port: int
    host: str

    def __init__(self, host: str, port: int) -> None:
        """Initialize the Server with host and port.

        Args:
            host (str): The hostname to bind the server to.
            port (int): The port number to run the server on.
        """
        self.host = host
        self.port = port

    def start(self) -> None:
        """Start the API server using Uvicorn."""
        # start the app
        uvicorn.run(app, host=self.host, port=self.port, http="h11")
