import pytest
from unittest.mock import patch, MagicMock

from cachetools import TTLCache

from privydns.resolver import DNSResolver, DoHHandler, DoTHandler, MTLSHandler

@pytest.fixture(scope="function")
def resolver():
    """Fixture to create a DNSResolver instance for testing."""
    return DNSResolver()

@pytest.mark.asyncio
async def test_doh(resolver):
    """Test asynchronous DNS over an HTTPS query."""
    response = await resolver.query("example.com", protocol="doh")
    assert response is not None
    assert len(response) > 0

@pytest.mark.asyncio
@patch('privydns.resolver.dns.query.tls')
async def test_dot(mock_tls_query, resolver):
    """Test asynchronous DNS over a TLS query."""

    # Mock the TLS query to return a mock response
    mock_response = MagicMock()
    mock_response.answer = ["mock_answer"]
    mock_tls_query.return_value = mock_response

    # Run the query and assert the response
    response = await resolver.query("example.com", protocol="dot")
    assert response == ["mock_answer"]

@pytest.mark.asyncio
async def test_invalid_protocol(resolver):
    """Test that an invalid protocol raises a ValueError."""
    with pytest.raises(ValueError):
        await resolver.query("example.com", protocol="invalid")

@pytest.mark.asyncio
async def test_doh_handler_cache():
    """Test that the DoH handler uses cache correctly."""
    # Create a TTLCache with a predefined hit
    mock_cache = TTLCache(maxsize=100, ttl=300)
    mock_cache["doh:example.com:A"] = ["mock_answer"]

    # Create handler with the mock cache
    handler = DoHHandler("https://dns.google/dns-query")

    # Test cache hit
    result = await handler.query("example.com", "A", mock_cache, 3)
    assert result == ["mock_answer"]

@pytest.mark.asyncio
async def test_dot_handler_cache():
    """Test that the DoT handler uses cache correctly."""
    # Create a TTLCache with a predefined hit
    mock_cache = TTLCache(maxsize=100, ttl=300)
    mock_cache["dot:example.com:A"] = ["mock_answer"]

    # Create handler with the mock cache
    handler = DoTHandler("1.1.1.1", 853)

    # Test cache hit
    result = await handler.query("example.com", "A", mock_cache, 3)
    assert result == ["mock_answer"]

@pytest.mark.asyncio
async def test_mtls_missing_parameters():
    """Test that MTLSHandler raises ValueError when parameters are missing."""
    # Create a TTLCache
    mock_cache = TTLCache(maxsize=100, ttl=300)

    # Create handler with missing parameters
    handler = MTLSHandler("server.example.com", None, None)

    # Test that ValueError is raised
    with pytest.raises(ValueError):
        await handler.query("example.com", "A", mock_cache, 3)

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
async def test_doh_handler_retry(mock_client):
    """Test that DoH handler retries on failure."""
    # Create a TTLCache
    mock_cache = TTLCache(maxsize=100, ttl=300)

    # Setup mock client to fail twice then succeed
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'mock_dns_response'

    mock_client_instance = MagicMock()
    mock_client_instance.__aenter__.return_value.post.side_effect = [
        Exception("Connection error"),  # First attempt fails
        Exception("Timeout"),           # Second attempt fails
        mock_response                   # Third attempt succeeds
    ]
    mock_client.return_value = mock_client_instance

    # Mock dns.message.from_wire
    with patch('dns.message.from_wire') as mock_from_wire:
        mock_dns_response = MagicMock()
        mock_dns_response.answer = ["mock_answer"]
        mock_from_wire.return_value = mock_dns_response

        # Create handler and test
        handler = DoHHandler("https://dns.google/dns-query")
        result = await handler.query("example.com", "A", mock_cache, 3)

        # Verify the result and that post was called 3 times
        assert result == ["mock_answer"]
        assert mock_client_instance.__aenter__.return_value.post.call_count == 3

@pytest.mark.asyncio
@patch('privydns.resolver.dns.query.tls')
async def test_dot_handler_retry(mock_to_thread):
    """Test that DoT handler retries on failure."""

    # Create a TTLCache
    mock_cache = TTLCache(maxsize=100, ttl=300)

    # Setup mocks to fail twice then succeed
    mock_response = MagicMock()
    mock_response.answer = ["mock_answer"]

    mock_to_thread.side_effect = [
        Exception("Connection error"),  # First attempt fails
        Exception("Timeout"),           # Second attempt fails
        mock_response                   # Third attempt succeeds
    ]

    # Create handler and test
    handler = DoTHandler("1.1.1.1", 853)
    result = await handler.query("example.com", "A", mock_cache, 3)

    # Verify the result and that to_thread was called 3 times
    assert result == ["mock_answer"]
    assert mock_to_thread.call_count == 3

def test_resolver_initialization():
    """Test that DNSResolver initializes handlers correctly."""
    # Test with default parameters
    resolver = DNSResolver()
    assert "doh" in resolver.handlers
    assert "dot" in resolver.handlers
    assert "mtls" not in resolver.handlers

    # Test with mTLS parameters
    resolver = DNSResolver(
        mtls_server="mtls.example.com",
        certfile="/path/to/cert.pem",
        keyfile="/path/to/key.pem"
    )
    assert "mtls" in resolver.handlers
