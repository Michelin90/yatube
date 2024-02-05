![example workflow](https://github.com/Michelin90/yatube/actions/workflows/python-app.yml/badge.svg
# YaTube
Cоциальная сеть для ведения текстовых блогов с пользовательским web-интрефейсом.

Предоставляет следующие возможности:
- публикация постов, содержащих текст и изображения;
- просмотр и комментирование постов других авторов;
- подписка на авторов.

## Язык и инструменты:
[![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.2-blue?style=for-the-badge&logo=django)](https://www.djangoproject.com/)

## Автор:
Михаил [Michelin90](https://github.com/Michelin90) Хохлов

## Установка и запуск
### Клонировать репозиторий и перейти в него в командной строке:
```
https://github.com/Michelin90/https://github.com/Michelin90/yatube.git
```
```
cd yatube
```
### Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
```
source venv/Scripts/activate
```
### Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
### Создать в корневой папке проекта файл .env и добвить в него следующее:
```
SECRET_KEY=<ваш секретный ключ для django-проекта>
```
### Выполнить миграции:
```
python3 manage.py migrate
```
### Запустить проект:
```
python manage.py runserver
```

## Возможности пользователей

Зарегестриованный пользователь имеет возможность:
- публиковать, просматривать, редактировать, удалять свои публикации;
- подписываться на авторов других публикаций;
- просматривать информацию о сообществах;
- просматривать и публиковать комментарии к публикациям других пользователей (включая самого себя), удалять и редактировать свои комментарии.

Анонимный пользователь имеет возможность:
- просматривать публикации;
- просматривать информацию о сообществах;
- просматривать комментарии.
