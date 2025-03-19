# Telegram Error Logger

This is a Django middleware that logs errors and sends them to Telegram.

## Installation

```sh
pip install telegram-error-logger


## settings.py
MIDDLEWARE = [
    ...
    "telegram_error_logger.log.Exception",
    ...
]

## .env
MODULE_NAME=CORE
TELEGRAM_GROUP_ID=-123456789
TELEGRAM_BOT_TOKEN=your_bot_token


python setup.py sdist bdist_wheel
twine upload dist/*
