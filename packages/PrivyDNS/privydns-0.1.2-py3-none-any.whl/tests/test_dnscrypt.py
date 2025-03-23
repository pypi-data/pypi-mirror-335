import pytest
from unittest.mock import patch, MagicMock
import dns.message
from privydns import DNSCryptResolver, DNSQueryError
from privydns.dnscrypt import encrypt_query


@pytest.fixture
def mock_socket():
    """Fixture to mock the socket.socket class."""
    with patch('socket.socket') as mock_socket_class:
        # Create a mock instance of the socket
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value = mock_socket_instance
        yield mock_socket_instance


@pytest.fixture
def mock_encrypt_query():
    """Fixture to mock the encrypt_query function."""
    with patch('privydns.dnscrypt.encrypt_query') as mock_encrypt_query:
        yield mock_encrypt_query


def test_query_success(mock_encrypt_query, mock_socket):
    """
    Test successful DNSCrypt query.
    """
    # Mock the encrypted query
    mock_query = MagicMock(spec=dns.message.Message)
    mock_query.to_wire.return_value = b'fake_query_wire'
    mock_encrypt_query.return_value = b'fake_encrypted_query'

    # Mock socket behavior correctly
    mock_socket.recvfrom.return_value = (b'fake_response_wire', 'fake_address')

    # Mock DNS response
    mock_dns_response = MagicMock()
    mock_dns_response.answer = ["fake_answer"]
    dns.message.from_wire = MagicMock(return_value=mock_dns_response)

    # Instantiate the resolver and run the query
    resolver = DNSCryptResolver(server="1.1.1.1", port=853)
    response = resolver.query("example.com")

    # Assertions
    mock_socket.sendto.assert_called_once_with(b'fake_encrypted_query', ('1.1.1.1', 853))
    assert response == ["fake_answer"]

    mock_encrypt_query.assert_called_once()
    assert isinstance(mock_encrypt_query.call_args[0][0], dns.message.Message)


def test_query_failure(mock_encrypt_query, mock_socket):
    """
    Test DNSCrypt query failure (e.g., timeout or error).
    """
    # Mock the encrypted query
    mock_query = MagicMock(spec=dns.message.Message)
    mock_query.to_wire.return_value = b'fake_query_wire'
    mock_encrypt_query.return_value = b'fake_encrypted_query'

    # Mock socket behavior to simulate a timeout
    mock_socket.recvfrom.side_effect = Exception("Timeout")

    # Instantiate the DNSCryptResolver and run the query
    resolver = DNSCryptResolver(server="1.1.1.1", port=853)

    # Run query and assert the exception
    with pytest.raises(DNSQueryError):
        resolver.query("example.com")

    mock_socket.sendto.assert_called_once_with(b'fake_encrypted_query', ('1.1.1.1', 853))


def test_invalid_response_format(mock_encrypt_query, mock_socket):
    """
    Test DNSCrypt query failure due to invalid response format.
    """
    # Mock the encrypted query
    mock_query = MagicMock(spec=dns.message.Message)
    mock_query.to_wire.return_value = b'fake_query_wire'
    mock_encrypt_query.return_value = b'fake_encrypted_query'

    # Mock socket behavior
    mock_socket.recvfrom.return_value = (b'invalid_response', 'fake_address')

    # Simulate DNS response parsing failure
    with patch("dns.message.from_wire", side_effect=Exception("Invalid DNS response")):
        # Instantiate the DNSCryptResolver and run the query
        resolver = DNSCryptResolver(server="1.1.1.1", port=853)

        # Run query and assert the exception
        with pytest.raises(DNSQueryError):
            resolver.query("example.com")

    mock_socket.sendto.assert_called_once_with(b'fake_encrypted_query', ('1.1.1.1', 853))


def test_encrypt_query():
    """
    Test the encryption of DNS query using NaCl.
    """
    # Mock DNS query message
    query = dns.message.make_query("example.com", "A")

    # Encrypt the query
    encrypted_query = encrypt_query(query)

    # Assertions
    assert isinstance(encrypted_query, bytes)
    assert len(encrypted_query) > 0
