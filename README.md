## Foodastic (yandex-practicum-project)
![Foodastic workflow](https://github.com/anay2103/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Foodastic - онлайн сервис для публикации кулинарных рецептов. Пользователи могут создавать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное» и скачивать список продуктов для приготовления выбранных блюд.

Проект доступен по адресу: http://foodastic.co.vu

Документация с описанием API endpoints проекта размещена [здесь](http://foodastic.co.vu/api/docs/)

### Установка и начало работы:
1. Установите Docker согласно [инструкции для вашей ОС](https://docs.docker.com/engine/install/). 
2. Склонируйте данный репозиторий: 
   ```
   git@github.com:anay2103/foodgram-project-react.git
   ```
3. При необходимости измените настройки Django-приложения.   
  Создайте файл `.env` в корневой директории проекта и укажите в нем следующие переменные:
   * `DEBUG` - True/False для debug-режима
   * `ALLOWED_HOSTS`- список адресов по которым приложение принимает запросы. Для запуска на локальной машине укажите localhost;
   * `SECRET_KEY` - уникальный секретный ключ для установки Django;
  
4. Для работы с приложением используйте следующие команды в [директории infra](infra):
   * Запуск контейнеров: 
     ```
     docker-compose up
     ```
   * Создание миграций Django: 
     ```
     docker-compose exec infra_web_1 python manage.py makemigrations
     ```
   * Применение миграций Django:  
     ```
     docker-compose exec infra_web_1 python manage.py migrate
     ```
   * Создание суперюзера Django: 
     ```
     docker-compose exec infra_web_1 python manage.py createsuperuser
     ```
   * Сборка статических файлов проекта: 
     ```
     docker-compose exec infra_web_1 python manage.py collectstatic --no-input
     ``` 
   * Загрузка исходных данных из файла в БД (файл с данными есть в репозитории): 
     ```
     docker-compose exec infra_web_1 python manage.py  loaddata < dump.json
     ```
   * Остановка контейнеров: 
     ```
     docker-compose down
     ```
### Развитие проекта
Пулл-реквесты приветствуются, также любые предложения по доработке/развитию проекта автор с благодарностью примет по адресу: <yana-karausheva@yandex.ru>
