"""
Shared utility functions for AMQP connection management.
"""
import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

def construct_url(
    url: str,
    heartbeat: Optional[int] = None,
    connection_attempts: Optional[int] = None,
    retry_delay: Optional[int] = None,
) -> str:
    """
    Construct a URL with additional query parameters for RabbitMQ connection.
    
    :param url: Base RabbitMQ connection URL
    :param heartbeat: Heartbeat interval in seconds
    :param connection_attempts: Number of connection attempts
    :param retry_delay: Delay between connection attempts in seconds
    :return: Modified URL with additional parameters
    """
    url_parts = list(urlparse(url))
    query = dict(parse_qs(url_parts[4]))
    
    if heartbeat is not None:
        query.update({"heartbeat": heartbeat})
    if connection_attempts is not None:
        query.update({"connection_attempts": connection_attempts})
    if retry_delay is not None:
        query.update({"retry_delay": retry_delay})

    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

