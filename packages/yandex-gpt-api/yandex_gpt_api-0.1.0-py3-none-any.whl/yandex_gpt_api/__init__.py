"""
Библиотека для работы с Yandex GPT API.

Предоставляет функции для синхронного и асинхронного взаимодействия с API,
включая потоковый режим для получения ответов по мере их генерации.
"""

from .api import gpt, gpt_streaming, gpt_async, gpt_streaming_httpx

__all__ = ['gpt', 'gpt_streaming', 'gpt_async', 'gpt_streaming_httpx']
