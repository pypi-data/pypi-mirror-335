import asyncio
import ssl
import dns.message
import dns.query
import httpx
from cachetools import TTLCache
from abc import ABC, abstractmethod
from .exceptions import DNSQueryError
from .logging import logger

class DNSProtocolHandler(ABC):
    """
    Abstract base class for DNS protocol handlers.

    This class defines the interface that all DNS protocol handlers must implement.
    Each concrete implementation handles a specific DNS protocol (DoH, DoT, mTLS).

    Attributes:
        None
    """

    @abstractmethod
    async def query(self, domain: str, record_type: str, cache, retries: int):
        """
        Execute a DNS query using the specific protocol.

        Args:
            domain (str): The domain name to query.
            record_type (str): The DNS record type (e.g., 'A', 'AAAA', 'MX').
            cache (TTLCache): Cache object for storing query results.
            retries (int): Number of retry attempts for failed queries.

        Returns:
            list: DNS answer records from the response.

        Raises:
            DNSQueryError: If the query fails after all retry attempts.
        """
        pass

class DoHHandler(DNSProtocolHandler):
    """
    Handler for DNS over HTTPS (DoH) protocol.

    This class implements the DNS over HTTPS protocol, which encrypts DNS queries
    using the HTTPS protocol for enhanced privacy and security.

    Attributes:
        server (str): The URL of the DoH server.
    """

    def __init__(self, server: str):
        """
        Initialize the DoH handler with a server URL.

        Args:
            server (str): The URL of the DoH server (e.g., 'https://dns.google/dns-query').
        """
        self.server = server

    async def query(self, domain: str, record_type: str, cache, retries: int):
        """
        Execute a DNS over an HTTPS query.

        This method sends a DNS query over HTTPS to the configured server,
        with support for caching and automatic retries.

        Args:
            domain (str): The domain name to query.
            record_type (str): The DNS record type (e.g., 'A', 'AAAA', 'MX').
            cache (TTLCache): Cache object for storing query results.
            retries (int): Number of retry attempts for failed queries.

        Returns:
            list: DNS answer records from the response.

        Raises:
            DNSQueryError: If the query fails after all retry attempts.
        """
        cache_key = f"doh:{domain}:{record_type}"
        if cache_key in cache:
            logger.info(f"Cache hit for {cache_key}")
            return cache[cache_key]

        logger.debug(f"DoH query for {domain} ({record_type}) to server {self.server}")
        query = dns.message.make_query(domain, record_type)
        logger.debug(f"Created DNS query message with ID: {query.id}")

        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"DoH attempt {attempt}/{retries} for {domain}")
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.server,
                        data=query.to_wire(),
                        headers={"Content-Type": "application/dns-message"},
                    )
                    logger.debug(f"DoH response status: {response.status_code}")

                    if response.status_code == 200:
                        dns_response = dns.message.from_wire(response.content)
                        logger.debug(f"DoH response parsed successfully, answer records: {len(dns_response.answer)}")
                        cache[cache_key] = dns_response.answer
                        return dns_response.answer

                    logger.warning(f"DoH query failed with status {response.status_code} (attempt {attempt})")
            except Exception as e:
                logger.error(f"DoH query error on attempt {attempt}: {e}")
                logger.debug(f"Exception details: {type(e).__name__}", exc_info=True)

        logger.error(f"All DoH query attempts failed for {domain}")
        raise DNSQueryError(f"Failed DoH query after {retries} attempts")

class DoTHandler(DNSProtocolHandler):
    """
    Handler for DNS over TLS (DoT) protocol.

    This class implements the DNS over TLS protocol, which encrypts DNS queries
    using TLS for enhanced privacy and security.

    Attributes:
        server (str): The hostname or IP address of the DoT server.
        port (int): The port number for the DoT server (typically 853).
    """

    def __init__(self, server: str, port: int):
        """
        Initialize the DoT handler with server address and port.

        Args:
            server (str): The hostname or IP address of the DoT server.
            port (int): The port number for the DoT server (typically 853).
        """
        self.server = server
        self.port = port

    async def query(self, domain: str, record_type: str, cache, retries: int):
        """
        Execute a DNS over TLS query.

        This method sends a DNS query over TLS to the configured server,
        with support for caching and automatic retries.

        Args:
            domain (str): The domain name to query.
            record_type (str): The DNS record type (e.g., 'A', 'AAAA', 'MX').
            cache (TTLCache): Cache object for storing query results.
            retries (int): Number of retry attempts for failed queries.

        Returns:
            list: DNS answer records from the response.

        Raises:
            DNSQueryError: If the query fails after all retry attempts.
        """
        cache_key = f"dot:{domain}:{record_type}"
        if cache_key in cache:
            logger.info(f"Cache hit for {cache_key}")
            return cache[cache_key]

        query = dns.message.make_query(domain, record_type)
        ssl_context = ssl.create_default_context()

        logger.debug(f"Attempting DoT query to {self.server}:{self.port} for {domain} ({record_type})")
        logger.debug(f"Created DNS query message with ID: {query.id}")

        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"DoT attempt {attempt}/{retries} for {domain}")
                response = await asyncio.to_thread(
                    dns.query.tls, query, self.server, port=self.port,
                    ssl_context=ssl_context, server_hostname=self.server
                )
                logger.debug(f"DoT query successful, answer records: {len(response.answer)}")
                cache[cache_key] = response.answer
                return response.answer
            except Exception as e:
                logger.error(f"DoT query error on attempt {attempt}: {e}")
                logger.debug(f"Exception details: {type(e).__name__}", exc_info=True)

        logger.error(f"All DoT query attempts failed for {domain}")
        raise DNSQueryError(f"Failed DoT query after {retries} attempts")

class MTLSHandler(DNSProtocolHandler):
    """
    Handler for DNS over mutual TLS (mTLS) protocol.

    This class implements DNS queries over mutual TLS, which provides
    two-way authentication between client and server for enhanced security.

    Attributes:
        server (str): The hostname or IP address of the mTLS server.
        certfile (str): Path to the client certificate file.
        keyfile (str): Path to the client private key file.
    """

    def __init__(self, server: str, certfile: str, keyfile: str):
        """
        Initialize the mTLS handler with server address and certificate information.

        Args:
            server (str): The hostname or IP address of the mTLS server.
            certfile (str): Path to the client certificate file.
            keyfile (str): Path to the client private key file.
        """
        self.server = server
        self.certfile = certfile
        self.keyfile = keyfile

    async def query(self, domain: str, record_type: str, cache, retries: int):
        """
        Execute a DNS query over mutual TLS.

        This method sends a DNS query over mutual TLS to the configured server,
        with support for caching and automatic retries.

        Args:
            domain (str): The domain name to query.
            record_type (str): The DNS record type (e.g., 'A', 'AAAA', 'MX').
            cache (TTLCache): Cache object for storing query results.
            retries (int): Number of retry attempts for failed queries.

        Returns:
            list: DNS answer records from the response.

        Raises:
            ValueError: If any required mTLS parameters are missing.
            DNSQueryError: If the query fails after all retry attempts.
        """
        if not all([self.server, self.certfile, self.keyfile]):
            raise ValueError("mTLS requires server, certfile, and keyfile parameters")

        cache_key = f"mtls:{domain}:{record_type}"
        if cache_key in cache:
            logger.info(f"Cache hit for {cache_key}")
            return cache[cache_key]

        query = dns.message.make_query(domain, record_type)

        # Create SSL context with client certificate authentication
        ssl_context = ssl.create_default_context()
        ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        for attempt in range(1, retries + 1):
            try:
                # Use asyncio.to_thread to run the blocking DNS query in a separate thread
                response = await asyncio.to_thread(
                    dns.query.tls, query, self.server, 853, ssl_context
                )

                if response and response.answer:
                    cache[cache_key] = response.answer
                    logger.info(f"mTLS query success for {domain} (attempt {attempt})")
                    return response.answer
                logger.warning(f"mTLS query returned empty response for {domain} (attempt {attempt})")

            except Exception as e:
                logger.error(f"mTLS query error: {e} (attempt {attempt})")

        raise DNSQueryError(f"Failed mTLS query after {retries} attempts")

class DNSResolver:
    """
    A resolver for querying DNS records over secure protocols.

    This class provides a unified interface for resolving DNS queries over
    various secure protocols including DNS over HTTPS (DoH), DNS over TLS (DoT),
    and mutual TLS (mTLS). It supports caching, automatic retries, and both
    synchronous and asynchronous operation modes.

    Attributes:
        cache (TTLCache): Cache for storing DNS responses with time-to-live expiration.
        retries (int): Number of retry attempts for failed queries.
        handlers (dict): Dictionary mapping protocol names to handler instances.
    """

    def __init__(self,
                 doh_server="https://dns.google/dns-query",
                 dot_server="1.1.1.1", dot_port=853,
                 mtls_server=None, certfile=None, keyfile=None,
                 cache_size=100, cache_ttl=300, retries=3):
        """
        Initialize the DNS resolver with the provided configuration.

        Args:
            doh_server (str): The URL of the DoH server.
                Default: "https://dns.google/dns-query"
            dot_server (str): The hostname or IP address of the DoT server.
                Default: "1.1.1.1"
            dot_port (int): The port number for the DoT server.
                Default: 853
            mtls_server (str, optional): The hostname or IP address of the mTLS server.
                Default: None
            certfile (str, optional): Path to the client certificate file for mTLS.
                Default: None
            keyfile (str, optional): Path to the client private key file for mTLS.
                Default: None
            cache_size (int): Maximum number of entries in the cache.
                Default: 100
            cache_ttl (int): Time-to-live for cache entries in seconds.
                Default: 300
            retries (int): Number of retry attempts for failed queries.
                Default: 3
        """
        # Cache for storing DNS responses (TTL-based)
        self.cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        self.retries = retries

        logger.debug(f"Initializing DNSResolver with cache_size={cache_size}, cache_ttl={cache_ttl}, retries={retries}")
        logger.debug(f"DoH server: {doh_server}")
        logger.debug(f"DoT server: {dot_server}:{dot_port}")

        # Initialize protocol handlers
        self.handlers = {
            "doh": DoHHandler(doh_server),
            "dot": DoTHandler(dot_server, dot_port)
        }

        # Only add mTLS handler if all required parameters are provided
        if all([mtls_server, certfile, keyfile]):
            logger.debug(f"mTLS server: {mtls_server}, certfile: {certfile}, keyfile: {keyfile}")
            self.handlers["mtls"] = MTLSHandler(mtls_server, certfile, keyfile)
        else:
            logger.debug("mTLS not configured (missing server, certfile, or keyfile)")

    async def query(self, domain: str, record_type: str = "A", protocol: str = "doh") -> list:
        """
        Resolve a DNS query using the specified protocol.

        This method delegates the DNS query to the appropriate protocol handler,
        with support for caching and automatic retries.

        Args:
            domain (str): The domain name to query.
            record_type (str, optional): The DNS record type (e.g., 'A', 'AAAA', 'MX').
                Default: "A"
            protocol (str, optional): The DNS protocol to use ('doh', 'dot', 'mtls').
                Default: "doh"

        Returns:
            list: DNS answer records from the response.

        Raises:
            ValueError: If an invalid protocol is specified.
            DNSQueryError: If the DNS query fails after all retry attempts.
        """
        logger.info(f"Resolving {domain} ({record_type}) using {protocol}")

        if protocol not in self.handlers:
            available_protocols = ", ".join(self.handlers.keys())
            logger.error(f"Invalid protocol: {protocol}. Available protocols: {available_protocols}")
            raise ValueError(f"Invalid protocol. Choose from: {available_protocols}")

        handler = self.handlers[protocol]
        logger.debug(f"Using handler: {handler.__class__.__name__}")

        try:
            result = await handler.query(domain, record_type, self.cache, self.retries)
            logger.debug(f"Query successful for {domain}, returned {len(result)} records")
            return result
        except Exception as e:
            logger.error(f"Query failed for {domain}: {e}")
            logger.debug("Exception details:", exc_info=True)
            raise


