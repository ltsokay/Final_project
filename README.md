<<<<<<< HEAD
# Final Project

## Как запустить сервер

1. Убедитесь, что установлен Python 3
2. В терминале перейдите в папку с проектом
3. Запустите сервер:
   python3 server.py,
по умолчанию сервер слушает порт 8080 (можно изменить в коде)

## Пример с curl

### Получить список задач
curl http://localhost:8080/tasks

### Создать задачу
curl -X POST http://localhost:8080/tasks -H "Content-Type: application/json" -d '{"title":"Homework","priority":"normal"}'

### Отметить задачу выполненной (id=1)
curl -X POST http://localhost:8080/tasks/1/complete -i
