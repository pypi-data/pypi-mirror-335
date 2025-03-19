import asyncio
from typing import Optional, Dict, AsyncIterator
import aio_pika
import random
from dataclasses import dataclass
import time
from contextlib import asynccontextmanager
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    AsyncRetrying
)

from kal_utils.event_messaging.core.logging import logger

@dataclass
class ConnectionConfig:
    """Configuration for RabbitMQ connection settings."""
    pool_size: int = 5
    connection_timeout: float = 30.0  # seconds
    idle_timeout: float = 300.0  # seconds
    max_retries: int = 5  # For connection attempts
    retry_multiplier: float = 1.0  # For exponential backoff
    retry_max_wait: float = 60.0  # Max wait between retries in seconds

class RabbitMQConnectionManager:
    """
    Manages a pool of RabbitMQ connections with retry logic and connection health monitoring.
    
    Features:
    - Connection pooling with configurable pool size
    - Exponential backoff retry mechanism
    - Connection health monitoring
    - Automatic connection cleanup
    - Connection reuse optimization
    """
    
    def __init__(self, connection_url: str, config: Optional[ConnectionConfig] = None):
        self.connection_url = connection_url
        self.config = config or ConnectionConfig()
        self.connection_pool: Dict[str, tuple[aio_pika.Connection, float, bool]] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Initialize the connection manager and start background tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("RabbitMQ connection manager started")

    async def stop(self):
        """Gracefully shut down all connections and cleanup tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            for conn_id, (connection, _, _) in self.connection_pool.items():
                if not connection.is_closed:
                    await connection.close()
            self.connection_pool.clear()
        
        logger.info("RabbitMQ connection manager stopped")

    async def _create_connection(self) -> aio_pika.Connection:
        """Create a new connection with retry logic."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=self.config.retry_multiplier,
                max=self.config.retry_max_wait
            ),
            retry=retry_if_exception_type(
                (aio_pika.exceptions.AMQPConnectionError, asyncio.TimeoutError)
            )
        ):
            with attempt:
                try:
                    connection = await asyncio.wait_for(
                        aio_pika.connect_robust(self.connection_url),
                        timeout=self.config.connection_timeout
                    )
                    logger.info("Successfully established RabbitMQ connection")
                    return connection
                except Exception as e:
                    logger.error(f"Connection attempt failed: {str(e)}")
                    raise

    async def _get_available_connection(self) -> tuple[str, aio_pika.Connection]:
        """Get an available connection from the pool or create a new one."""
        async with self._lock:
            # Clean up closed connections first
            closed_ids = [
                conn_id for conn_id, (conn, _, _) in self.connection_pool.items()
                if conn.is_closed
            ]
            for conn_id in closed_ids:
                await self.connection_pool[conn_id][0].close()
                del self.connection_pool[conn_id]

            # Try to find an existing idle connection
            for conn_id, (connection, last_used, in_use) in self.connection_pool.items():
                if not in_use and not connection.is_closed:
                    self.connection_pool[conn_id] = (connection, time.time(), True)
                    return conn_id, connection

            # Create new connection if pool isn't full
            if len(self.connection_pool) < self.config.pool_size:
                connection = await self._create_connection()
                conn_id = str(len(self.connection_pool))
                self.connection_pool[conn_id] = (connection, time.time(), True)
                return conn_id, connection

            # Wait for a connection to become available
            raise RuntimeError("Connection pool exhausted")

    async def _cleanup_loop(self):
        """Periodically clean up idle connections."""
        cleanup_interval = self.config.idle_timeout / 2
        while True:
            try:
                await asyncio.sleep(cleanup_interval)
                await self._cleanup_idle_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")

    async def _cleanup_idle_connections(self):
        """Remove idle connections that have exceeded the idle timeout."""
        current_time = time.time()
        async with self._lock:
            to_remove = []
            for conn_id, (connection, last_used, in_use) in self.connection_pool.items():
                idle_time = current_time - last_used
                if not in_use and idle_time > self.config.idle_timeout:
                    if not connection.is_closed:
                        await connection.close()
                    to_remove.append(conn_id)
                    logger.debug(f"Closed idle connection {conn_id} (idle for {idle_time:.1f}s)")
            
            for conn_id in to_remove:
                del self.connection_pool[conn_id]

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[aio_pika.Connection]:
        """
        Acquire a connection from the pool.
        
        Usage:
            async with connection_manager.acquire() as connection:
                # Use the connection
        """
        conn_id = None
        try:
            conn_id, connection = await self._get_available_connection()
            yield connection
        finally:
            if conn_id is not None:
                async with self._lock:
                    if conn_id in self.connection_pool:
                        conn, _, _ = self.connection_pool[conn_id]
                        self.connection_pool[conn_id] = (conn, time.time(), False)
                        logger.debug(f"Released connection {conn_id} back to pool")


# import asyncio
# from typing import Optional, Dict
# import aio_pika
# import random
# from dataclasses import dataclass
# import time
# from contextlib import asynccontextmanager

# from kal_utils.event_messaging.core.logging import logger

# @dataclass
# class ConnectionConfig:
#     """Configuration for RabbitMQ connection settings."""
#     max_retries: int = 5
#     initial_delay: float = 1.0  # seconds
#     max_delay: float = 60.0  # seconds
#     jitter: float = 0.1
#     pool_size: int = 5
#     connection_timeout: float = 30.0  # seconds
#     idle_timeout: float = 300.0  # seconds

# class RabbitMQConnectionManager:
#     """
#     Manages a pool of RabbitMQ connections with retry logic and connection health monitoring.
    
#     Features:
#     - Connection pooling with configurable pool size
#     - Exponential backoff retry mechanism
#     - Connection health monitoring
#     - Automatic connection cleanup
#     - Connection reuse optimization
#     """
    
#     def __init__(self, connection_url: str, config: Optional[ConnectionConfig] = None):
#         self.connection_url = connection_url
#         self.config = config or ConnectionConfig()
#         self.connection_pool: Dict[str, tuple[aio_pika.Connection, float, bool]] = {}  # {id: (connection, last_used, in_use)}
#         self._lock = asyncio.Lock()
#         self._cleanup_task: Optional[asyncio.Task] = None
        
#     async def start(self):
#         """Initialize the connection manager and start background tasks."""
#         self._cleanup_task = asyncio.create_task(self._cleanup_loop())
#         logger.info("RabbitMQ connection manager started")

#     async def stop(self):
#         """Gracefully shut down all connections and cleanup tasks."""
#         if self._cleanup_task:
#             self._cleanup_task.cancel()
#             try:
#                 await self._cleanup_task
#             except asyncio.CancelledError:
#                 pass

#         async with self._lock:
#             for conn_id, (connection, _, _) in self.connection_pool.items():
#                 if not connection.is_closed:
#                     await connection.close()
#             self.connection_pool.clear()
        
#         logger.info("RabbitMQ connection manager stopped")

#     def _calculate_retry_delay(self, attempt: int) -> float:
#         """Calculate delay for retry attempt with exponential backoff and jitter."""
#         delay = min(
#             self.config.initial_delay * (2 ** attempt),
#             self.config.max_delay
#         )
#         jitter_range = delay * self.config.jitter
#         return delay + random.uniform(-jitter_range, jitter_range)

#     async def _create_connection(self) -> aio_pika.Connection:
#         """Create a new connection with retry logic."""
#         for attempt in range(self.config.max_retries):
#             try:
#                 connection = await asyncio.wait_for(
#                     aio_pika.connect_robust(self.connection_url),
#                     timeout=self.config.connection_timeout
#                 )
#                 logger.info(f"Successfully established RabbitMQ connection after {attempt + 1} attempts")
#                 return connection
#             except Exception as e:
#                 if attempt == self.config.max_retries - 1:
#                     logger.error(f"Failed to establish RabbitMQ connection after {self.config.max_retries} attempts")
#                     raise
                
#                 delay = self._calculate_retry_delay(attempt)
#                 logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds")
#                 await asyncio.sleep(delay)

#     async def _get_available_connection(self) -> tuple[str, aio_pika.Connection]:
#         """Get an available connection from the pool or create a new one."""
#         async with self._lock:
#             # Try to find an existing idle connection
#             for conn_id, (connection, last_used, in_use) in self.connection_pool.items():
#                 if not in_use and not connection.is_closed:
#                     self.connection_pool[conn_id] = (connection, time.time(), True)
#                     return conn_id, connection

#             # Create new connection if pool isn't full
#             if len(self.connection_pool) < self.config.pool_size:
#                 connection = await self._create_connection()
#                 conn_id = str(len(self.connection_pool))
#                 self.connection_pool[conn_id] = (connection, time.time(), True)
#                 return conn_id, connection

#             # Wait for a connection to become available
#             raise RuntimeError("Connection pool exhausted")

#     async def _cleanup_loop(self):
#         """Periodically clean up idle connections."""
#         while True:
#             try:
#                 await asyncio.sleep(60)  # Check every minute
#                 await self._cleanup_idle_connections()
#             except asyncio.CancelledError:
#                 break
#             except Exception as e:
#                 logger.error(f"Error in cleanup loop: {str(e)}")

#     async def _cleanup_idle_connections(self):
#         """Remove idle connections that have exceeded the idle timeout."""
#         current_time = time.time()
#         async with self._lock:
#             to_remove = []
#             for conn_id, (connection, last_used, in_use) in self.connection_pool.items():
#                 if not in_use and (current_time - last_used) > self.config.idle_timeout:
#                     if not connection.is_closed:
#                         await connection.close()
#                     to_remove.append(conn_id)
            
#             for conn_id in to_remove:
#                 del self.connection_pool[conn_id]

#     @asynccontextmanager
#     async def acquire(self) -> aio_pika.Connection:
#         """
#         Acquire a connection from the pool.
        
#         Usage:
#             async with connection_manager.acquire() as connection:
#                 # Use the connection
#         """
#         conn_id = None
#         try:
#             conn_id, connection = await self._get_available_connection()
#             yield connection
#         finally:
#             if conn_id is not None:
#                 async with self._lock:
#                     if conn_id in self.connection_pool:
#                         conn, _, _ = self.connection_pool[conn_id]
#                         self.connection_pool[conn_id] = (conn, time.time(), False)