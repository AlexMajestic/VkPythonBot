import env
import vk_api
import vk_api.bot_longpoll as poller
from random import randint
from cities_game import CitiesGame

current_users_activity = dict()

class VkBot:
    def __init__(self, group_id, token):
        self.vk_api_object = vk_api.VkApi(token=token)
        self.vk_bot_watcher = poller.VkBotLongPoll(self.vk_api_object, group_id=group_id)
        self.api = self.vk_api_object.get_api()

    def watch(self):
        for event in self.vk_bot_watcher.listen():
            if event.type == poller.VkBotEventType.MESSAGE_NEW:
                if event.object.peer_id not in current_users_activity:
                    current_users_activity[event.object.peer_id] = 'CHAT'

                if event.object.text.upper() == 'ИГРА' or current_users_activity[event.object.peer_id] == 'PLAY':
                    current_users_activity[event.object.peer_id] = 'PLAY'
                    game = CitiesGame(event.object.peer_id, current_users_activity)
                    self.sendMessage(event.object.peer_id, game.turn(event.object.text))
                else:
                    self.sendMessage(event.object.peer_id, 'Привет! Я бот, который пока умеет только играть в города. Напиши мне "Игра", чтобы начать!')
            else:
                print('Данное событие пока не обрабатывается системой')

    def sendMessage(self, user_id, message):
        try:
            self.api.messages.send(
                peer_id=user_id,
                random_id=randint(0, 2 ** 20),
                message=message
            )
        except Exception as error:
            with open('logs/send_error.txt', 'a', encoding='utf8') as log:
                log.write(f'При отправке пользоваветлю {user_id} возникла ошибка: {error}')

vk_bot = VkBot(group_id=env.group_id, token=env.token)
vk_bot.watch()