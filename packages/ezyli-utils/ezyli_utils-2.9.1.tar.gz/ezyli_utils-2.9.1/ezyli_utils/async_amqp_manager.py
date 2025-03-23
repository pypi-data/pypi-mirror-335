from typing import Any, Optional, Callable, Union, Dict
import aio_pika
from aio_pika import RobustConnection, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractQueue, AbstractExchange
import asyncio
import logging
from functools import wraps
import json
from .amqp_utils import construct_url

from aiormq import AMQPConnectionError

# Setup logger
logger = logging.getLogger(__name__)


def async_reconnect_on_error(max_retries: int = 3, retry_delay: int = 2):
    """Decorator to handle reconnection on connection errors."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if not self.connection or self.connection.is_closed:
                        await self.connect()
                    return await func(self, *args, **kwargs)
                except (AMQPConnectionError, aio_pika.exceptions.ConnectionClosed, aio_pika.exceptions.ChannelClosed) as e:
                    retry_count += 1
                    logger.warning(f"Connection error in {func.__name__}: {str(e)}. Retrying {retry_count}/{max_retries}")
                    if retry_count >= max_retries:
                        logger.error(f"Failed to execute {func.__name__} after {max_retries} retries")
                        raise
                    await asyncio.sleep(retry_delay)
                    await self.connect()
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    raise
        return wrapper
    return decorator

class AsyncAMQPManager:
    def __init__(self, url: str, qos: Optional[int] = None, 
                heartbeat: Optional[int] = 60,
                connection_attempts: Optional[int] = 3,
                retry_delay: Optional[int] = 5):
        """ The class initializer.

        :param url: RabbitMQ connection URL (e.g., amqp://guest:guest@localhost:5672/%2F)
        :param qos: Quality of service - prefetch count for consumer
        :param heartbeat: Heartbeat interval in seconds
        :param connection_attempts: Number of connection attempts
        :param retry_delay: Delay between connection attempts in seconds
        """
        self.url = construct_url(
            url=url,
            heartbeat=heartbeat,
            connection_attempts=connection_attempts,
            retry_delay=retry_delay
        )
        logger.info(f"AMQP URL: {self.url}")
        self.channel = None
        self.connection: AbstractRobustConnection = None
        self.qos = qos
        self.is_connecting = False
        self.stop_event = None
        self.connect_counter = 0
        
    async def _on_connection_reconnected(self, connection: RobustConnection):
        """ Send a LinkUp message when the connection is reconnected.

        :param connection: RabbitMQ's robust connection instance.
        """
        self.connection = connection
        self.is_connecting = False
        logger.info("Connection to RabbitMQ reconnected")
        
    def _on_connection_closed(self, _: Any, exception: AMQPConnectionError):
        """ Handle unexpectedly closed connection events.

        :param _: Not used.
        :param exception: Connection exception
        """
        self.connection = None
        self.is_connecting = False
        logger.warning(f"Connection to RabbitMQ closed: {str(exception)}")
        
    async def connect(self, loop: Optional[asyncio.AbstractEventLoop] = None, retry: bool = True):
        """ Connects to RabbitMQ server.
        
        :param loop: Optional event loop to use
        :param retry: Whether to retry connection on failure
        :return: True if connection is successful, False otherwise
        """
        if self.is_connecting:
            return True

        self.is_connecting = True
        try:
            if not loop:
                loop = asyncio.get_running_loop()
            
            logger.info(f"Connecting to RabbitMQ: {self.url}")
            
            # Attempt to connect
            attempt_count = 0
            while retry or attempt_count == 0:
                attempt_count += 1
                self.connect_counter += 1
                
                try:
                    self.connection = await aio_pika.connect_robust(
                        url=self.url, 
                        loop=loop
                    )
                    self.connection.reconnect_callbacks.add(self._on_connection_reconnected)
                    self.connection.close_callbacks.add(self._on_connection_closed)
                    self.channel = await self.connection.channel()
                    
                    if self.qos:
                        await self.channel.set_qos(prefetch_count=self.qos)
                    
                    # Reset counter on successful connection
                    self.connect_counter = 0
                    logger.info("Successfully connected to RabbitMQ")
                    return True
                    
                except AMQPConnectionError as e:
                    if not retry or attempt_count >= 3:  # Limit attempts if retry is False
                        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                        raise
                    logger.warning(f"Connection attempt {attempt_count} failed: {str(e)}, retrying...")
                    await asyncio.sleep(5 if self.connect_counter > 1 else 1)
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            self.connection = None
            self.channel = None
            return False
        finally:
            self.is_connecting = False
        
    @async_reconnect_on_error(max_retries=3)
    async def publish(self, routing_key: str, message: str, exchange_name: str = "", 
                     content_type: str = None, delivery_mode: int = 2, headers: Dict = None,
                     priority: int = None, expiration: Union[int, str] = None,
                     message_id: str = None, timestamp: int = None,
                     correlation_id: str = None,
                     max_retries: int = 5,
                     retry_delay: int = 2,):
        """ Publishes a message to a RabbitMQ exchange.

        :param routing_key: Message routing key.
        :param message: Message to be sent.
        :param exchange_name: Exchange name.
        :param content_type: Message content type.
        :param delivery_mode: Message delivery mode (1=non-persistent, 2=persistent).
        :param headers: Message headers.
        :param priority: Message priority.
        :param expiration: Message expiration in seconds or as string.
        :param message_id: Message identifier.
        :param timestamp: Message timestamp.
        :param max_retries: Maximum number of retries for publishing
        """
        exchange = await self.channel.get_exchange(exchange_name, ensure=False)
        
        message_properties = {}
        if content_type:
            message_properties['content_type'] = content_type
        if delivery_mode:
            message_properties['delivery_mode'] = delivery_mode
        if headers:
            message_properties['headers'] = headers
        if priority:
            message_properties['priority'] = priority
        if expiration:
            message_properties['expiration'] = str(expiration) if isinstance(expiration, int) else expiration
        if message_id:
            message_properties['message_id'] = message_id
        if timestamp:
            message_properties['timestamp'] = timestamp
        if correlation_id:
            message_properties['correlation_id'] = correlation_id

        # Using explicit retry logic for publish operation
        retry_count = 0
        last_exception = None
        
        while retry_count <= max_retries:
            try:
                await exchange.publish(
                    aio_pika.Message(
                        body=message.encode(),
                        **message_properties
                    ),
                    routing_key=routing_key
                )
                logger.debug(f"Published message to exchange {exchange_name} with routing key {routing_key}")
                return True
            except (AMQPConnectionError, aio_pika.exceptions.ConnectionClosed) as e:
                retry_count += 1
                last_exception = e
                if retry_count > max_retries:
                    logger.error(f"Failed to publish message after {max_retries} retries: {str(e)}")
                    raise last_exception
                logger.warning(f"Error publishing message (attempt {retry_count}/{max_retries}): {str(e)}")
                await asyncio.sleep(retry_delay)
                # Reconnect and try again
                await self.connect(retry=False)
        
        raise last_exception

    def _decode_message_body(self, message: aio_pika.IncomingMessage) -> Any:
        """
        Decode message body based on content type
        
        :param message: The incoming message to decode
        :return: Decoded message content
        """
        content_type = message.content_type
        body = message.body
        
        if (content_type == 'application/json'):
            try:
                return json.loads(body.decode())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON message: {e}")
                return body
        elif content_type and content_type.startswith('text/'):
            return body.decode()
        else:
            # Return raw bytes for binary content
            return body

    async def consume(
        self,
        queue: str,
        callback: Callable,
        validate_common_schema: bool = False,
        auto_ack: bool = False,
        consumer_tag: str = None,
        arguments: Dict = None,
        exclusive: bool = False,
        decode_message: bool = True
    ):
        """
        Start consuming messages from a queue. This method will keep trying to reconnect
        if the connection is lost.
        
        :param queue: The name of the queue to consume messages from
        :param callback: Callback function to process messages
        :param validate_common_schema: Whether to validate message against common schema
        :param auto_ack: A boolean indicating whether to automatically acknowledge the message
        :param consumer_tag: Consumer identifier tag
        :param arguments: Additional arguments for consume method
        :param exclusive: If True, only this consumer can access the queue
        :param decode_message: If True, message body will be decoded based on content type before passing to callback
        """
        # Create a wrapper callback that can handle schema validation if needed
        async def wrapped_callback(message):
            try:
                if validate_common_schema:
                    # Add schema validation here if needed
                    pass
                
                if decode_message:
                    # Decode message body before passing to callback
                    decoded_content = self._decode_message_body(message)
                    await callback(message, decoded_content)
                else:
                    # Pass the raw message to callback
                    await callback(message)
            except Exception as e:
                logger.error(f"Error in consume callback: {str(e)}")
                if not auto_ack:
                    await message.nack(requeue=True)
        
        self.stop_event = asyncio.Event()
        
        # Keep trying to consume until stopped
        while not self.stop_event.is_set():
            try:
                if not self.connection or self.connection.is_closed:
                    await self.connect()
                
                queue_obj: AbstractQueue = await self.channel.get_queue(queue, ensure=False)
                
                # Start consuming
                consumer_tag = await queue_obj.consume(
                    callback=wrapped_callback, 
                    no_ack=auto_ack, 
                    consumer_tag=consumer_tag,
                    arguments=arguments,
                    exclusive=exclusive
                )
                
                logger.info(f"Started consuming from queue: {queue}")
                
                # Wait until stop_event is set or connection is lost
                try:
                    # Wait until stop_event is set or connection is lost
                    await self.stop_event.wait()
                except KeyboardInterrupt:
                    logger.info("Consumer interrupted by user")
                    self.stop_consuming(queue, consumer_tag)
                    break
                
            except Exception as e:
                if self.stop_event.is_set():
                    break
                logger.error(f"Error in consumer setup: {str(e)}")
                logger.info("Reconnecting...")
                await asyncio.sleep(5)  # Wait before reconnecting
    
    @async_reconnect_on_error()
    async def stop_consuming(self, queue: str, consumer_tag: Any):
        """
        This method helps to stop consuming messages from a queue
        
        :param queue: Queue name
        :param consumer_tag: Consumer identifier
        """
        if self.stop_event:
            self.stop_event.set()
            
        if self.channel and not self.channel.is_closed:
            try:
                queue_obj: AbstractQueue = await self.channel.get_queue(queue, ensure=False)
                await queue_obj.cancel(consumer_tag=consumer_tag)
                logger.info(f"Stopped consuming from queue {queue} with consumer_tag {consumer_tag}")
            except Exception as e:
                logger.error(f"Error stopping consumer: {str(e)}")

    @async_reconnect_on_error()
    async def exchange_declare(self, exchange_name: str, exchange_type: ExchangeType, 
                              durable: bool = True, auto_delete: bool = False, 
                              arguments: Dict = None, internal: bool = False) -> AbstractExchange:
        """
        This method helps to declare an exchange
        
        :param exchange_name: The name of the exchange to declare
        :param exchange_type: The type of the exchange
        :param durable: A boolean indicating whether the exchange is durable
        :param auto_delete: A boolean indicating whether the exchange is auto delete
        :param arguments: Additional arguments for the exchange
        :param internal: If True, the exchange can't be directly published to by clients
        :return: Exchange object
        """
        exchange = await self.channel.declare_exchange(
            name=exchange_name,
            auto_delete=auto_delete,
            durable=durable,
            type=exchange_type,
            arguments=arguments,
            internal=internal
        )
        logger.info(f"Exchange declared: {exchange_name} (type: {exchange_type})")
        return exchange
    
    @async_reconnect_on_error()
    async def queue_declare(self, queue_name: str, durable: bool = False, auto_delete: bool = False,
                           arguments: Dict = None, exclusive: bool = False) -> AbstractQueue:
        """
        This method helps to declare a queue
        
        :param queue_name: The name of the queue to declare
        :param durable: A boolean indicating whether the queue is durable
        :param auto_delete: A boolean indicating whether the queue is auto delete
        :param arguments: Additional arguments for the queue
        :param exclusive: If True, only this connection can access the queue
        :return: Queue object
        """
        queue = await self.channel.declare_queue(
            name=queue_name,
            auto_delete=auto_delete,
            durable=durable,
            arguments=arguments,
            exclusive=exclusive
        )
        logger.info(f"Queue declared: {queue_name}")
        return queue
    
    @async_reconnect_on_error()
    async def queue_bind(self, queue_name: str, exchange_name: str, routing_key: str, arguments: Dict = None):
        """
        This method helps to bind a queue to an exchange
        
        :param queue_name: The name of the queue to bind
        :param exchange_name: The name of the exchange to bind to
        :param routing_key: The routing key to use
        :param arguments: The arguments to use
        """
        queue: AbstractQueue = await self.channel.get_queue(queue_name, ensure=False)
        exchange = await self.channel.get_exchange(exchange_name, ensure=False)
        
        await queue.bind(
            arguments=arguments,
            exchange=exchange,
            routing_key=routing_key
        )
        logger.info(f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}")
    
    @async_reconnect_on_error()
    async def queue_unbind(self, queue_name: str, exchange_name: str, routing_key: str, arguments: Dict = None):
        """
        This method helps to unbind a queue from an exchange
        
        :param queue_name: The name of the queue to unbind
        :param exchange_name: The name of the exchange to unbind from
        :param routing_key: The routing key to use
        :param arguments: The arguments to use
        """
        queue: AbstractQueue = await self.channel.get_queue(queue_name, ensure=False)
        exchange = await self.channel.get_exchange(exchange_name, ensure=False)
        
        await queue.unbind(
            arguments=arguments,
            exchange=exchange,
            routing_key=routing_key
        )
        logger.info(f"Queue {queue_name} unbound from exchange {exchange_name} with routing key {routing_key}")

    @async_reconnect_on_error()
    async def queue_delete(self, queue_name: str, if_unused: bool = False, if_empty: bool = False):
        """
        Delete a queue
        
        :param queue_name: Name of the queue to delete
        :param if_unused: Only delete if the queue has no consumers
        :param if_empty: Only delete if the queue is empty
        """
        queue: AbstractQueue = await self.channel.get_queue(queue_name, ensure=False)
        await queue.delete(if_unused=if_unused, if_empty=if_empty)
        logger.info(f"Queue deleted: {queue_name}")

    @async_reconnect_on_error()
    async def exchange_delete(self, exchange_name: str, if_unused: bool = False):
        """
        Delete an exchange
        
        :param exchange_name: Name of the exchange to delete
        :param if_unused: Only delete if the exchange has no bindings
        """
        exchange = await self.channel.get_exchange(exchange_name, ensure=False)
        await exchange.delete(if_unused=if_unused)
        logger.info(f"Exchange deleted: {exchange_name}")

    @async_reconnect_on_error()
    async def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue
        
        :param queue_name: Name of the queue to purge
        :return: Number of messages purged
        """
        queue: AbstractQueue = await self.channel.get_queue(queue_name, ensure=False)
        purge_count = await queue.purge()
        logger.info(f"Queue {queue_name} purged, removed {purge_count} messages")
        return purge_count

    @async_reconnect_on_error()
    async def get_message(self, queue_name: str, no_ack: bool = False):
        """
        Get a single message from a queue without consuming
        
        :param queue_name: Name of the queue to get a message from
        :param no_ack: If True, automatic acknowledgment is sent
        :return: The message or None if queue is empty
        """
        queue: AbstractQueue = await self.channel.get_queue(queue_name, ensure=False)
        message = await queue.get(no_ack=no_ack)
        if message:
            logger.debug(f"Got message from queue {queue_name}")
        return message

    async def close(self):
        """ Closes the connection to RabbitMQ server.
        """
        if self.connection:
            try:
                # Make sure to cancel any ongoing consume operations
                if self.stop_event:
                    self.stop_event.set()
                    
                await self.connection.close()
                logger.info("RabbitMQ connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.connection = None
                self.channel = None
        else:
            logger.warning("Connection is not established")



