# Бэкенд веб-сервиса бронирования жилья для путешествий на python3

Для выполнения задачи выбрал веб-фреймворк **tornado**, так как он:
1. асинхронный, неблокирующий
2. весьма производительный даже в синхронном режиме
3. имеет большое количество асинхронных драйверов для всех популярныъ диалектов SQL, а также NoSQL-хранилищ
4. достаточно популярный и хорошо документированный для поиска информации и устранения проблем
5. написанное приложение можно быстро запустить без конфигурирования каких-либо дополнительных прослоек между python-кодом и ОС (например, WSGI-контейнера)

Поскольку в качестве хранилища можно было выбрать исключительно реляционную СУБД, я остановился на **PostgreSQL**, так как у неё:
1. есть асинхронный драйвер для tornado (и даже не один; я остановился на самом популярном – **momoko**)
2. хороший функционал (аналитические функции, наследование, партиционирование итп)
3. более очевидный и удобный синтаксис, чем, например, у MS SQL / MySQL

Для нагрузочного тестирования выбрал утилиту для unix-систем **Siege**, т.к. она достаточно проста, удобна, есть много настраиваемых параметров для тестирования, позволяет оценить возможность конкурентного доступа к ресурсу со стороны клиентов.

##### Минусы:
1. tornado имеет более сложные конструкции, чем, например, Flask
2. если мы будем обязаны использовать MS SQL Server в качестве хранилища, для него нет асинхронного драйвера для tornado и создание высокопроизводительного микросервиса будет невозможным
3. конструкции по валидации параметров входящих HTTP-запросов от клиентов выглядят на мой взгляд несколько неэлегантно. Собственный валидатор в `decorators.py` написал умышленно (для tornado есть готовые решения, например, WTForms/Tornado tools, в рабочих проектах обычно использую JSONschema), т.к. поскольку это *тестовое задание*, хотел попробовать написать сам.
4. на текущий момент баланс можно посчитать не в любой заданной валюте, а лишь в рублёвом эквиваленте

##### Не успел:
* dockerfile
* веб-клиент
* больше тестов, более сложные проверки

### Результаты нагрузочного тестирования под Siege
Тестировал на рабочей машине, 1 процесс, без балансировщика. Результаты представлены ниже:  
Запрос баланса по партнёру с id=1 (500 000 транзакций)
```
$ siege http://localhost:3008/balance?partner_id=1
** SIEGE 3.0.5
** Preparing 20 concurrent users for battle.
The server is now under siege...
Lifting the server siege...      done.

Transactions:		         233 hits
Availability:		      100.00 %
Elapsed time:		        9.46 secs
Data transferred:	        0.00 MB
Response time:		        0.31 secs
Transaction rate:	       24.63 trans/sec
Throughput:		        0.00 MB/sec
Concurrency:		        7.71
Successful transactions:         233
Failed transactions:	           0
Longest transaction:	        0.56
Shortest transaction:	        0.14
```
Как следует из отчёта выше, максимальное время запроса баланса при конкурентном доступе составило **560 мс**, что удовлетворяет требованиям задачи.    
Произвольные запросы по конфигу:
```
$ siege -f siege-urls.txt -t10s -c 20
** SIEGE 3.0.5
** Preparing 20 concurrent users for battle.
The server is now under siege...
Lifting the server siege...      done.

Transactions:		         380 hits
Availability:		      100.00 %
Elapsed time:		        9.94 secs
Data transferred:	        0.53 MB
Response time:		        0.08 secs
Transaction rate:	       38.23 trans/sec
Throughput:		        0.05 MB/sec
Concurrency:		        3.22
Successful transactions:         380
Failed transactions:	           0
Longest transaction:	        0.59
Shortest transaction:	        0.00
```

### Структура проекта
* `templates`  
  * `web-client.html`  *веб-клиент (HTML+JS)*  
* `static`  
  * `style.css`        *стили для HMTL*  
* `loader.py`          *скрипт-генератор тестовых данных*  
* `requirements.txt`   *файл зависимостей для pip*  
* `siege-urls.txt`     *конфиг-файл для Siege*  
* `dockerfile`         *докерфайл (не готов)*  
* `decorators.py`      *валидатор входных данных*  
* `web.py`             *основной файл веб-приложения*  
* `tests.py`           *unit tests*  
* `ddl.sql`            *создание структуры БД, ограничений, партиций, тестовых партнёров*  

### Общие требования
* Ubuntu 14.04+
* Python 3.4.3+
* PostgreSQL DB 9.6+

### Установка необходимых фреймворков
`sudo pip3 install -r requirements.txt`

### Наполнение тестовыми данными
1. Создаём структуру: `psql ivan -h 127.0.0.1 -d ivan -a -f ddl.sql`
2. Наполняем тестовыми данными (500 000 транзакций): `python3 loader.py`

### Запуск приложения
`python3 web.py`

### Функциональные тесты
`python3 tests.py`

### Тестирование под нагрузкой
1. Устанавливаем unix-утилиту Siege: `sudo apt-get install siege --upgrade`
2. Запускаем тестирование на 10с с 20 пользователями: `siege -f siege-urls.txt -t10s -c 20`

