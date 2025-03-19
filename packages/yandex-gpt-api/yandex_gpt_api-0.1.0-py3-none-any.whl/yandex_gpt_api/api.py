#!/usr/bin/env python3
"""
Библиотека для взаимодействия с Yandex GPT API.
Поддерживает синхронный и асинхронный режимы работы, включая потоковую обработку ответов.
"""
import os
import json
import asyncio
import requests
import httpx
from typing import AsyncGenerator, List, Dict, Optional


def gpt(auth_headers, messages=None, temperature=0.6, max_tokens=2000):
    """
    Синхронный режим для Yandex GPT.
    
    Args:
        auth_headers: Заголовки аутентификации с API ключом или IAM токеном
        messages: Список сообщений с ключами 'role' и 'text'
        temperature: Контролирует случайность (0.0 до 1.0)
        max_tokens: Максимальное количество токенов для генерации
        
    Returns:
        Строка с ответом от API
    """
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    
    # Используем предоставленные сообщения или по умолчанию
    if messages is None:
        messages = [
            {
                "role": "system",
                "text": "Вы - полезный ассистент"
            },
            {
                "role": "user",
                "text": "Расскажи короткую историю о роботе"
            }
        ]
    
    # Подготавливаем тело запроса
    request_body = {
        "modelUri": f"gpt://{os.getenv('FOLDER_ID')}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": str(max_tokens),
            "reasoningOptions": {
                "mode": "DISABLED"
            }
        },
        "messages": messages
    }
    
    # Выполняем запрос
    response = requests.post(url, headers=auth_headers, json=request_body)
    
    if response.status_code != 200:
        raise RuntimeError(
            f'Invalid response received: code: {response.status_code}, message: {response.text}'
        )
    
    return response.text


async def gpt_async(auth_headers, messages=None, temperature=0.6, max_tokens=2000, timeout=60.0):
    """
    Асинхронная функция для взаимодействия с Yandex GPT API.
    
    Args:
        auth_headers (dict): Заголовки авторизации (IAM-токен или API-ключ)
        messages (list): Список сообщений для обработки
        temperature (float): Температура генерации (от 0 до 1)
        max_tokens (int): Максимальное количество токенов в ответе
        timeout (float): Таймаут запроса в секундах
    
    Returns:
        str: Ответ от API в формате JSON
    """
    if messages is None:
        messages = []
    
    folder_id = os.environ.get('FOLDER_ID')
    if not folder_id:
        return json.dumps({"error": "Не указан FOLDER_ID"})
    
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    
    request_body = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": messages
    }
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=auth_headers, json=request_body)
            response.raise_for_status()
            return response.text
    except httpx.TimeoutError:
        return json.dumps({"error": "Превышено время ожидания ответа от API"})
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Ошибка HTTP: {e.response.status_code}", "details": e.response.text})
    except Exception as e:
        return json.dumps({"error": f"Ошибка при выполнении запроса: {str(e)}"})


def gpt_streaming(auth_headers, messages=None, temperature=0.6, max_tokens=2000, debug=False):
    """
    Синхронная функция для потокового взаимодействия с Yandex GPT API.
    
    Args:
        auth_headers (dict): Заголовки аутентификации
        messages (list, optional): Список сообщений для отправки
        temperature (float, optional): Температура генерации (0.0-1.0)
        max_tokens (int, optional): Максимальное количество токенов в ответе
        debug (bool, optional): Включить отладочный вывод
    
    Yields:
        Текстовые фрагменты по мере их генерации
    """
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    
    # Используем предоставленные сообщения или по умолчанию
    if messages is None:
        messages = [
            {
                "role": "system",
                "text": "Вы - полезный ассистент"
            },
            {
                "role": "user",
                "text": "Расскажи короткую историю о роботе"
            }
        ]
    
    if debug:
        print(f"URL: {url}")
        print(f"Headers: {auth_headers}")
        print(f"Messages: {messages}")
    
    # Подготавливаем тело запроса с включенным потоковым режимом
    request_body = {
        "modelUri": f"gpt://{os.getenv('FOLDER_ID')}/yandexgpt",
        "completionOptions": {
            "stream": True,
            "temperature": temperature,
            "maxTokens": str(max_tokens)
        },
        "messages": messages
    }
    
    if debug:
        print(f"Request body: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
    
    # Выполняем запрос с потоковым режимом
    response = requests.post(url, headers=auth_headers, json=request_body, stream=True)
    
    if debug:
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
    
    if response.status_code != 200:
        error_message = f'Invalid response received: code: {response.status_code}, message: {response.text}'
        if debug:
            print(f"Error: {error_message}")
        raise RuntimeError(error_message)
    
    # Обрабатываем потоковый ответ
    last_text = ""
    buffer = b""
    
    # Итерируемся по чанкам ответа
    for chunk in response.iter_content(chunk_size=1024):
        if not chunk:
            continue
            
        if debug:
            print(f"Received chunk of size: {len(chunk)} bytes")
        
        # Добавляем чанк в буфер
        buffer += chunk
        
        try:
            # Пытаемся декодировать буфер
            text = buffer.decode('utf-8')
            
            # Проверяем, есть ли в буфере полные JSON-объекты
            try:
                # Пытаемся найти полные JSON-объекты в буфере
                data = json.loads(text)
                
                if debug:
                    print(f"Parsed JSON: {json.dumps(data, ensure_ascii=False)[:200]}...")
                
                # Извлекаем текст из структуры ответа
                if 'result' in data and 'alternatives' in data['result']:
                    for alt in data['result']['alternatives']:
                        if 'message' in alt and 'text' in alt['message']:
                            current_text = alt['message']['text']
                            
                            if debug:
                                print(f"Current text: {current_text}")
                            
                            # Если это первый фрагмент или полностью новый текст
                            if not last_text:
                                if debug:
                                    print(f"First fragment: {current_text}")
                                yield current_text
                                last_text = current_text
                            # Если текст изменился, выдаем только новую часть
                            elif current_text != last_text:
                                if current_text.startswith(last_text):
                                    new_part = current_text[len(last_text):]
                                    if new_part:
                                        if debug:
                                            print(f"New part: {new_part}")
                                        yield new_part
                                else:
                                    if debug:
                                        print(f"Completely new text: {current_text}")
                                    yield current_text
                                last_text = current_text
                
                # Очищаем буфер после успешной обработки
                buffer = b""
            except json.JSONDecodeError:
                # Если не удалось разобрать JSON, возможно, это неполный чанк
                if debug:
                    print("Incomplete JSON, waiting for more data")
                # Оставляем данные в буфере для следующей итерации
        except UnicodeDecodeError:
            # Если не удалось декодировать, продолжаем накапливать байты
            if debug:
                print("Unicode decode error, waiting for more data")


async def gpt_streaming_httpx(auth_headers, messages=None, temperature=0.6, max_tokens=2000, timeout=60.0):
    """
    Асинхронная функция для потокового взаимодействия с Yandex GPT API с использованием httpx.
    
    Args:
        auth_headers (dict): Заголовки авторизации (IAM-токен или API-ключ)
        messages (list): Список сообщений для обработки
        temperature (float): Температура генерации (от 0 до 1)
        max_tokens (int): Максимальное количество токенов в ответе
        timeout (float): Таймаут запроса в секундах
    
    Yields:
        str: Фрагменты ответа от API
    """
    if messages is None:
        messages = []
    
    folder_id = os.environ.get('FOLDER_ID')
    if not folder_id:
        yield "Ошибка: Не указан FOLDER_ID"
        return
    
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    
    request_body = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": True,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": messages
    }
    
    try:
        # Для отслеживания уже полученного текста
        full_text = ""
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream('POST', url, headers=auth_headers, json=request_body) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if chunk.strip():
                        # Пропускаем пустые строки
                        if not chunk or chunk == 'data: [DONE]':
                            continue
                            
                        try:
                            # Обрабатываем строку JSON
                            if chunk.startswith('data: '):
                                json_str = chunk[6:]  # Убираем префикс 'data: '
                                data = json.loads(json_str)
                                
                                if 'result' in data and 'alternatives' in data['result']:
                                    for alt in data['result']['alternatives']:
                                        if 'message' in alt and 'text' in alt['message']:
                                            current_text = alt['message']['text']
                                            
                                            # Выдаем только новую часть текста
                                            if len(current_text) > len(full_text):
                                                new_text = current_text[len(full_text):]
                                                if new_text:  # Проверяем, что есть новый текст
                                                    full_text = current_text
                                                    yield new_text
                            else:
                                # Если это не JSON с префиксом 'data: ', просто выдаем как есть
                                yield chunk
                        except json.JSONDecodeError:
                            # Если не удалось разобрать JSON, выдаем как есть
                            if chunk.startswith('data: '):
                                yield chunk[6:]
                            else:
                                yield chunk
    except httpx.TimeoutError:
        yield "\nОшибка: Превышено время ожидания ответа от API"
    except httpx.HTTPStatusError as e:
        yield f"\nОшибка HTTP: {e.response.status_code}"
    except Exception as e:
        yield f"\nОшибка при выполнении запроса: {str(e)}"
