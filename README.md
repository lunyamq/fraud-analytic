# Fraud Analytic

## Установка
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
docker exec -it bin-cassandra-1 cqlsh
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
docker exec -it fraud-analitic-processor-1 bash
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
docker exec -it fraud-analitic-processor-1 bash
```
10. Запускаем `consumer.py`:
```bash
./sparkrun.sh consumer.py
```
11. После завершения работы producer.py проверяем результаты в Cassandra:
```sql
SELECT * FROM fraud.alerts;
```