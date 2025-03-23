import json
from typing import Optional, Callable, Union, Dict
import pika
import pika.frame
from pika.spec import PERSISTENT_DELIVERY_MODE, BasicProperties
import logging
from functools import wraps
import time
from .amqp_utils import construct_url
from .schemas import COMMON_SCHEMA
# Setup logger
logger = logging.getLogger(__name__)


def sync_reconnect_on_error(max_retries: int = 3, retry_delay: int = 2):
    """Decorator to handle reconnection on connection errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if not self.connection or self.connection.is_closed:
                        self.connect()
                    return func(self, *args, **kwargs)
                except (pika.exceptions.AMQPConnectionError, 
                       pika.exceptions.ConnectionClosedByBroker,
                       pika.exceptions.ChannelClosedByBroker,
                       pika.exceptions.ConnectionWrongStateError) as e:
                    retry_count += 1
                    logger.warning(f"Connection error in {func.__name__}: {str(e)}. Retrying {retry_count}/{max_retries}")
                    if retry_count >= max_retries:
                        logger.error(f"Failed to execute {func.__name__} after {max_retries} retries")
                        raise
                    time.sleep(retry_delay)
                    self.connect()
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    raise
        return wrapper
    return decorator


class SyncAMQPManager:
    """
    A robust synchronous AMQP (RabbitMQ) client that handles connection issues
    with automatic reconnection.
    """
    
    EXCHANGE_TYPES = {
        'direct': 'direct',
        'topic': 'topic',
        'fanout': 'fanout',
        'headers': 'headers',
        'x-lvc':'x-lvc'
    }
    
    def __init__(self, url: str, qos: Optional[int] = None, 
                heartbeat: Optional[int] = 60, 
                connection_attempts: Optional[int] = 3,
                retry_delay: Optional[int] = 5):
        """
        Initialize the SyncAMQPManager with connection URL
        
        :param url: RabbitMQ connection URL (e.g., amqp://guest:guest@localhost:5672/%2F)
        :param qos: Quality of service (prefetch count)
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
        self.params = pika.URLParameters(self.url)
        self.connection = None
        self.channel = None
        self.connect_counter = 0
        self.should_consume = True
        self.qos = qos
        self.is_connecting = False
        self._consumers = {}  # Track active consumers

    def connect(self, retry: bool = True) -> bool:
        """
        Establish connection to RabbitMQ server.
        
        :param retry: Whether to retry connection on failure
        :return: True if successful, False otherwise
        """
        if self.is_connecting:
            return True
            
        self.is_connecting = True
        try:
            logger.info(f"Connecting to RabbitMQ: {self.url}")
            
            # Close existing connection if any
            if self.connection and not self.connection.is_closed:
                try:
                    self.connection.close()
                except Exception:
                    pass
            
            # Attempt to connect
            attempt_count = 0
            while retry or attempt_count == 0:
                attempt_count += 1
                self.connect_counter += 1
                
                try:
                    self.connection = pika.BlockingConnection(self.params)
                    self.channel = self.connection.channel()
                    
                    # Set QoS if specified
                    if self.qos:
                        self.channel.basic_qos(prefetch_count=self.qos)
                    
                    # Reset counter on successful connection
                    self.connect_counter = 0
                    logger.info("Successfully connected to RabbitMQ")
                    return True
                except pika.exceptions.AMQPConnectionError as e:
                    if not retry or attempt_count >= 3:  # Limit attempts if retry is False
                        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                        raise
                    logger.warning(f"Connection attempt {attempt_count} failed: {str(e)}, retrying...")
                    time.sleep(5 if self.connect_counter > 1 else 1)
                
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            self.connection = None
            self.channel = None
            return False
        finally:
            self.is_connecting = False
    
    @sync_reconnect_on_error()
    def exchange_declare(self, exchange_name: str, exchange_type: str, 
                        durable: bool = True, auto_delete: bool = False, 
                        arguments: Dict = None, internal: bool = False) -> None:
        """
        Declare an exchange
        
        :param exchange_name: Name of the exchange to declare
        :param exchange_type: Type of exchange ('direct', 'topic', 'fanout', 'headers')
        :param durable: If True, exchange will survive broker restarts
        :param auto_delete: If True, exchange will be deleted when no queues are bound to it
        :param arguments: Additional arguments for exchange declaration
        :param internal: If True, exchange can't be directly published to by clients
        """
        if exchange_type not in self.EXCHANGE_TYPES:
            raise ValueError(f"Invalid exchange type: {exchange_type}. Must be one of {list(self.EXCHANGE_TYPES.keys())}")
            
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPES[exchange_type],
            durable=durable,
            auto_delete=auto_delete,
            internal=internal,
            arguments=arguments
        )
        logger.info(f"Exchange declared: {exchange_name} (type: {exchange_type})")

    @sync_reconnect_on_error()
    def queue_declare(self, queue_name: str, durable: bool = False, 
                     auto_delete: bool = False, exclusive: bool = False,
                     arguments: Dict = None) -> str:
        """
        Declare a queue
        
        :param queue_name: Name of the queue to declare
        :param durable: If True, queue will survive broker restarts
        :param auto_delete: If True, queue will be deleted when all consumers disconnect
        :param exclusive: If True, only this connection can use the queue
        :param arguments: Additional arguments for queue declaration
        :return: The queue name (useful for server-generated names when queue_name is empty)
        """
        result = self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments
        )
        logger.info(f"Queue declared: {result.method.queue}")
        return result.method.queue

    @sync_reconnect_on_error()
    def queue_bind(self, queue_name: str, exchange_name: str, routing_key: str, 
                  arguments: Dict = None) -> None:
        """
        Bind a queue to an exchange
        
        :param queue_name: Name of the queue to bind
        :param exchange_name: Name of the exchange to bind to
        :param routing_key: Routing key for the binding
        :param arguments: Additional arguments for binding
        """
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key,
            arguments=arguments
        )
        logger.info(f"Queue {queue_name} bound to exchange {exchange_name} with routing key {routing_key}")

    @sync_reconnect_on_error()
    def queue_unbind(self, queue_name: str, exchange_name: str, routing_key: str, 
                    arguments: Dict = None) -> None:
        """
        Unbind a queue from an exchange
        
        :param queue_name: Name of the queue to unbind
        :param exchange_name: Name of the exchange to unbind from
        :param routing_key: Routing key to unbind
        :param arguments: Additional arguments for unbinding
        """
        self.channel.queue_unbind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key,
            arguments=arguments
        )
        logger.info(f"Queue {queue_name} unbound from exchange {exchange_name} with routing key {routing_key}")

    @sync_reconnect_on_error()
    def publish(
        self,
        routing_key: str,
        message: str,
        exchange_name: str = "",
        content_type: str = "text/plain",
        delivery_mode: int = PERSISTENT_DELIVERY_MODE, 
        headers: Dict = None,
        priority: int = None,
        expiration: Union[int, str] = None,
        message_id: str = None,
        timestamp: int = None,
        correlation_id: str = None,
        max_retries: int = 5,
        retry_delay: int = 2,
    ) -> bool:
        """
        Publish a message to an exchange
        
        :param routing_key: Routing key for the message
        :param message: Message body (string)
        :param exchange_name: Name of the exchange to publish to
        :param content_type: Content type of the message
        :param delivery_mode: 1 for non-persistent, 2 for persistent
        :param headers: Message headers
        :param priority: Message priority
        :param expiration: Message expiration in milliseconds
        :param message_id: Message ID
        :param timestamp: Message timestamp
        :param correlation_id: Correlation ID for RPC
        :param max_retries: Maximum number of retries for publishing
        :return: True if publish was successful
        """
        properties = {}
        if content_type:
            properties['content_type'] = content_type
        if delivery_mode:
            properties['delivery_mode'] = delivery_mode
        if headers:
            properties['headers'] = headers
        if priority:
            properties['priority'] = priority
        if expiration:
            properties['expiration'] = str(expiration) if isinstance(expiration, int) else expiration
        if message_id:
            properties['message_id'] = message_id
        if timestamp:
            properties['timestamp'] = timestamp
        if correlation_id:
            properties['correlation_id'] = correlation_id

        retry_count = 0
        while retry_count <= max_retries:
            try:
                self.channel.basic_publish(
                    exchange=exchange_name,
                    routing_key=routing_key,
                    body=message.encode(),
                    properties=BasicProperties(**properties)
                )
                logger.debug(f"Published message to exchange {exchange_name} with routing key {routing_key}")
                return True
            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Failed to publish message after {max_retries} retries: {str(e)}")
                    raise
                logger.warning(f"Error publishing message (attempt {retry_count}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                # Reconnect and try again
                self.connect(retry=False)
        
        return False

    def consume(
        self,
        queue: str,
        callback: Callable,
        validate_common_schema: bool = False,
        auto_ack: bool = False,
        consumer_tag: str = None,
        arguments: Dict = None,
        exclusive: bool = False
    ) -> str:
        """
        Start consuming messages from a queue. This method will keep trying to reconnect
        if the connection is lost.
        
        :param queue: Name of the queue to consume from
        :param callback: Callback function to process messages
        :param validate_common_schema: Whether to validate message against common schema
        :param auto_ack: If True, messages are auto-acknowledged
        :param consumer_tag: Consumer tag to identify this consumer
        :param arguments: Additional arguments for the consume call
        :param exclusive: If True, only this consumer can access the queue
        :return: Consumer tag that identifies the consumer
        """
        self.should_consume = True
        
        # Wrap the callback to handle errors
        def wrapped_callback(ch, method, properties, body):
            try:
                if not validate_common_schema or self._is_valid_body(body):
                    callback(ch, method, properties, body)
            except Exception as e:
                logger.error(f"Error in consume callback: {str(e)}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        while self.should_consume:
            logger.info("Setting up consumer...")
            try:
                if self.channel is None or self.channel.is_closed:
                    self.connect()
                
                consumer_tag = self.channel.basic_consume(
                    queue=queue,
                    on_message_callback=wrapped_callback,
                    auto_ack=auto_ack,
                    exclusive=exclusive,
                    consumer_tag=consumer_tag,
                    arguments=arguments
                )
                
                self._consumers[consumer_tag] = queue
                logger.info(f"Started consuming from queue: {queue} with tag {consumer_tag}")
                
                try:
                    self.channel.start_consuming()
                except KeyboardInterrupt:
                    logger.info("Consumer interrupted by user")
                    self.stop_consuming(consumer_tag)
                    break
                
            except Exception as e:
                if not self.should_consume:
                    break
                logger.error(f"Error in consumer setup: {str(e)}")
                logger.info("Reconnecting...")
                time.sleep(5)  # Wait before reconnecting
        
        return consumer_tag

    @sync_reconnect_on_error()
    def stop_consuming(self, consumer_tag: str = None) -> None:
        """
        Stop consuming messages
        
        :param consumer_tag: Tag of the consumer to stop, or None to stop all consumers
        """
        self.should_consume = False
        if not self.channel:
            return
        self.channel.stop_consuming()
        # if consumer_tag:
        #     if consumer_tag in self._consumers:
        #         self.channel.basic_cancel(consumer_tag=consumer_tag)
        #         queue = self._consumers.pop(consumer_tag, "unknown")
        #         logger.info(f"Stopped consuming from queue {queue} with tag {consumer_tag}")
        # else:
        #     self.channel.basic_recover(requeue=True)  # Requeue unacknowledged messages
        #     self.channel.cancel()  # Cancel all consumers
        #     self._consumers.clear()
        #     logger.info("Stopped all consumers")

    def start_consuming(self) -> None:
        """
        Start the IO loop to process messages from all registered consumers
        This method blocks until stop_consuming is called from another thread
        """
        self.should_consume = True
        try:
            logger.info("Starting consumer IO loop")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer loop: {str(e)}")
            self.stop_consuming()
            
    @sync_reconnect_on_error()
    def get_message(self, queue_name: str, auto_ack: bool = False):
        """
        Get a single message from a queue without consuming
        
        :param queue_name: Name of the queue
        :param auto_ack: If True, message is automatically acknowledged
        :return: Tuple of (method, properties, body) or None if queue is empty
        """
        method, properties, body = self.channel.basic_get(
            queue=queue_name, 
            auto_ack=auto_ack
        )
        
        if method:
            logger.debug(f"Got message from queue {queue_name}")
            return method, properties, body
        
        return None
        
    @sync_reconnect_on_error()
    def ack(self, delivery_tag: int, multiple: bool = False) -> None:
        """
        Acknowledge a message
        
        :param delivery_tag: Delivery tag of the message to acknowledge
        :param multiple: If True, acknowledge all messages up to and including this one
        """
        self.channel.basic_ack(delivery_tag=delivery_tag, multiple=multiple)
    
    @sync_reconnect_on_error()
    def nack(self, delivery_tag: int, multiple: bool = False, requeue: bool = True) -> None:
        """
        Negative acknowledgment of a message
        
        :param delivery_tag: Delivery tag of the message
        :param multiple: If True, nack all messages up to and including this one
        :param requeue: If True, message will be returned to the queue
        """
        self.channel.basic_nack(
            delivery_tag=delivery_tag,
            multiple=multiple,
            requeue=requeue
        )
        
    @sync_reconnect_on_error()
    def reject(self, delivery_tag: int, requeue: bool = True) -> None:
        """
        Reject a message
        
        :param delivery_tag: Delivery tag of the message to reject
        :param requeue: If True, message will be returned to the queue
        """
        self.channel.basic_reject(delivery_tag=delivery_tag, requeue=requeue)
    
    @sync_reconnect_on_error()
    def queue_delete(self, queue_name: str, if_unused: bool = False, 
                    if_empty: bool = False) -> int:
        """
        Delete a queue
        
        :param queue_name: Name of the queue to delete
        :param if_unused: If True, queue is only deleted if it has no consumers
        :param if_empty: If True, queue is only deleted if it has no messages
        :return: The number of messages deleted with the queue
        """
        result = self.channel.queue_delete(
            queue=queue_name,
            if_unused=if_unused,
            if_empty=if_empty
        )
        logger.info(f"Queue deleted: {queue_name}")
        return result.message_count
    
    @sync_reconnect_on_error()
    def exchange_delete(self, exchange_name: str, if_unused: bool = False) -> None:
        """
        Delete an exchange
        
        :param exchange_name: Name of the exchange to delete
        :param if_unused: If True, exchange is only deleted if it has no bindings
        """
        self.channel.exchange_delete(
            exchange=exchange_name,
            if_unused=if_unused
        )
        logger.info(f"Exchange deleted: {exchange_name}")
    
    @sync_reconnect_on_error()
    def purge_queue(self, queue_name: str) -> int:
        """
        Purge all messages from a queue
        
        :param queue_name: Name of the queue to purge
        :return: The number of messages purged
        """
        result = self.channel.queue_purge(queue=queue_name)
        logger.info(f"Queue {queue_name} purged, removed {result.message_count} messages")
        return result.message_count
    
    def close(self) -> None:
        """
        Close the connection to RabbitMQ
        """
        self.should_consume = False
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
                logger.info("Channel closed")
                
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
                
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")
        finally:
            self.connection = None
            self.channel = None
            
    def _is_valid_body(self, body):
        # Convert body from bytes to string and then to a dictionary
        try:
            content = json.loads(body.decode())
        except json.JSONDecodeError:
            print(f"Invalid JSON received :: {body.decode()}")
            return False
        schema = COMMON_SCHEMA
        return self.validate_data(content, schema)