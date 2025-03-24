#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-chunkystreamsocket-py
"""Unit tests for ChunkyStreamSocket."""

from dataclasses import dataclass
import socket
import threading
import time

import pytest
from pymisclib.chunkystreamsocket import ChunkyStreamSocket


@dataclass
class EchoServer:
    """Simple test server that accepts connections and echos all input."""
    _backlog: int = 0  # allow no connection backlog
    _loop_time: float = 0.1
    _running: bool = False
    _sock: socket.socket|None = None
    _thread: threading.Thread|None = None

    @property
    def port(self) -> int|None:
        """Return the server port."""
        if self._sock is None:
            return None
        return self._sock.getsockname()[1]

    @property
    def running(self) -> bool:
        """True if the loop is running."""
        return self._running

    @property
    def sock(self) -> socket.socket|None:
        """Return the OS socket or None if there is none."""
        return self._sock

    def _client_loop(self,
                     client_sock: socket.socket):
        """Handle client connections while running."""
        client_sock.settimeout(self._loop_time)
        while self._running:
            try:
                msg = client_sock.recv(1)
                client_sock.sendall(msg)
            except socket.timeout:
                pass
            except OSError:
                break
        try:
            client_sock.close()
        except OSError:
            pass

    def _run_loop(self):
        """While running, accept client connections."""
        if self._running:
            raise RuntimeError('Server is already running.')
        self._sock = socket.socket()
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(('localhost', 0))
        self.sock.listen(self._backlog)
        self._running = True
        while self._running:
            client_sock, client_addr = self._sock.accept()
            self._client_loop(client_sock)
        self._sock.close()
        self._sock = None

    def run(self):
        """Run server in a new thread."""
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.start()
        while not self._running:
            time.sleep(0.001)

    def stop(self):
        """Stop the server."""
        self._running = False
        self._thread.join(5.0)
        self._thread = None


@pytest.fixture(autouse=True)
def server() -> EchoServer:
    """Fixture to start an EchoServer before running the test function."""
    server = EchoServer()
    server.run()
    yield server  # run test function
    server.stop()

def connect(es: EchoServer,
            css: ChunkyStreamSocket,
            timeout: float|None):
    """Connect and validate."""
    css.connect(timeout)
    addr, port = css.sock.getpeername()
    assert addr == '127.0.0.1'
    assert port == es.port

def test_connect_ok_timeout(server):
    """Test connection to the server."""
    c = ChunkyStreamSocket(host='127.0.0.1', port=server.port)
    connect(server, c, timeout=0.1)
    c.close()

def test_connect_ok_non_blocking(server):
    """Test connection to the server."""
    c = ChunkyStreamSocket(host='127.0.0.1', port=server.port)
    try:
        connect(server,c, 0)
    except Exception:
        # Non-blocking connect() failed, so give it some time.
        time.sleep(0.1)
        connect(server, c, 0)  # try again
    c.close()

def test_connect_ok_blocking(server):
    """Test connection to the server."""
    c = ChunkyStreamSocket(host='127.0.0.1', port=server.port)
    connect(server, c, timeout=None)
    c.close()
