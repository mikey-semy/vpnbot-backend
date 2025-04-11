"""
Модуль аутентификации и авторизации пользователей.

Этот модуль предоставляет компоненты для проверки подлинности
и авторизации пользователей в приложении FastAPI с использованием
JWT токенов и интеграции с Dishka.

Основные компоненты:
- OAuth2PasswordBearer: схема безопасности для документации OpenAPI
- get_current_user: функция-зависимость для получения текущего пользователя

Примеры использования:

1. В маршрутах FastAPI с использованием стандартных зависимостей:
    ```
    @router.get("/protected")
    async def protected_route(user: CurrentUserSchema = Depends(get_current_user)):
        return {"message": f"Hello, {user.username}!"}
    ```
"""

import logging

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import (InvalidCredentialsError, TokenError,
                                 TokenInvalidError, TokenMissingError)
from app.core.security import TokenManager
from app.core.settings import settings
from app.schemas import CurrentUserSchema, UserCredentialsSchema
from app.services.v1.auth.service import AuthService

logger = logging.getLogger(__name__)

# Создаем экземпляр OAuth2PasswordBearer для использования с Depends
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.AUTH_URL,
    scheme_name="OAuth2PasswordBearer",
    description="Bearer token",
    auto_error=False,
)


class AuthenticationManager:
    """
    Менеджер аутентификации пользователей.

    Этот класс предоставляет методы для работы с аутентификацией,
    включая проверку токенов и получение данных текущего пользователя.

    Методы:
        get_current_user: Получает данные текущего пользователя по токену
        validate_token: Проверяет валидность токена и извлекает полезную нагрузку
    """

    @staticmethod
    @inject
    async def get_current_user(
        request: Request,
        token: str = Depends(oauth2_scheme),
        auth_service: FromDishka[AuthService] = None,
    ) -> UserCredentialsSchema:
        """
        Получает данные текущего аутентифицированного пользователя.

        Эта функция проверяет JWT токен, переданный в заголовке Authorization,
        декодирует его, и получает пользователя из системы по идентификатору
        в токене (sub).

        Args:
            request: Запрос FastAPI, содержащий заголовки HTTP
            token: Токен доступа, извлекаемый из заголовка Authorization
            auth_service: Сервис аутентификации (внедряется Dishka)

        Returns:
            UserCredentialsSchema: Схема данных текущего пользователя

        Raises:
            TokenInvalidError: Если токен отсутствует, недействителен или истек
        """
        logger.debug(
            "Обработка запроса аутентификации с заголовками: %s", request.headers
        )
        logger.debug("Начало получения данных пользователя")
        logger.debug("Получен токен: %s", token)

        if not token:
            logger.debug("Токен отсутствует в запросе")
            raise TokenMissingError()

        try:
            payload = TokenManager.verify_token(token)

            user_email = TokenManager.validate_payload(payload)

            user = await auth_service.get_user_by_identifier(user_email)

            if not user:
                logger.debug("Пользователь с email %s не найден", user_email)
                raise InvalidCredentialsError()

            user_schema = UserCredentialsSchema.model_validate(user)
            logger.debug("Пользователь успешно аутентифицирован: %s", user_schema)

            current_user = CurrentUserSchema(
                id=user_schema.id,
                username=user_schema.username,
                email=user_schema.email,
                role=user_schema.role,
                is_active=user_schema.is_active,
                is_verified=user_schema.is_verified,
            )

            return current_user

        except TokenError:
            # Перехватываем все ошибки токенов и пробрасываем дальше
            raise
        except Exception as e:
            logger.debug("Ошибка при аутентификации: %s", str(e))
            raise TokenInvalidError() from e


# Для совместимости с существующим кодом и простоты использования
get_current_user = AuthenticationManager.get_current_user
