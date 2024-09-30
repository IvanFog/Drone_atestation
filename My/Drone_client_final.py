import asyncio  # Библиотека для асинхронного программирования
import websockets  # Библиотека для работы с WebSocket
import jwt  # Библиотека для работы с JWT-токенами
import datetime  # Библиотека для работы с датами и временем
import logging  # Библиотека для логирования
from abc import ABC, abstractmethod  # Абстрактные классы для паттерна Command
import cProfile

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Адрес WebSocket-сервера
SERVER_URL = "ws://localhost:8765"
# Секретный ключ для JWT-токенов
SECRET_KEY = 'my_secret_key'
# Имя пользователя для авторизации
USERNAME = 'drone1'
# Пароль для авторизации
PASSWORD = '333'

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

    def add_command(self, command: Command):
        # Добавляет команду в список команд
        self._commands.append(command)

    def execute_command(self):
        # Выполняет все команды в списке команд
        for command in self._commands:
            command.execute()
            self._history.append(command)
        self._commands.clear()

def create_jwt_token(username, secret_key):
    # Создает JWT-токен с именем пользователя и временем истечения
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }, secret_key, algorithm="HS256")
    return token

async def websocket_client():
    # Асинхронная функция, которая устанавливает соединение WebSocket с сервером
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            logging.info(f"Drone client connected to {SERVER_URL}")
            #  Оповещение в Drone_client.py
            print(f"Drone client connected to {SERVER_URL}")

            auth_message = f'LOGIN:{USERNAME},{PASSWORD}'
            await websocket.send(auth_message)

            auth_response = await websocket.recv()

            if auth_response.startswith("JWT:"):
                logging.info(f"Received JWT-token: {auth_response}")
                logging.info("Authorization successful. Waiting for commands...")

                while True:
                    try:
                        command_message = await websocket.recv()
                        logging.info(f"Received command: {command_message}")

                        if command_message.startswith("COMMAND:"):
                            command = command_message.split(":")[1]

                            if command == "takeoff":
                                response = "Drone is taking off"
                                remote_control.add_command(take_off)
                                remote_control.execute_command()

                            elif command == "land":
                                remote_control.add_command(land)
                                remote_control.execute_command()
                                response = "Drone is landing"
                            else:
                                response = f"Unknown command: {command}"
                            logging.info(response)

                            #  Убираем строку, которая отправляла статус на сервер
                            #  await websocket.send(f"STATUS_UPDATE: {USERNAME}: {response}")

                    except websockets.ConnectionClosedError:
                        logging.error("Connection with server lost.")
                        break

            else:
                logging.error("Authorization failed.")

    except ConnectionRefusedError:
        logging.error(f"Connection to {SERVER_URL} refused. Is the server running?")
    except Exception as e:
        logging.error(f"Error connecting to server: {e}")


drone = Drone()
land = LandCommand(drone)
take_off = TakeOffCommand(drone)
remote_control = RemoteControl()

if __name__ == "__main__":
    # Запускаем cProfile для профилирования
    with cProfile.Profile() as pr:
        asyncio.run(websocket_client())
    # Выводим результаты профилирования в файл
    pr.print_stats(sort="cumulative")