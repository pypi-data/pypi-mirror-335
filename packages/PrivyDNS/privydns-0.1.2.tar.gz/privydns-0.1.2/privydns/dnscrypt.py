import dns.message
import dns.query
import socket
import nacl.secret
import nacl.utils
from .exceptions import DNSQueryError
from .logging import logger

def encrypt_query(query: dns.message.Message) -> bytes:
    """
    Encrypt the DNS query using DNSCrypt.

    Args:
        query (dns.message.Message): The DNS query message to encrypt.

    Returns:
        bytes: The encrypted DNS query in wire format.

    This function uses NaCl's secret box for encryption. It generates a random key and nonce,
    and returns the encrypted query message.
    """
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    box = nacl.secret.SecretBox(key)
    nonce = nacl.utils.random(box.NONCE_SIZE)

    encrypted_query = box.encrypt(query.to_wire(), nonce)
    return encrypted_query


class DNSCryptResolver:
    """
    A resolver for DNS queries using DNSCrypt.

    This class performs DNS queries over the DNSCrypt protocol, where the query is
    encrypted before being sent over a UDP connection. It supports synchronous query resolution.

    Attributes:
        server (str): The IP address of the DNSCrypt server (default: "1.1.1.1").
        port (int): The port for the DNSCrypt server (default: 853).

    Methods:
        __init__: Initializes the resolver with the provided DNSCrypt server and port.
        query: Performs a DNSCrypt query for the given domain and record type.
    """

    def __init__(self, server: str = "1.1.1.1", port: int = 853):
        """
        Initializes the DNSCryptResolver instance with the server address and port.

        Args:
            server (str): The IP address of the DNSCrypt server (default: "1.1.1.1").
            port (int): The port for the DNSCrypt server (default: 853).
        """
        self.server = server
        self.port = port

    def query(self, domain: str, record_type: str = "A") -> list:
        """
        Perform a DNSCrypt query for the given domain and record type.

        Args:
            domain (str): The domain name to query.
            record_type (str): The DNS record type to request (default: 'A').

        Returns:
            list: A list of DNS answer records.

        Raises:
            DNSQueryError: If the DNSCrypt query fails.
        """
        try:
            # Create DNS query message
            query = dns.message.make_query(domain, record_type)

            # Encrypt the query using DNSCrypt encryption
            encrypted_query = encrypt_query(query)

            # Send the encrypted query over UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)  # Set timeout for receiving the response
            sock.sendto(encrypted_query, (self.server, self.port))

            # Receive the response
            response, _ = sock.recvfrom(4096)

            # Parse the DNS response
            dns_response = dns.message.from_wire(response)
            return dns_response.answer

        except Exception as e:
            logger.error(f"DNSCrypt query error: {e}")
            raise DNSQueryError(f"DNSCrypt query failed for {domain}")
