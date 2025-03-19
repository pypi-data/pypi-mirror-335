import asyncio
import logging
import redis.asyncio as redis
import traceback
import uuid
from redis.exceptions import ConnectionError, ResponseError
from .types.rs_message import RSMessage

logger = logging.getLogger("redstream.redis_stream_router")


class RedisStreamRouter:
    """Маршрутизатор сообщений между потоками Redis Streams."""

    def __init__(self, max_concurrent_requests=100):
        """Глобальная инициализация без конфигурации и без подключения к Redis."""
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

        # 🔄 Определяем `source_streams`
        if source_streams is not None:
            self.source_streams = source_streams
        elif consumer_groups is not None:
            self.source_streams = list(consumer_groups.keys())
        elif handlers is not None:
            self.source_streams = list(handlers.keys())

        # 🔄 Объединяем `consumer_groups`
        self.consumer_groups = {}
        for stream in self.source_streams:
            if stream in registered_consumer_groups:
                self.consumer_groups[stream] = registered_consumer_groups[stream]  
            elif consumer_groups and stream in consumer_groups:
                self.consumer_groups[stream] = consumer_groups[stream]
            elif consumer_group:
                self.consumer_groups[stream] = consumer_group

        # ✅ Гарантируем, что у всех потоков есть группа
        missing_groups = [s for s in self.source_streams if s not in self.consumer_groups]
        if missing_groups:
            package_group = f"{package_name}_group" if package_name else "default_group"
            for stream in missing_groups:
                self.consumer_groups[stream] = package_group
            logger.warning(f"⚠️ Потоки {missing_groups} не имели групп. Используется `{package_group}`.")

        if handlers is not None:
            self.handlers = handlers

        await self._initialize_consumer_groups()
        logger.info(f"🔄 Итоговый source_streams: {self.source_streams}")
        logger.info(f"🔄 Итоговый consumer_groups: {self.consumer_groups}")

    async def _initialize_consumer_groups(self):
        """Создает группы потребителей, если они еще не существуют."""
        for stream, group in self.consumer_groups.items():
            try:
                await self.redis_conn.xgroup_create(stream, group, id="0", mkstream=True)
                logger.info(f"✅ Группа {group} создана для {stream}")
            except ResponseError as e:
                if "BUSYGROUP" in str(e):
                    logger.info(f"⚠️ Группа {group} уже существует для {stream}")
                else:
                    logger.error(f"❌ Ошибка создания группы {group} для {stream}: {e}")
                    logger.debug(traceback.format_exc())

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

                # ✅ Перебираем всех обработчиков потока
                for handler in self.handlers[stream]:
                    try:
                        logger.debug(f"🔍 Вызываем обработчик '{handler.__name__}' для потока {stream}")
                        result = await handler(message_data, message_id, stream)
                        if result:
                            processed_data_list.append(result)
                    except Exception as e:
                        logger.error(f"❌ Ошибка при выполнении '{handler.__name__}': {e}")
                        logger.debug(traceback.format_exc())

                # ✅ Проверяем, есть ли `correlation_id`
                correlation_id = message_data.get("correlation_id")
                for processed_data in processed_data_list:
                    if isinstance(processed_data, dict):
                        for target_stream, result in processed_data.items():
                            if correlation_id:
                                result["correlation_id"] = correlation_id  # Передаем ID ответа
                            await self.publish_message(target_stream, result)

                # ✅ Подтверждаем обработку сообщения в Redis
                await self.redis_conn.xack(stream, self.consumer_groups[stream], message_id)

            except Exception as e:
                logger.error(f"❌ Ошибка обработки {message_id} из {stream}: {e}")
                logger.debug(traceback.format_exc())

    async def send_request_with_timeout(self, target_stream, message, response_stream=None, timeout=5, max_retries=3):
        """
        Отправляет сообщение и ожидает ответ с таймаутом. Если `response_stream` не указан, создаётся уникальный поток.
        """
        async with self.request_semaphore:
            correlation_id = str(uuid.uuid4())
            message["correlation_id"] = correlation_id

            # ✅ Генерируем уникальный поток, если не передан
            if response_stream is None:
                response_stream = f"response_stream_{correlation_id}"

            response_redis_conn = None

            try:
                response_redis_conn = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                response_group = f"{response_stream}_group"
                consumer_name = f"consumer_{correlation_id}"

                # ✅ Создаём поток и группу, если они не существуют
                try:
                    await response_redis_conn.xgroup_create(response_stream, response_group, id="0", mkstream=True)
                except ResponseError as e:
                    if "BUSYGROUP" not in str(e):
                        logger.error(f"❌ Ошибка создания группы: {e}")

                # 📤 Отправляем сообщение с указанием потока ожидания
                message["response_stream"] = response_stream  # ✅ Добавляем поток в само сообщение
                for attempt in range(max_retries):
                    try:
                        await self.redis_conn.xadd(target_stream, message)
                        logger.info(f"📤 Запрос отправлен в {target_stream}, ожидаем в {response_stream}, correlation_id={correlation_id} (попытка {attempt+1})")
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            logger.error(f"❌ Не удалось отправить запрос: {e}")
                            return None
                        await asyncio.sleep(0.5 * (2 ** attempt))  # Backoff

                # ⏳ Ожидаем ответ
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        messages = await response_redis_conn.xreadgroup(
                            groupname=response_group,
                            consumername=consumer_name,
                            streams={response_stream: ">"},
                            count=1,
                            block=500
                        )
                        if messages:
                            for stream, msg_list in messages:
                                for msg_id, data in msg_list:
                                    if data.get("correlation_id") == correlation_id:
                                        await response_redis_conn.xack(stream, response_group, msg_id)
                                        return data
                                    else:
                                        logger.warning(f"⚠️ Получен неожиданный ответ (другой correlation_id): {data}")

                    except ConnectionError as e:
                        logger.warning(f"⚠️ Соединение прервано: {e}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"❌ Ошибка чтения ответа: {e}")
                        await asyncio.sleep(0.5)

                logger.warning(f"⏳ Таймаут ожидания ответа для correlation_id={correlation_id}")

            finally:
                if response_redis_conn:
                    try:
                        await response_redis_conn.xgroup_delconsumer(response_stream, response_group, consumer_name)
                        await response_redis_conn.aclose()
                    except Exception as e:
                        logger.error(f"❌ Ошибка при закрытии Redis-соединения: {e}")

            return None

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

        # Дождаться завершения обработки всех сообщений
        while not self.queue.empty():
            await asyncio.sleep(0.1)

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("✅ Все процессы завершены.")


# ✅ Создаем глобальный объект `redis_router`
redis_router = RedisStreamRouter()
