# Импорт модулей
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
# Права бота
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
# Создание обьекта Bot
bot = commands.Bot(command_prefix="!", intents=intents)
# Загрудка ТОКЕНА из корня проекта
load_dotenv(dotenv_path="../.venv/.env")
TOKEN = os.getenv("DISTOKEN")
# Класс для передачи данных через дискорд
class SendData():
    def __init__(self):
        # Иницилизация переменных класса
        self.messagesList = []
    async def setup(self, ch_server):
        # Ждем запуск бота
        await bot.wait_until_ready()
        # Иницилизацая обьекта канала
        self.ch_server = bot.get_channel(ch_server)
    async def sendData(self, message, chanell):
        # Метод для отправки сообщений в дискорд
        chanell = bot.get_channel(chanell)
        await chanell.send(message)
    async def packagingDataUpdate(self, chanell, time=1, packedDataLength=2):
        # Метод постоянно пакующий определенное количество сообщений и возращающий их
        chanell = bot.get_channel(chanell)
        while True:
            async for mes in chanell.history(limit=packedDataLength):
                self.messagesList.append(mes)
            await asyncio.sleep(time)
            return self.messagesList
    async def joinUser(self):
        pass
    async def exitUser(self):
        pass
# Класс для получения данных из дискорд
class GetData():
    def __init__(self):
        # Иницилизация переменных
        self.messagesList = []
    async def getData(self, chanell, packedDataLength=1):
        # метод для получения сообщений
        chanell = bot.get_channel(chanell)
        async for mes in chanell.history(limit=packedDataLength):
            self.messagesList.append(mes)
        # Возращаем данные
        return self.messagesList
