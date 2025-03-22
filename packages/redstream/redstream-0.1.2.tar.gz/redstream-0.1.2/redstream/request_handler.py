import asyncio
import logging
import uuid
import traceback
import redis.asyncio as redis
from redis.exceptions import ConnectionError, ResponseError

logger = logging.getLogger("redstream.redis_stream_router.request_handler")

async def send_request_with_timeout(redis_conn, redis_url, target_stream, message, response_stream=None, timeout=5, max_retries=3):
    """
    Отправляет сообщение и ожидает ответ с таймаутом.
    Если response_stream не указан, создается уникальный поток.
    Возвращает данные ответа или None.
    """
    correlation_id = message.get("correlation_id") or str(uuid.uuid4())
    message["correlation_id"] = correlation_id

    if response_stream is None:
        response_stream = f"response_stream_{correlation_id}"

    response_redis_conn = None

    try:
        response_redis_conn = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        response_group = f"{response_stream}_group"
        consumer_name = f"consumer_{correlation_id}"

        try:
            await response_redis_conn.xgroup_create(response_stream, response_group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.error(f"❌ Ошибка создания группы: {e}")

        message["response_stream"] = response_stream
        for attempt in range(max_retries):
            try:
                await redis_conn.xadd(target_stream, message)
                logger.info(f"📤 Запрос отправлен в {target_stream}, ожидаем в {response_stream}, correlation_id={correlation_id} (попытка {attempt+1})")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"❌ Не удалось отправить запрос: {e}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))

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
                    for stream_name, msg_list in messages:
                        for msg_id, data in msg_list:
                            if data.get("correlation_id") == correlation_id:
                                logger.debug(f"Подтверждаем сообщение: stream={stream_name}, group={response_group}, msg_id={msg_id}")
                                await response_redis_conn.xack(stream_name, response_group, msg_id)
                                logger.debug("Сообщение подтверждено.")
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
                logger.debug(f"Удаляем consumer '{consumer_name}' из группы '{response_group}' на потоке '{response_stream}'")
                await response_redis_conn.xgroup_delconsumer(response_stream, response_group, consumer_name)
                await response_redis_conn.aclose()
            except Exception as e:
                logger.error(f"❌ Ошибка при закрытии Redis-соединения: {e}")

    return None

async def send_streaming_request(
    redis_conn, redis_url, target_stream, message, response_stream=None,
    initial_timeout=5, max_retries=3, track_own_responses=True
):
    correlation_id = message.get("correlation_id") or str(uuid.uuid4())
    message["correlation_id"] = correlation_id

    if response_stream is None:
        response_stream = f"response_stream_{correlation_id}"
    response_group = f"{response_stream}_group"
    consumer_name = f"consumer_{correlation_id}"

    await redis_conn.xadd(target_stream, {**message, "response_stream": response_stream})
    logger.info(f"📤 Запрос отправлен в {target_stream}, ожидаем в {response_stream}, correlation_id={correlation_id}")

    response_redis_conn = redis.from_url(redis_url, decode_responses=True)

    try:
        try:
            await response_redis_conn.xgroup_create(response_stream, response_group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.error(f"❌ Ошибка создания группы: {e}")

        final_received = False

        while not final_received:
            messages = await response_redis_conn.xreadgroup(
                groupname=response_group,
                consumername=consumer_name,
                streams={response_stream: ">"},
                count=10,
                block=2000
            )

            for stream_name, msg_list in messages or []:
                for msg_id, data in msg_list:
                    if not track_own_responses or data.get("correlation_id") == correlation_id:
                        await response_redis_conn.xack(stream_name, response_group, msg_id)
                        try:
                            yield data
                        except GeneratorExit:
                            logger.warning("🧹 Прерывание генератора, выполняем очистку.")
                            raise
                        if data.get("final_chunk") == "1":
                            logger.info("✅ Поток завершен по признаку final_chunk.")
                            final_received = True
                            return
                    else:
                        logger.debug(f"⚠️ Игнор чужого сообщения: {data}")
            await asyncio.sleep(0.05)

    except GeneratorExit:
        logger.warning("🧹 Генератор прерван — выполняется очистка.")
        raise

    except Exception as e:
        logger.exception(f"❌ Ошибка в send_streaming_request: {e}")

    finally:
        try:
            await response_redis_conn.xgroup_delconsumer(response_stream, response_group, consumer_name)
            await response_redis_conn.aclose()
            logger.debug("🔒 Соединение Redis закрыто.")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при закрытии Redis: {e}")

