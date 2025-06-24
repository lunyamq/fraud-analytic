# Fraud Analytic
Fraud Analytic — это потоковая система обнаружения мошенничества в финансовых транзакциях.
Она использует Apache Kafka для получения данных, Apache Spark ML для обработки и предсказания, а Cassandra для хранения результатов.
Модель машинного обучения обучается на датасете с Kaggle и оценивает вероятность мошенничества в реальном времени.
Результаты доступны через Flask API, которые можно визуализировать с помощью Power BI.

## Установка и запуск
1. Копируем репозиторий:
```bash
git clone https://github.com/lunyamq/fraud-analytic.git
cd fraud-analytic
```
2. Запускаем Docker и собираем контейнеры:
```bash
docker-compose up --build
```
3. Подключаемся к Cassandra:
```bash
docker exec -it fraud-analytic-cassandra-1 cqlsh
```
4. Добавляем keyspace и таблицу:
```sql
CREATE KEYSPACE IF NOT EXISTS fraud
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS fraud.alerts (
    time double,
    amount double,
    fraud_probability double,
    prediction double,
    clazz double,
    PRIMARY KEY (time, amount)
);
```
5. В новом терминале заходим в контейнер processor:
```bash
docker exec -it fraud-analytic-processor-1 bash
```
6. Скачиваем dataset:
```bash
./download.sh
```
7. Обучаем модель:
```bash
spark-submit model_training.py
```
8. Запускаем `producer.py`:
```bash
python3 producer.py
```
9. В новом терминале снова заходим в контейнер processor:
```bash
docker exec -it fraud-analytic-processor-1 bash
```
10. Запускаем `consumer.py`:
```bash
./sparkrun.sh consumer.py
```
11. После завершения работы producer.py проверяем результаты в Cassandra:
```sql
SELECT * FROM fraud.alerts;
```

## Веб-интерфейсы
1. Dashboard (Мониторинг мошеннических операций в реальном времени):
Веб-интерфейс на Flask с визуализацией последних данных о мошеннических операциях. 
Отображает динамику вероятности мошенничества по времени с помощью графиков Chart.js, таблицу последних транзакций и статистику (количество операций, среднюю вероятность, сумму).  
Адрес: http://localhost:5000

2. Flask API (Просмотр данных о мошенничестве):
Flask-сервер предоставляет простой API для доступа к данным из Cassandra. Возвращает JSON с записями из таблицы fraud.alerts.
Адрес: http://localhost:5000/fraud

Пример ответа:
```json
[
  {
    "amount": 316.06,
    "clazz": 1.0,
    "fraud_probability": 0.9089357093357741,
    "prediction": 1.0,
    "time": 93853.0
  }
]
```

3. Spark UI (Мониторинг заданий):
После запуска контейнеров вы можете отслеживать выполнение Spark-задач через веб-интерфейс.
Адрес: http://localhost:8080

Что можно посмотреть:
* Активные и завершенные задания (Jobs)
* Распределение ресурсов между исполнителями (Executors)
* Логи выполнения задач (Stages)

## Авторы
- [@lunyamq](https://github.com/lunyamq)
- [@UsachevDev](https://github.com/UsachevDev)
