import _env
import vk_api
import vk_api.bot_longpoll as poller
import json
from random import randint
from cities_game import CitiesGame

current_users_activity = dict()

class VkBot:
    def __init__(self, group_id, token):
        self.vk_api_object = vk_api.VkApi(token=token)
        self.vk_bot_watcher = poller.VkBotLongPoll(self.vk_api_object, group_id=group_id)
        self.api = self.vk_api_object.get_api()

        # Определение констант клавиатуры
        self.KEYBOARD_START = 1  # Основная клавиатура при первом обращении к боту
        self.KEYBOARD_CITIES_PLAY = 2  # Кливиатура с подсказками для игры в "Города"

    def watch(self):
        for event in self.vk_bot_watcher.listen():
            if event.type == poller.VkBotEventType.MESSAGE_NEW:
                if event.object.peer_id not in current_users_activity:
                    current_users_activity[event.object.peer_id] = 'CHAT'

                print(event.object)

                if event.object.text.upper() == 'Закончить игру'.upper() and current_users_activity[event.object.peer_id] == 'PLAY':
                    current_users_activity[event.object.peer_id] = 'CHAT'
                    game = CitiesGame(user_id=event.object.peer_id, current_users_activity=current_users_activity)
                    game.reset()
                    self.sendMessage(
                        user_id=event.object.peer_id,
                        message='Отлично поиграли, спасибо!',
                        keyboard_id=self.KEYBOARD_START
                    )
                elif event.object.text.upper() == 'Нужна подсказка'.upper() and current_users_activity[event.object.peer_id] == 'PLAY':
                    game = CitiesGame(user_id=event.object.peer_id, current_users_activity=current_users_activity)
                    self.sendMessage(
                        user_id=event.object.peer_id,
                        message=f'Ну хорошо, я помогу. Как насчет {game.choose_city(is_hint=True)}?',
                        keyboard_id=self.KEYBOARD_CITIES_PLAY
                    )
                else:
                    if event.object.text.upper() == 'ИГРА' or current_users_activity[event.object.peer_id] == 'PLAY':
                        current_users_activity[event.object.peer_id] = 'PLAY'
                        game = CitiesGame(user_id=event.object.peer_id, current_users_activity=current_users_activity)
                        self.sendMessage(
                            user_id=event.object.peer_id,
                            message=game.turn(event.object.text),
                            keyboard_id=self.KEYBOARD_CITIES_PLAY
                        )
                    else:
                        self.sendMessage(
                            user_id=event.object.peer_id,
                            message='Привет! Я бот, который пока умеет только играть в города. Напиши мне "Игра", чтобы начать!',
                            keyboard_id=self.KEYBOARD_START
                        )
            else:
                print('Данное событие пока не обрабатывается системой')

    def sendMessage(self, user_id, message, keyboard_id=None):
        try:
            self.api.messages.send(
                peer_id=user_id,
                random_id=randint(0, 2 ** 20),
                message=message,
                keyboard=self.get_keyboard(keyboard_id)
            )
        except Exception as error:
            with open('logs/send_error.txt', 'a', encoding='utf8') as log:
                log.write(f'При отправке пользоваветлю {user_id} возникла ошибка: {error}\n')

    def get_keyboard(self, keyboard_id):
        if keyboard_id == self.KEYBOARD_START:
            return json.dumps({
                "one_time": True,
                "buttons": [
                    [
                        {
                            "action":
                            {
                                "type": "text",
                                "label": "Игра"
                            },
                            "color": "primary"
                        }
                    ]
                ]
            })
        elif keyboard_id == self.KEYBOARD_CITIES_PLAY:
            return json.dumps({
                "one_time": True,
                "buttons": [
                    [
                        {
                            "action":
                                {
                                    "type": "text",
                                    "label": "Нужна подсказка"
                                },
                            "color": "secondary"
                        },
                        {
                            "action":
                                {
                                    "type": "text",
                                    "label": "Закончить игру"
                                },
                            "color": "secondary"
                        }
                    ]
                ]
            })
        return "{}"


vk_bot = VkBot(group_id=_env.group_id, token=_env.token)
vk_bot.watch()