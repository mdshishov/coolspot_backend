# Backend проекта «Сайт ресторана»

[Deploy](https://github.com/mdshishov/coolspot_deploy) | [Frontend](https://github.com/mdshishov/coolspot_frontend)

Backend-часть веб-приложения ресторана. Реализованы CRUD-операции для управления блюдами, пользователями, корзинами и заказами. Настроена административная панель с разграничением прав доступа для различных групп пользователей. Подготовлена API-документация для интеграции с [frontend](https://github.com/mdshishov/coolspot_frontend), поддерживающая просмотр и отправку тестовых запросов из браузера без использования стороннего ПО.


## Технологический стек

* **Python 3.12+** – основной язык разработки.
* **Django 6.0.5** — backend-фреймворк.
* **Django REST Framework 3.17.1** — разработка REST API.
* **PostgreSQL 16** — система управления базами данных.
* **Simple JWT** — аутентификация и авторизация пользователей.
* **drf-spectacular (OpenAPI / Swagger UI)** — API-документации и ручное тестирование запросов.


## Запуск проекта

### Предварительные требования
Перед началом убедитесь, что на вашем компьютере установлены следующие инструменты:
* **Python 3.12+**
* **PostgreSQL 16**
* **pgAdmin 4** (опционально, для более удобной работы с БД)

### 1. Клонирование и установка зависимостей
```bash
git clone https://github.com/mdshishov/coolspot_backend.git
cd coolspot_backend
pip install -r requirements.txt
```

### 2. Создание базы данных
Создать новую БД можно через консоль или графический интерфейс pgAdmin 4 (если он установлен). Ниже приведены команды для работы через консоль.

```bash
# Подключение к PostgreSQL (пользователь по умолчанию – postgres)
psql -U <username>

# Создание базы данных
CREATE DATABASE coolspot_db;

# Выход из консоли
\q
```

### 3. Настройка файла окружения
В корне проекта найдите файл `.env.exaple` и создайте на его основе копию с именем `.env` в той же директории.

```bash
# Через консоль
cp .env.example .env
```

Заполните в `.env` данные для подключения к PostgreSQL (замените значения на свои).
```
DEBUG=True

SECRET_KEY='<your_key>'

DB_NAME=coolspot_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

Для генерации `SECRET_KEY` можно воспользоваться следующей командой:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Применение миграций и создание администратора
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Локальный запуск
```bash
python manage.py runserver
```
После запуска будут доступны:
* Панель администратора – http://127.0.0.1:8000/admin/
* API-документация – http://127.0.0.1:8000/api/docs/


## Работа с API

> [!IMPORTANT]  
> API прежде всего ориентировано на [frontend-часть](https://github.com/mdshishov/coolspot_frontend) для клиентов, поэтому для тестирования всех эндпоинтов лучше создать учётную запись клиента. Это можно сделать через [панель администратора](http://127.0.0.1:8000/admin/) (добавить нового пользователя в таблицу «Пользователи» с ролью «Клиент») или отправить [POST-запрос на `/api/auth/register/`](http://127.0.0.1:8000/api/docs/#/auth/auth_register_create) через интерфейс [API-документации](http://127.0.0.1:8000/api/docs/).

### Настройка JWT-авторизации
Отправьте [POST-запрос на `/api/auth/login/`](http://127.0.0.1:8000/api/docs/#/auth/auth_login_create) с данными авторизации зарегистрированного клиента (в поле `username` укажите номер телефона).

При успешной авторизации сервер вернёт JSON вида:
```json
{
  "refresh": "eyJhb...",
  "access": "eyJhb...",
  "role": "client"
}
```

1. Целиком скопируйте значение поля `access`.
2. Нажмите на кнопку **Authorize** в правом верхнем углу, вставьте токен в открывшееся поле и подтвердите авторизацию.

Теперь при отправке запросов токен доступа будет указываться автоматически.
