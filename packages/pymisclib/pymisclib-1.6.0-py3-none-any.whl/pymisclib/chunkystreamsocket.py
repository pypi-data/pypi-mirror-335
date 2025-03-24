#!/usr/bin/env python3
# vim ts=4,fileencoding=utf-8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2012-2022, 2023 by Christian Dönges
# SPDXID: SPDXRef-chunkystreamsocket-py
"""A socket used to send and receive message chunks over a TCP connection.

The chunks are assembled back together when receiving.
"""

# pylint: disable=consider-using-assignment-expr

from dataclasses import dataclass
import logging
import socket


@dataclass
class ChunkyStreamSocket:
    """Socket used to send message chunks over a TCP connection."""
    host: str = '127.0.0.1'  # Host name or IP address.
    """Host name or IP address."""
    port: int = 10000
    """Port number."""
    sock: socket.socket | None = None
    """Socket to use."""
    logger: logging.Logger = logging.getLogger(__name__)
    """Logger for diagnostics."""
    debug: bool = False
    """True to enable debug output."""
    log_n_bytes: int = 0   # number of communicated bytes to log
    """Number of communicated bytes to log."""
    _backlog_bytes: bytes | None = None
    _chunk_size: int = 4096
    _server_socket: bool = False  # True for a server socket, False for a client socket.

    def __post_init__(self):
        """Custom initializer called after __init__().
        """
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __str__(self) -> str:
        """Human-readable representation of the instance."""
        return f'<{self.__class__.__name__} {self.connection}>'

    @property
    def connection(self) -> str:
        """Human-readable description of the underlying connection."""
        if self.sock is None:
            return 'no socket'
        if self._server_socket:
            return f'listening at {self.host}:{self.port}'
        else:
            return f'connected to {self.host}:{self.port}'

    @property
    def server_socket(self) -> bool:
        """Is this a server socket (which accepts connections) or a client
            socket, which connects to a server?

        :return: True if server socket, False if client socket.
        """
        return self._server_socket

    def bind_and_listen(self, backlog: int = 5, timeout: float = None):
        """Bind to the host and port to make a server socket.

            :param int backlog: The maximum number of queued connections.
            :param float timeout: The number of seconds after which socket
                 operations will time out. Set to None for a blocking socket.

        """
        self.logger.debug('bind_and_listen(%s:%u)', self.host, self.port)
        # Set the timeout.
        self.sock.settimeout(timeout)
        # Allow the server socket to re-bind immediately.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the given address and port.
        self.sock.bind((self.host, self.port))
        self._server_socket = True
        # Start listening for a connection attempt.
        self.sock.listen(backlog)

    def accept(self) -> tuple[int, tuple[str, int]]:
        """Accept a client connection on the (server) socket.

            :return: The client socket and client address tuple.
            :rtype: tuple[int, tuple[str, int]]
            :raise TimeoutError: No connection accepted withing allowed time.

        """
        try:
            (client_sock, client_addr) = self.sock.accept()  # pylint: disable=no-member
        except socket.timeout as ex:
            raise TimeoutError('accept() timed out') from ex
        self.logger.debug('accept(%s)', client_addr)
        return (client_sock, client_addr)

    def close(self):
        """Close the socket."""
        self.logger.debug('close() %s', self.connection)
        try:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Ignore errors in shutdown since we close the socket anyways.
                pass
            self.sock.close()
            self.sock = None
        except AttributeError:
            # If the socket has been closed asynchronously, self.socket
            # may be None, resulting in this error.
            pass
        self._client_address = None

    def connect(self, timeout: float|None = None):
        """Connect client socket to the server at host:port.

        :param float timeout: The number of seconds after which socket
            operations will time out. Set to None for a blocking socket.
        :raise ConnectionError: Failed to establish connection.
        :raise InterruptedError: Connection attempt was interrrupted by a signal.
        :raise TimeoutError: Connection attempt timed out.
        """
        if timeout is None:
            self.logger.debug('connect(%s:%u, BLOCKING)', self.host, self.port)
        elif timeout == 0:
            self.logger.debug('connect(%s:%u, NON-BLOCKING)', self.host, self.port)
        else:
            self.logger.debug('connect(%s:%u, TIMEOUT:%f)', self.host, self.port, timeout)
        # Set the timeout.
        self.sock.settimeout(timeout)
        # Allow socket to re-bind immediately.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.connect((self.host, self.port))
        except InterruptedError as ex:
            self.logger.error('Connection attempt to %s:%u interrupted: %s',
                              self.host, self.port, ex)
            raise ex
        except TimeoutError as ex:
            self.logger.error('Connection attempt to %s:%u timed out: %s',
                              self.host, self.port, ex)
            raise ex
        except OSError as ex:
            self.logger.error('Connection attempt to %s:%u failed: %s',
                              self.host, self.port, ex)
            raise ConnectionError('unable to connect') from ex
        self.logger.debug('Connected to %s:%s', self.host, self.port)

    def send(self, msg_bytes: bytes) -> int:
        """Send the bytes.

        :param bytes msg_bytes: The bytes to send. If the receiver is expecting
            a separator, it must be appended to the message by the caller.
        :return: The number of bytes sent.
        :rtype: int
        :raise ConnectionError: sending failed because the connection was broken.
        """
        total_nr_sent = 0
        while total_nr_sent < len(msg_bytes):
            current_nr_sent = 0
            try:
                current_nr_sent = self.sock.send(msg_bytes[total_nr_sent:])
            except ConnectionAbortedError as ex:
                self.logger.debug('Connection ')
            if current_nr_sent == 0:
                self.logger.debug('self.sock.send() failed.')
                raise ConnectionError("socket connection broken")
            total_nr_sent = total_nr_sent + current_nr_sent
        if self.log_n_bytes != 0:
            self.logger.debug('--> %s', msg_bytes[:self.log_n_bytes])
        return total_nr_sent

    def recv(self, length: int, timeout: float = None) -> bytes:
        """Receive length bytes from the socket.

        This function handles chunked data (i.e. the data to receive is split
        into multiple packets). If more data than expected is received, it is
        placed into a backlog buffer until the next call to a receive
        function.

        :param int length: Number of bytes to read.
        :param float timeout: Timeout in seconds or `None` for blocking I/O.
        :return: The received bytes.
        :rtype: bytes

        :raise ConnectionError: The connection was broken.
        :raise TimeoutError: Timeout while receiving.
        """
        if length == 0:
            return bytes()
        chunks = []
        nr_received = 0
        # Retrieve the backlog from the previous recv() call and use it as the
        # first chunk.
        if self._backlog_bytes is not None:
            chunks.append(self._backlog_bytes)
            nr_received = len(self._backlog_bytes)
            self._backlog_bytes = None

        # Set the timeout.
        self.sock.settimeout(timeout)

        # Receive bytes until we have enough to satisfy the length requirement.
        while nr_received < length:
            recv_len = min(length - nr_received, self._chunk_size)
            chunk = self.sock.recv(recv_len)
            if self.debug:
                self.logger.debug('socket.recv(%u) := %s', recv_len, chunk)
            if chunk == b'':
                # Connection was closed.
                break
            chunks.append(chunk)
            nr_received = nr_received + len(chunk)

        # Join all chunks into one message.
        msg_bytes = b''.join(chunks)

        # Check if the connection was closed.
        if len(msg_bytes) == 0:
            self.logger.debug('No data received, connection closed.')
            raise ConnectionError("socket connection broken")

        # Cut off the part that is too long.
        if len(msg_bytes) > length:
            self._backlog_bytes = msg_bytes[length:]
            msg_bytes = msg_bytes[:length]

        if self.log_n_bytes != 0:
            self.logger.debug('<-- %s', msg_bytes[:self.log_n_bytes])
        return msg_bytes

    def recv_to_separator(self, separator: bytes) -> bytes:
        """Receive bytes until the given separator is found.

        This function handles chunked data (i.e. the data to receive is
        split into multiple packets). If more data than expected is
        received, it is placed into a backlog buffer until the next call
        to a receive function.

        :param bytes separator: One or more bytes that separate messages in the
            TCP stream.
        :return: The received bytes.
        :rtype: bytes

        :raise ConnectionError: The connection was broken.
        :raise TimeoutError: A timeout occurred while receiving.
        """
        self.logger.debug('recv_to_separator(%s)', separator)
        start_search_index = 0
        chunk = b''
        msg_bytes = b''
        while True:
            if self._backlog_bytes is not None and len(self._backlog_bytes) > 0:
                # The first time around, process the backlog.
                chunk = self._backlog_bytes
                self._backlog_bytes = None
                if self.debug:
                    self.logger.debug('backlog chunk = %s', chunk)
            else:
                chunk = self.sock.recv(self._chunk_size)
                if self.debug:
                    self.logger.debug('socket.recv(%d) := %s', self._chunk_size, chunk)
            if chunk == b'':
                raise ConnectionError("socket connection broken")

            msg_bytes = msg_bytes + chunk
            start_separator_index = msg_bytes.find(separator, start_search_index)
            if start_separator_index > -1:
                # We found the separator at index start_separator_index.
                self._backlog_bytes = msg_bytes[start_separator_index + len(separator):]
                if self.debug:
                    self.logger.debug('Backlog: %u bytes', self._backlog_bytes)
                msg_bytes = msg_bytes[:start_separator_index]
                break
            # The separator could have started in the current chunk but
            # finishes in the next chunk, so we need to search the
            # len(separator) - 1 last bytes of the separator again
            start_search_index = max(0, len(msg_bytes) - (len(separator) - 1))

        if self.log_n_bytes != 0:
            self.logger.debug('<-- %s', msg_bytes[:self.log_n_bytes])
        return msg_bytes


if __name__ == '__main__':
    import sys
    from threading import Barrier, BrokenBarrierError, Thread
    from time import sleep

    start_barrier = Barrier(2, timeout=5)
    end_barrier = Barrier(3, timeout=60)
    MSG_SEP = b'\0\1\2\1\0'

    messages = [
        b'abcdef',
        b'1234',
        b'a', b'bc', b'de\0', b'\1\2\1\0fghi',
        b'xyzZYX',
        b'',
        b'+++',
    ]

    def server():
        """Test server."""
        logger = logging.getLogger('server')
        logger.info('server starting')
        server_socket = ChunkyStreamSocket(logger=logging.getLogger('server.socket'))
        server_socket.bind_and_listen(timeout=60)
        logger.debug('server_socket = %s', server_socket.sock)
        start_barrier.wait()

        logger.info('server running')
        (accepted_socket, client_addr) = server_socket.accept()
        logger.debug('Accepted client from %s:%u', client_addr[0], client_addr[1])
        cs = ChunkyStreamSocket(sock=accepted_socket,
                                logger=logging.getLogger('server.cs'))
        while True:
            msg = cs.recv_to_separator(MSG_SEP)
            logger.info('MSG: %s', msg)
            if msg == b'+++':
                logger.debug('EOF received')
                break

        logger.info('server closing connection')
        cs.close()
        server_socket.close()
        try:
            end_barrier.wait()
        except BrokenBarrierError:
            logger.error('server() end_barrier broken')

    def client():
        """Test client."""
        logger = logging.getLogger('client')
        logger.info('client starting')
        client_socket = ChunkyStreamSocket(logger=logging.getLogger('client.socket'))
        logger.debug('client_socket = %s', client_socket.sock)
        start_barrier.wait()
        logger.info('client running')
        client_socket.connect()
        for message in messages:
            try:
                client_socket.send(message + MSG_SEP)
            except RuntimeError as e:
                logger.critical('send(%u) failed: %s', len(message + MSG_SEP), e)
                logger.critical('client terminating')
                break
        try:
            end_barrier.wait()
        except BrokenBarrierError:
            logger.error('client() end_barrier broken')
        finally:
            client_socket.close()

    # Log everything to the console.
    main_logger = logging.getLogger()
    main_logger.setLevel(logging.NOTSET)
    ch = logging.StreamHandler()
    ch.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s - %(name)20s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    main_logger.addHandler(ch)

    server_thread = Thread(target=server, args=())
    client_thread = Thread(target=client, args=())
    server_thread.start()
    sleep(1.0)  # give the server time to set up before starting client.
    client_thread.start()
    main_logger.info('Client and server running.')
    try:
        end_barrier.wait(timeout=5)
    except BrokenBarrierError:
        main_logger.error('Barrier broken. Terminating')
    sys.exit(0)
