import io
import logging
import os
import requests
import traceback
from django.http import JsonResponse
from datetime import datetime
from dotenv import load_dotenv
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

load_dotenv(override=True)

MODULE_NAME=os.getenv("MODULE_NAME")
TELEGRAM_GROUP_ID=os.getenv("TELEGRAM_GROUP_ID")
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")

TOPIC_LIST = {
    "ORDERS": 2,
    "CONTRACT": 4,
    "RATES": 38,
    "E-TICKET": 49,
    "RULES": 44,
    "SUPPLIERS": 42,
    "RULES MATCHER": 40,
    "CORE": 36,
    "CONTENT": 29,
    "CHARTER": 24,
    "REPORTS": 272
}

class Exception:
    """
    Этот middleware обрабатывает все ошибки со статус-кодами 300, 400, 500
    и отправляет их в Telegram в виде `.txt` файла с полной информацией о запросе.
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = None
        try:
            response = self.get_response(request)
        except Exception as e:
            # 🔹 Ошибка 500 - внутренняя ошибка сервера
            response = JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)
            self.log_and_notify(request, response, e)
  
        # 🔹 Проверяем коды 300, 400 и 500
        if response.status_code >= 300:
            self.log_and_notify(request, response)

        return response
    
    def log_and_notify(self, request, response, exception=None):
        """
        Логирование ошибки и отправка в Telegram в `.txt` формате
        (IP, User-Agent, Дата, Заголовки, Параметры запроса и Тело запроса)
        """
        logger = logging.getLogger('django')
        
       # 🔹 Получение IP-адреса клиента
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            user_ip = forwarded_for.split(',')[0]  # Если несколько IP, берем первый
        else:
            user_ip = request.META.get('REMOTE_ADDR', 'Неизвестный IP')

        # 🔹 User-Agent (информация о браузере клиента)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Неизвестный User-Agent')

        # 🔹 Текущая дата и время
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 🔹 Данные запроса
        request_method = request.method  # GET, POST, PUT, PATCH, DELETE
        request_headers = dict(request.headers)  # Все заголовки запроса
        request_query_params = dict(request.GET)  # Query параметры (`?key=value`)
        request_body = "Тело запроса пустое"

        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # 🔹 Используем request.read(), чтобы избежать RawPostDataException
                request_body = request.read()  # ✅ Безопасное чтение тела запроса
                
                if request_body:
                    request_body = request_body.decode("utf-8", errors="ignore")
                else:
                    request_body = "Тело запроса пустое"
            except Exception as e:
                request_body = f"Ошибка при чтении тела запроса: {str(e)}"
                
         # 🔹 Текст ошибки для Telegram
        error_message = f"🚨 *Сервис {MODULE_NAME}*\n\n"
        error_message += f"🔄 *Метод:* `{request_method}`\n"
        error_message += f"📍 *Путь:* `{request.path}`\n"
        error_message += f"🔵 *Статус-код:* `{response.status_code}`\n"
        error_message += f"🌍 *IP клиента:* `{user_ip}`\n"
        error_message += f"🖥 *User-Agent:* `{user_agent}`\n"
        error_message += f"📅 *Дата и время:* `{current_time}`\n"
        
        # 🔹 Сбор информации об ошибке
        
        if exception:
                
            logger.error(f"Ошибка {MODULE_NAME}:", exc_info=True)
            error_trace = traceback.format_exc()
            log_content = f"Путь: {request.path}\n"
            log_content += f"Метод: {request_method}\n"
            log_content += f"Статус-код: {response.status_code}\n"
            log_content += f"IP клиента: {user_ip}\n"
            log_content += f"User-Agent: {user_agent}\n"
            log_content += f"Дата и время: {current_time}\n"
            log_content += f"Заголовки:\n{request_headers}\n\n"
            log_content += f"Параметры запроса:\n{request_query_params}\n\n"
            log_content += f"Тело запроса:\n{request_body}\n\n"
            log_content += f"Ошибка: {str(exception)}\n\n"
            log_content += f"{error_trace}\n"
            
            if isinstance(exception, (ValidationError, DRFValidationError)):
                log_content += f"❌ *Validation Error:* `{exception}`\n"
                logger.error(f"Validation Error: {exception}")
            
        else:
            log_content = f"Путь: {request.path}\n"
            log_content += f"Метод: {request_method}\n"
            log_content += f"Статус-код: {response.status_code}\n"
            log_content += f"IP клиента: {user_ip}\n"
            log_content += f"User-Agent: {user_agent}\n"
            log_content += f"Дата и время: {current_time}\n"
            log_content += f"Заголовки:\n{request_headers}\n\n"
            log_content += f"Параметры запроса:\n{request_query_params}\n\n"
            log_content += f"Тело запроса:\n{request_body}\n\n"
            log_content += f"Ответ сервера: {response.content.decode('utf-8')}\n"

        # 🔹 Отправка файла в Telegram
        self.send_to_telegram(error_message, log_content)

    def send_to_telegram(self, caption, content):
        """Отправка `.txt` файла в Telegram без его сохранения на диск."""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        file_obj = io.BytesIO(content.encode('utf-8'))
        file_obj.name = "error_log.txt"

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {"document": file_obj}
        data = {"chat_id": TELEGRAM_GROUP_ID, "message_thread_id": TOPIC_LIST[MODULE_NAME], "caption": caption, "parse_mode": "Markdown"}
        try:
            requests.post(url, files=files, data=data)
        except Exception as e:
            print("Ошибка при отправке файла в Telegram:", e)
