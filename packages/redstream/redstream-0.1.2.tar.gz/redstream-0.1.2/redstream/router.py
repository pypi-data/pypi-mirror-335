import asyncio
import logging
import redis.asyncio as redis
import traceback
import uuid
from redis.exceptions import ConnectionError, ResponseError
from .types.rs_message import RSMessage
from .consumer_group_manager import initialize_consumer_groups
from .request_handler import send_request_with_timeout, send_streaming_request

logger = logging.getLogger("redstream.redis_stream_router")

class RedisStreamRouter:
    """Маршрутизатор сообщений между потоками Redis Streams."""

    def __init__(self, max_concurrent_requests=100):
        self.redis_url = None
        self.redis_conn = None  # Подключение к Redis устанавливается позже
        self.source_streams = []
        self.consumer_groups = {}
        self.handlers = {}
        self.shutdown_event = asyncio.Event()
        self.queue = asyncio.Queue()
        self.tasks = []
        self.request_semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def set_config(self, redis_url, redis_handler, package_name, source_streams=None, consumer_groups=None, consumer_group=None, handlers=None):
        """Настройка RedisStreamRouter + подключение к Redis."""
        self.redis_url = redis_url
        self.redis_conn = redis.from_url(self.redis_url, decode_responses=True)

        # Автоматически загружаем все обработчики
        redis_handler.auto_register_handlers(package_name)
        handlers = redis_handler.get_handlers()
        registered_consumer_groups = redis_handler.get_consumer_groups()
        logger.info(f"🔄 Зарегистрированные хендлеры: {handlers}")

        # Определяем source_streams
        if source_streams is not None:
            self.source_streams = source_streams
        elif consumer_groups is not None:
            self.source_streams = list(consumer_groups.keys())
        elif handlers is not None:
            self.source_streams = list(handlers.keys())

        # Объединяем consumer_groups
        self.consumer_groups = {}
        for stream in self.source_streams:
            if stream in registered_consumer_groups:
                self.consumer_groups[stream] = registered_consumer_groups[stream]
            elif consumer_groups and stream in consumer_groups:
                self.consumer_groups[stream] = consumer_groups[stream]
            elif consumer_group:
                self.consumer_groups[stream] = consumer_group

        # Гарантируем, что у всех потоков есть группа
        missing_groups = [s for s in self.source_streams if s not in self.consumer_groups]
        if missing_groups:
            package_group = f"{package_name}_group" if package_name else "default_group"
            for stream in missing_groups:
                self.consumer_groups[stream] = package_group
            logger.warning(f"⚠️ Потоки {missing_groups} не имели групп. Используется `{package_group}`.")

        if handlers is not None:
            self.handlers = handlers

        await initialize_consumer_groups(self.redis_conn, self.consumer_groups)
        logger.info(f"🔄 Итоговый source_streams: {self.source_streams}")
        logger.info(f"🔄 Итоговый consumer_groups: {self.consumer_groups}")

    async def publish_message(self, target_stream, message):
        """Отправляет сообщение в указанный поток Redis."""
        if not self.redis_conn:
            logger.error("🚨 Ошибка: Redis не подключен!")
            return

        try:
            await self.redis_conn.xadd(target_stream, message)
            logger.info(f"📤 Сообщение отправлено в {target_stream}: {message}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в {target_stream}: {e}")
            logger.debug(traceback.format_exc())

    async def read_messages(self, source_stream):
        """Читает сообщения из потока и помещает их в очередь."""
        if not self.redis_conn:
            logger.error("🚨 Ошибка: Redis не подключен!")
            return

        group = self.consumer_groups[source_stream]
        consumer = f"{source_stream}_consumer"

        while not self.shutdown_event.is_set():
            try:
                messages = await self.redis_conn.xreadgroup(
                    groupname=group,
                    consumername=consumer,
                    streams={source_stream: ">"},
                    count=10,
                    block=2000
                )
                if messages:
                    for stream, msg_list in messages:
                        for message_id, message_data in msg_list:
                            await self.queue.put((stream, message_id, message_data))
            except Exception as e:
                logger.error(f"❌ Ошибка чтения из {source_stream}: {e}")
                logger.debug(traceback.format_exc())

        logger.info(f"🛑 Чтение из {source_stream} остановлено.")

    async def process_messages(self):
        """Обрабатывает сообщения из очереди, вызывая всех зарегистрированных обработчиков."""
        while not self.shutdown_event.is_set():
            try:
                stream, message_id, message_data = await self.queue.get()
                logger.info(f"📩 Получено сообщение из {stream}: {message_data}")

                if stream not in self.handlers or not self.handlers[stream]:
                    logger.warning(f"⚠ Нет зарегистрированных обработчиков для потока {stream}")
                    continue

                processed_data_list = []

                for handler in self.handlers[stream]:
                    try:
                        result = await handler(message_data, message_id, stream)
                        if result:
                            processed_data_list.append(result)
                    except Exception as e:
                        logger.error(f"❌ Ошибка при выполнении '{handler.__name__}': {e}")
                        logger.debug(traceback.format_exc())

                correlation_id = message_data.get("correlation_id")
                for processed_data in processed_data_list:
                    if isinstance(processed_data, dict):
                        for target_stream, result in processed_data.items():
                            if correlation_id:
                                result["correlation_id"] = correlation_id
                            await self.publish_message(target_stream, result)

                await self.redis_conn.xack(stream, self.consumer_groups[stream], message_id)

            except Exception as e:
                logger.error(f"❌ Ошибка обработки {message_id} из {stream}: {e}")
                logger.debug(traceback.format_exc())

    async def send_request_with_timeout(self, target_stream, message, response_stream=None, timeout=5, max_retries=3):
        """
        Отправляет запрос с таймаутом.
        Обертка вокруг функции из request_handler для сохранения обратной совместимости.
        """
        async with self.request_semaphore:
            return await send_request_with_timeout(self.redis_conn, self.redis_url, target_stream, message, response_stream, timeout, max_retries)

    async def send_streaming_request(
        self, target_stream, message, response_stream=None,
        initial_timeout=5, max_retries=3, track_own_responses=True
    ):
        """
        Потоковый запрос с промежуточными ответами.
        Обертка вокруг функции из request_handler с контролем завершения генератора.
        """
        async with self.request_semaphore:
            gen = send_streaming_request(
                self.redis_conn,
                self.redis_url,
                target_stream,
                message,
                response_stream,
                initial_timeout,
                max_retries,
                track_own_responses
            )
            try:
                async for response in gen:
                    yield response
            finally:
                await gen.aclose()

    async def start(self):
        """Запускает чтение сообщений (группы уже созданы)."""
        self.shutdown_event.clear()

        for stream in self.source_streams:
            self.tasks.append(asyncio.create_task(self.read_messages(stream)))
        self.tasks.append(asyncio.create_task(self.process_messages()))

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("🛑 RedisStreamRouter остановлен.")

    async def stop(self):
        """Останавливает роутер, дожидаясь обработки всех сообщений в очереди."""
        logger.info("🛑 Остановка RedisStreamRouter...")
        self.shutdown_event.set()

        while not self.queue.empty():
            await asyncio.sleep(0.1)

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("✅ Все процессы завершены.")

# Глобальный объект `redis_router` для использования в пакете
redis_router = RedisStreamRouter()
