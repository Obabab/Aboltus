# Пояснение к настройке PostgreSQL в docker-compose

## Сервис `db`

```yaml
db:
```
- Имя сервиса в docker-compose. Используется для ссылок внутри других сервисов.

```yaml
  image: postgres:15-alpine
```
- Используемый Docker-образ PostgreSQL версии 15 на базе легковесного дистрибутива Alpine.

```yaml
  container_name: postgres_db
```
- Явное имя контейнера. Удобно при отладке или обращении вручную (`docker exec -it postgres_db bash`).

```yaml
  restart: unless-stopped
```
- Перезапуск контейнера, если он упал, за исключением случаев, когда контейнер был остановлен вручную.

### Переменные окружения:

```yaml
  environment:
    POSTGRES_DB: mydatabase
```
- Название создаваемой базы данных по умолчанию.

```yaml
    POSTGRES_USER: postgres
```
- Имя пользователя PostgreSQL.

```yaml
    POSTGRES_PASSWORD: laygon
```
- Пароль для пользователя `postgres`.

```yaml
    POSTGRES_INITDB_ARGS: "--encoding=UTF8"
```
- Аргументы, передаваемые при инициализации базы. Здесь указывается кодировка UTF-8.

```yaml
    LANG: en_US.UTF-8
    LC_ALL: en_US.UTF-8
```
- Языковые настройки окружения внутри контейнера (локаль).

```yaml
    PGDATA: /var/lib/postgresql/data/pgdata
```
- Путь к директории, где будут храниться данные PostgreSQL.

### Хранилище (тома):

```yaml
  volumes:
    - postgres_data:/var/lib/postgresql/data
```
- Монтирование тома `postgres_data` в директорию PostgreSQL. Обеспечивает сохранение данных между перезапусками контейнера.

### Сетевые настройки:

```yaml
  ports:
    - "5432:5432"
```
- Проброс порта PostgreSQL наружу. Внешний порт 5432 → внутренний 5432 (стандартный порт PostgreSQL).

### Проверка состояния:

```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d mydatabase"]
```
- Команда для проверки, готов ли сервер к подключению.

```yaml
    interval: 5s
    timeout: 5s
    retries: 10
    start_period: 10s
```
- Параметры healthcheck:
  - `interval`: интервал между проверками.
  - `timeout`: максимальное время выполнения проверки.
  - `retries`: число попыток перед пометкой контейнера как "нездоровый".
  - `start_period`: время ожидания перед началом проверок после старта контейнера.

```yaml
  networks:
    - app_network
```
- Участие в пользовательской сети `app_network`, используется для связи с другими сервисами.

```yaml
  hostname: db
```
- Имя хоста внутри Docker-сети. Можно обращаться к этому контейнеру по имени `db`.

```yaml
  command: postgres -c 'max_connections=1000'
```
- Запуск PostgreSQL с переопределением параметра конфигурации: максимум 1000 одновременных подключений.
