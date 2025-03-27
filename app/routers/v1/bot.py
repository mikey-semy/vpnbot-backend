"""
Модуль для обработки вебхуков Telegram бота.

Этот модуль содержит роутер и обработчики для приема и обработки
вебхук-обновлений от Telegram бота. Используется для интеграции
бота с веб-сервером через webhook API.

Роутеры:
- /bot/webhook - Эндпоинт для приема вебхуков от Telegram

Зависимости:
- FastAPI для создания API эндпоинтов
- Telegram бот и диспетчер для обработки обновлений
"""
from dishka.integrations.fastapi import FromDishka, inject
from bot.core.instance import dp, bot
class AuthRouter(BaseRouter):
    """
    Класс для настройки маршрутов аутентификации.

    Этот класс предоставляет маршруты для аутентификации пользователей,
    такие как вход, выход, запрос на восстановление пароля и подтверждение сброса пароля.

    """

    def __init__(self):
        super().__init__(prefix="bot", tags=["Webhook"])


def configure(self):

    @self.router.post("/webhook")
    @inject
    async def bot_webhook(update: dict) -> dict:
        """
        Обработчик вебхука для приема обновлений от бота.

        Args:
            update (dict): Обновление от бота.

        Returns:
            dict: Результат обработки обновления.
        """
        await dp.feed_webhook_update(bot, update)
        return {'ok': True}
