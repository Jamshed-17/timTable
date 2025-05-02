# Используем официальный образ Python
FROM python:3.12.7

# Копируем файл с зависимостями
COPY requirements.txt requirements.txt

# Обновляем pip перед установкой зависимостей
RUN pip install --upgrade pip

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Запускаем приложение
CMD ["python", "TeleMain.py"]