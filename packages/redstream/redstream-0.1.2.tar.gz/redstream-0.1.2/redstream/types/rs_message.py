import json
import pytz
import uuid
from typing import Optional, Dict, Any, Union
import logging

logger = logging.getLogger("redstream.types.rs_message")


class RSMessage:
    """Универсальная структура сообщения для микросервисной архитектуры (Redis Streams)."""
    
    """
    Поддерживает:
    - Текстовые, мультимедийные, голосовые сообщения
    - Ответы (`reply_to_message_id`)
    - Text-to-Speech (`tts_generated`)
    - Correlation ID для трекинга запросов
    - Совместимость с aiogram Message (если aiogram доступен)
    - Готов для работы с RedisStreamRouter
    """

    def __init__(
        self,
        event_type: str,                        # Тип события ("message", "edit_message"...)
        message_type: Optional[str] = "text",   # Тип сообщения
        action: Optional[str] = "",             # Требуемое действие
        status: Optional[str] = "",             # Статус операции
        chat_id: Optional[str] = None,          # ID чата (группы)
        user_id: Optional[str] = None,          # ID пользователя
        message_id: Optional[str] = None,       # ID сообщения в чате
        text: Optional[str] = "",               # Текст события
        is_command: Optional[bool] = False,     # Является ли событие командой
        first_name: Optional[str] = "",         # Имя пользователя
        username: Optional[str] = "",           # Логин пользователя
        date: Optional[str] = None,             # Дата/время сообщения
        reply_to_message_id: Optional[Union[str, int]] = None,
        media_data: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        tts_generated: Optional[bool] = False,
        correlation_id: Optional[str] = None,
        response_stream: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        callback_data: Optional[Union[str, Dict[str, Any]]] = None, # 🔥 Данные колбэка
        callback_action: Optional[str] = None,                      # 🔥 Действие при колбэке
    ):
        self.event_type = event_type
        self.message_type = message_type
        self.action = action
        self.status = status
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id
        self.text = text or ""
        self.is_command = is_command
        self.first_name = first_name
        self.username = username
        self.date = date or self._current_time()
        self.reply_to_message_id = str(reply_to_message_id) if reply_to_message_id else None
        self.media_data = media_data
        self.file_path = file_path
        self.tts_generated = tts_generated
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.response_stream = response_stream
        self.extra_data = extra_data
        self.callback_data = callback_data  # ✅ Данные для обработки колбэка
        self.callback_action = callback_action  # ✅ Действие при колбэке

    @staticmethod
    def _current_time() -> str:
        """Возвращает текущее время в формате UTC."""
        return pytz.utc.localize(pytz.datetime.datetime.utcnow()).isoformat()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RSMessage":
        """Создает объект RSMessage из словаря."""

        def safe_json_loads(value: Any) -> Any:
            """Попытка распарсить JSON-строку, иначе вернуть как есть."""
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Ошибка разбора JSON: {value}")
                    return value  # Если JSON некорректен, оставляем строку (но лучше избегать такого)
            return value

        logger.debug(f"📩 from_dict() входные данные: {data}")

        instance = cls(
            event_type=data.get("event_type", "message"),
            message_type=data.get("message_type", "text"),
            action=data.get("action", ""),
            status=data.get("status", ""),
            chat_id=data.get("chat_id"),
            user_id=int(data["user_id"]) if data.get("user_id") is not None else None,
            message_id=data.get("message_id") or "unknown",
            text=data.get("text", ""),
            is_command=data.get("is_command", False),
            first_name=data.get("first_name", ""),
            username=data.get("username", ""),
            date=data.get("date"),
            reply_to_message_id=str(data["reply_to_message_id"]) if data.get("reply_to_message_id") else None,
            media_data=data.get("media_data"),
            file_path=data.get("file_path"),
            tts_generated=data.get("tts_generated", False),
            correlation_id=data.get("correlation_id") or str(uuid.uuid4()),
            response_stream=data.get("response_stream"),
            extra_data=safe_json_loads(data.get("extra_data")),  # 🛠 Теперь `extra_data` всегда словарь
            callback_data=data.get("callback_data"),
            callback_action=data.get("callback_action"),
        )

        logger.debug(f"📩 from_dict() создал RSMessage с message_id={instance.message_id}, correlation_id={instance.correlation_id}")

        return instance

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует объект в словарь для передачи через Redis."""
        result = {
            k: ("1" if isinstance(v, bool) and v else "0" if isinstance(v, bool) else str(v) if isinstance(v, uuid.UUID) else v)
            for k, v in self.__dict__.items()
            if v is not None
        }

        if isinstance(self.extra_data, dict):
            result["extra_data"] = json.dumps(self.extra_data, ensure_ascii=False)

        if isinstance(self.callback_data, dict):
            result["callback_data"] = json.dumps(self.callback_data, ensure_ascii=False)

        result["correlation_id"] = str(self.correlation_id)  # ✅ Приводим к строке

        return result

    def to_json(self) -> str:
        """Сериализация в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "RSMessage":
        """Создает RSMessage из JSON-строки."""
        return cls.from_dict(json.loads(json_str))

    # === Методы для работы с aiogram (если доступен) ===
    @classmethod
    def from_aiogram_message(cls, message: Any) -> "RSMessage":
        """Создает RSMessage из aiogram.types.Message."""
        if not hasattr(message, "chat") or not hasattr(message, "from_user"):
            raise ValueError("Переданный объект не является aiogram Message.")

        return cls(
            event_type="message",
            message_type=message.content_type.value,
            chat_id=str(message.chat.id),
            user_id=str(message.from_user.id),
            message_id=str(message.message_id),
            text=message.text or message.caption or "",
            is_command=bool(message.text and message.text.startswith("/")),
            first_name=message.from_user.first_name or "",
            username=message.from_user.username or "",
            date=str(message.date),
            reply_to_message_id=str(message.reply_to_message.message_id) if message.reply_to_message else None,
            media_data=cls.extract_media_data(message),
        )

    def to_aiogram_message(self) -> Dict[str, Any]:
        """Конвертирует RSMessage в JSON-структуру, схожую с aiogram Message."""
        return {
            "chat": {"id": int(self.chat_id) if self.chat_id else None},
            "from_user": {
                "id": int(self.user_id) if self.user_id else None,
                "first_name": self.first_name,
                "username": self.username,
            },
            "message_id": int(self.message_id) if self.message_id else None,
            "date": self.date,
            "text": self.text,
            "content_type": self.message_type,
            "media_data": self.media_data,
            "reply_to_message_id": int(self.reply_to_message_id) if self.reply_to_message_id else None,
            "correlation_id": self.correlation_id,
        }

    @staticmethod
    def extract_media_data(message: Any) -> Optional[Dict[str, Any]]:
        """Извлекает информацию о мультимедиа (фото, видео, документы) из aiogram Message."""
        media_data = None
        if hasattr(message, "photo") and message.photo:
            media_data = {"type": "photo", "file_id": message.photo[-1].file_id}
        elif hasattr(message, "video") and message.video:
            media_data = {"type": "video", "file_id": message.video.file_id}
        elif hasattr(message, "document") and message.document:
            media_data = {
                "type": "document",
                "file_id": message.document.file_id,
                "file_name": message.document.file_name,
            }
        elif hasattr(message, "voice") and message.voice:
            media_data = {"type": "voice", "file_id": message.voice.file_id}
        elif hasattr(message, "audio") and message.audio:
            media_data = {"type": "audio", "file_id": message.audio.file_id}
        return media_data
