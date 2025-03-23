import os
import requests
import time

class WNAGet:
    def __init__(self):
        self.password = "PA3MA3AH_P3M00"
        self.authenticated = False
        self.link = None
        self.number = None
        self.server_url = "http://localhost:5000"  # URL сервера для взаимодействия с wnastart

    def authenticate(self, password):
        if password == self.password:
            self.authenticated = True
            print("Доступ успешно разблокирован.")
        else:
            print("Вы ввели не корректный пароль, попробуйте ввести его заново через команду wnaget (пароль).")

    def message_users(self):
        if not self.authenticated:
            print("Сначала введите пароль через команду wnaget (пароль).")
            return

        # Отправка запроса на сервер для уведомления пользователей
        response = requests.post(f"{self.server_url}/notify")
        if response.status_code == 200:
            data = response.json()
            print(f"Уведомлено пользователей: {data['total_users']}")
            print(f"Зарегистрировано устройств: {data['approved_users']}")
            print(f"Не зарегистрировано устройств: {data['unapproved_users']}")
        else:
            print("Ошибка при уведомлении пользователей.")

    def launch(self):
        if not self.authenticated:
            print("Сначала введите пароль через команду wnaget (пароль).")
            return

        print("Выберете след. пункт:")
        print("1. Select link")
        print("2. Select number")
        print("3. Start launch")

        choice = input("> ")

        if choice == "1":
            self.link = input("Введите ссылку: ")
            print(f"Выберете след. пункт:")
            print(f"1. Select link: {self.link}")
            print("2. Select number")
            print("3. Start launch")
        elif choice == "2":
            self.number = input("Введите число: ")
            print(f"Выберете след. пункт:")
            print(f"1. Select link: {self.link}")
            print(f"2. Select number: {self.number}")
            print("3. Start launch")
        elif choice == "3":
            if not self.link or not self.number:
                print("Сначала выберите ссылку и число.")
                return

            # Отправка запроса на сервер для запуска задач
            payload = {"link": self.link, "number": self.number}
            response = requests.post(f"{self.server_url}/launch", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("Запуск программы на всех устройствах с указанными параметрами:")
                print(f"Зарегистрировано устройств: {data['approved_users']}")
                print(f"Не зарегистрировано устройств: {data['unapproved_users']}")
                print("Запуск")
                print(f"Успешно запущено устройств с указанными параметрами: {data['approved_users']}")
                print(f"Не успешно запущено устройств с указанными параметрами: {data['unapproved_users']}")
            else:
                print("Ошибка при запуске задач.")

def main():
    wnaget = WNAGet()
    while True:
        command = input("* ")
        if command.startswith("wnaget"):
            password = command.split(" ")[1]
            wnaget.authenticate(password)
        elif command == "Message users":
            wnaget.message_users()
        elif command == "Launch":
            wnaget.launch()
        else:
            print("Неизвестная команда.")