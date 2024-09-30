# server.py - Сервер, который управляет дроном через WebSocket-соединение

import asyncio  # Библиотека для асинхронного программирования
import websockets  # Библиотека для работы с WebSocket
import jwt  # Библиотека для работы с JWT-токенами
import datetime  # Библиотека для работы с датами и временем
import logging  # Библиотека для логирования
from abc import ABC, abstractmethod  # Абстрактные классы для паттерна Command
from flask import Flask, render_template, request, jsonify  # Библиотека Flask для создания веб-приложения
from flask_cors import CORS  # Библиотека CORS для разрешения кросс-доменных запросов
import time  # Библиотека для работы со временем
import cProfile  # Импортируем cProfile

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Адрес WebSocket-сервера
SERVER_URL = "ws://localhost:8765"
# Секретный ключ для JWT-токенов
SECRET_KEY = 'my_secret_key'

# Словарь для хранения подключенных дронов
connected_drones = {}

class JWTManager:
    # Класс для управления JWT-токенами
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def create_jwt_token(self, username):
        # Создает JWT-токен с именем пользователя и временем истечения
        payload = {
            'username': username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_jwt_token(self, token):
        # Проверяет JWT-токен на действительность и возвращает имя пользователя, если токен действителен
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["username"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

#  Реализация паттерна Command
class Command(ABC):
    # Абстрактный класс для всех команд
    @abstractmethod
    def execute(self):
        # Метод, который выполняет команду
        pass


class Drone:
    # Класс, представляющий дрон
    def take_off(self):
        logging.info("Command - Drone is taking off")
        # Логика взлета

    def land(self):
        logging.info("Command - Drone is landing")
        # Логика посадки

    def patrol(self):
        logging.info("Command - Drone is patrolling")
        # Логика патрулирования

    def capture_photo(self):
        logging.info("Command - Drone is capturing a photo")
        # Логика фотосъемки

    def record_video(self):
        logging.info("Command - Drone is recording a video")
        # Логика записи видео

class TakeOffCommand(Command):
    # Команда для взлета дрона
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self):
        self._drone.take_off()


class LandCommand(Command):
    # Команда для посадки дрона
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self):
        self._drone.land()

class PatrolCommand(Command):
    # Команда для патрулирования дрона
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self):
        self._drone.patrol()

class CapturePhotoCommand(Command):
    # Команда для фотосъемки дрона
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self):
        self._drone.capture_photo()

class RecordVideoCommand(Command):
    # Команда для записи видео дроном
    def __init__(self, drone: Drone):
        self._drone = drone

    def execute(self):
        self._drone.record_video()

class RemoteControl:
    # Класс для управления дроном
    def __init__(self):
        self._commands = []  # Список команд
        self._history = []  # История выполненных команд
        self._drone = None  # Ссылка на дрон

    def set_drone(self, drone):
        # Устанавливает ссылку на дрон
        self._drone = drone

    def add_command(self, command: Command):
        # Добавляет команду в список команд
        self._commands.append(command)

    def execute_command(self):
        # Выполняет все команды в списке команд
        for command in self._commands:
            command.execute()
            self._history.append(command)
        self._commands.clear()

# Создаем объект JWTManager
jwt_manager = JWTManager(SECRET_KEY)
# Создаем объект RemoteControl
remote_control = RemoteControl()

async def handle_client(websocket, path):
    # Асинхронная функция, которая обрабатывает соединения WebSocket от клиента
    async for data in websocket:
        # Цикл, который обрабатывает входящие данные от клиента
        if data.startswith("LOGIN:"):
            # Обработка сообщения логина
            username, password = data[6:].split(",")
            logging.info(f"Login attempt: {username}, {password}")

            if username in connected_drones.keys():
                # Проверка, подключен ли дрон с таким именем
                await websocket.send("ERROR: Drone already connected.")
                return

            # Проверка аутентификации
            token = jwt_manager.create_jwt_token(username)
            await websocket.send(f"JWT:{token}")
            logging.info(f"Token sent: {token}")

            connected_drones[username] = websocket
            logging.info(f"Drone {username} connected.")
            #  Оповещение в server.py
            print(f"Drone {username} connected.")

            # Создание объекта Drone
            drone = Drone()  # Без AirDrone IP
            remote_control.set_drone(drone)

        elif data.startswith("COMMAND:"):
            # Обработка сообщения с командой
            command = data.split(":")[1].strip()
            logging.info(f"Received command: {command}")

            # Логика обработки команд
            if command == "takeoff":
                remote_control.add_command(TakeOffCommand(remote_control._drone))
                remote_control.execute_command()
                response = "Drone is taking off"
            elif command == "land":
                remote_control.add_command(LandCommand(remote_control._drone))
                remote_control.execute_command()
                response = "Drone is landing"
            elif command == "patrol":
                remote_control.add_command(PatrolCommand(remote_control._drone))
                remote_control.execute_command()
                response = "Drone is patrolling"
            elif command == "capture_photo":
                remote_control.add_command(CapturePhotoCommand(remote_control._drone))
                remote_control.execute_command()
                response = "Drone captured a photo"
            elif command == "record_video":
                remote_control.add_command(RecordVideoCommand(remote_control._drone))
                remote_control.execute_command()
                response = "Drone is recording a video"
            else:
                response = f"Unknown command: {command}"
            logging.info(response)

            await websocket.send(f"STATUS_UPDATE: {username}: {response}")

        else:
            await websocket.send("ERROR: Unknown command.")

app = Flask(__name__)

# Включаем CORS для приложения Flask
CORS(app)

@app.route('/')
# Главная страница веб-приложения
def index():
    return render_template('index.html')



async def main():
    # Запускает WebSocket-сервер
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    # Запускаем cProfile для профилирования
    with cProfile.Profile() as pr:
        app.run(debug=True)
        asyncio.run(main())
    # Выводим результаты профилирования в файл
    pr.print_stats(sort="cumulative")