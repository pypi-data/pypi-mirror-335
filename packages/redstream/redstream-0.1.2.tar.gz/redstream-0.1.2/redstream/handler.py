import os
import logging
import importlib
import pkgutil
import redis.asyncio as redis  # Асинхронный клиент Redis
import traceback
from functools import wraps

logger = logging.getLogger("redstream.redis_handler")


class RedisHandlerRegistry:
    """Глобальный реестр обработчиков Redis Stream."""

    def __init__(self, auto_register_package=None, redis_url="redis://localhost:6379/0"):
        self.handlers = {}  # Словарь поток -> список обработчиков
        self.consumer_groups = {}  # Словарь поток -> consumer_group
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)  # Асинхронный клиент Redis

        if auto_register_package:
            self.auto_register_handlers(auto_register_package)

    def message(self, stream_name, consumer_group=None, filter_func=None):
        """Декоратор для регистрации обработчиков Redis Stream."""
        def decorator(func):
            @wraps(func)
            async def wrapper(message_data, message_id, source_stream):
                try:
                    # Проверяем, соответствует ли сообщение фильтру
                    if filter_func and not filter_func(message_data):
                        logger.info(f"⏩ Фильтр '{func.__name__}' отклонил сообщение ID: {message_data.get('message_id')}")
                        return None
                    logger.info(f"✅ Фильтр '{func.__name__}' принял сообщение ID: {message_data.get('message_id')}")

                    return await func(message_data, message_id, source_stream)
                except Exception as e:
                    logger.error(f"❌ Ошибка в обработчике {func.__name__}: {e}")
                    logger.debug(traceback.format_exc())
                    return None

            # ✅ Гарантируем, что `self.handlers[stream_name]` – список
            if stream_name not in self.handlers:
                self.handlers[stream_name] = []
            elif not isinstance(self.handlers[stream_name], list):
                logger.warning(f"⚠ self.handlers[{stream_name}] был {type(self.handlers[stream_name])}, исправляем на список!")
                self.handlers[stream_name] = [self.handlers[stream_name]]

            # ✅ Добавляем обработчик в список
            self.handlers[stream_name].append(wrapper)

            if consumer_group:
                self.consumer_groups[stream_name] = consumer_group  # 🔥 Сохраняем consumer_group

            logger.info(f"✅ Зарегистрирован обработчик: {stream_name} -> {func.__name__} (consumer_group={consumer_group})")
            return wrapper

        return decorator

    def get_handlers(self):
        """Возвращает все зарегистрированные обработчики."""
        return self.handlers

    def get_consumer_groups(self):
        """Возвращает все consumer_groups."""
        return self.consumer_groups

    def auto_register_handlers(self, package_name):
        """Рекурсивно ищет файлы обработчиков во всем пакете и его подпакетах."""
        logger.info(f"🔍 Поиск обработчиков в {package_name}...")

        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__[0]  # Абсолютный путь к пакету
            for module_info in pkgutil.walk_packages([package_path], prefix=f"{package_name}."):
                module_name = module_info.name
                if module_name.endswith("__main__") or module_name.endswith("__init__"):
                    continue

                try:
                    logger.info(f"📥 Импорт обработчика: {module_name}")
                    importlib.import_module(module_name)
                except Exception as e:
                    logger.error(f"❌ Ошибка при импорте {module_name}: {e}")
                    logger.debug(traceback.format_exc())

        except ModuleNotFoundError as e:
            logger.error(f"❌ Ошибка при загрузке обработчиков: {e}")
            logger.debug(traceback.format_exc())

        logger.info(f"✅ Все обработчики загружены автоматически. Итоговый список: {list(self.handlers.keys())}")


# ✅ Создаем глобальный экземпляр
redis_handler = RedisHandlerRegistry()


#Мне надо иметь возможность маркировать некоторые конфигурации как "только для чтения". Вносить изменения может только специальный сервис.
#Попытка внести запись в неизменяемые данные другими сервисами должна игнорироваться и отображаться варнингом в логах 
#Не должно быть привязки к именам сервисов внутри классов