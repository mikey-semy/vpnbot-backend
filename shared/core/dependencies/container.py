"""
Модуль содержит контейнер зависимостей.
"""

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers.users import UserProvider

container = make_async_container(
    UserProvider(),
)
