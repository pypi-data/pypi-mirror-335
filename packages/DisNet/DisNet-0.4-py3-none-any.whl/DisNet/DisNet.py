# Импорт модулей
import copy

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
    async def sendData(self, chanell, message):
        # Метод для отправки сообщений в дискорд
        chanell = bot.get_channel(chanell)
        await chanell.send(message)
# Класс для получения данных из дискорд
class GetData():
    def __init__(self):
        # Иницилизация переменных
        self.messagesList = []
    async def getData(self, chanell,  packedDataLength=1):
        # Метод пакующий определенное количество сообщений и возращающий их
        chanell = bot.get_channel(chanell)
        async for mes in chanell.history(limit=packedDataLength):
            self.messagesList.append(mes.content)
        result = copy.deepcopy(self.messagesList)
        self.messagesList = []
        return result

# Класс управления сообщениями
class MessagesManager():
    def __init__(self):
        pass
    async def clearMessages(self, chanell, messagesLength=1):
        # метод очищающий сообщения
        chanell = bot.get_channel(chanell)
        async for mes in chanell.history(limit=messagesLength):
            await mes.delete()
    async def aditMessages(self, chanell, messagesLength=None, messagesNum=None, newMessage=None):
        # Метод корректирующий сообщения
        chanell = bot.get_channel(chanell)
        if messagesLength != None:
            async for mes in chanell.history(limit=messagesLength):
                await mes.edit(content=newMessage)
        elif messagesNum != None:
            i = 0
            async for mes in chanell.history(limit=messagesNum):
                if i == messagesNum-1:
                    await mes.edit(content=newMessage)
                else:
                    i += 1

sendData = SendData()
getData = GetData()
messagesManager = MessagesManager()