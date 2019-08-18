import random
import inspect
import os.path

class CitiesGame:
    def __init__(self, user_id, current_users_activity):
        self.user_id = user_id
        self.current_users_activity = current_users_activity
        if self.user_id not in game_stats:
            game_stats[self.user_id] = {
                'used_cities': [],
                'status': 'start',
                'prev_letter': '',
                'errors_in_raw': 0
            }

    def turn(self, city_name):
        city_name = city_name.upper()

        if game_stats[self.user_id]['status'] == 'start':
            selected_city = self.choose_city(city_name)
            game_stats[self.user_id]['status'] = 'play'
            game_stats[self.user_id]['used_cities'].append(selected_city)
            game_stats[self.user_id]['prev_letter'] = self.get_accepted_last_char(selected_city)
            return f'Я начну! {selected_city.title()}. Тебе на "{game_stats[self.user_id]["prev_letter"]}"'
        else:
            # Проверяем, что указанный город не был использован ранее
            if city_name in game_stats[self.user_id]['used_cities']:
                game_stats[self.user_id]['errors_in_raw'] += 1
                return f'{city_name} уже было! Придумай другой город.'

            # Проверяем, что указанный город есть в списке городов
            if city_name not in cities[city_name[0]]:
                return 'Такого слова нет. Попробуй другое.'

            selected_city = self.choose_city(city_name)

            # Проверяем, что указанный город есть в списке и начинается на нужную букву
            if selected_city and city_name[0] != game_stats[self.user_id]['prev_letter']:
                return f'Не подойдет! Город должен начинаться на "{game_stats[self.user_id]["prev_letter"]}"'

            # Проверяем, что Бот смог найти следующее слово
            if not selected_city:
                self.reset()
                self.current_users_activity[self.user_id] = 'CHAT'
                return 'Поздравляю с победой! Я больше не знаю городов..'

            game_stats[self.user_id]['used_cities'].append(selected_city)
            game_stats[self.user_id]['prev_letter'] = self.get_accepted_last_char(selected_city)
            return f'{selected_city.title()}. Тебе на "{game_stats[self.user_id]["prev_letter"]}"'

    def choose_city(self, city_name=None, is_hint=False):
        """
        Метод для выбора следующего города на основе текущего города
        """
        if game_stats[self.user_id]['status'] == 'start':
            return random.choice(cities[chr(random.randint(1040, 1045))])

        if not is_hint:
            game_stats[self.user_id]['used_cities'].append(city_name)

        if is_hint:
            last_char = game_stats[self.user_id]['prev_letter']
        else:
            last_char = self.get_accepted_last_char(city_name)

        if last_char in cities:
            cities_variants = [city for city in cities[last_char] if city not in game_stats[self.user_id]['used_cities']]
            if len(cities_variants) > 0:
                return random.choice(cities_variants)

        return False

    def get_accepted_last_char(self, city_name):
        """
        Метод для определение следующего символа,
        по которому можно подобрать город
        """
        while city_name[-1] in ['Ь', 'Ъ', 'Ё', 'Ы']:
            city_name = city_name[:-1]

        return city_name[-1]

    def reset(self):
        game_stats.pop(self.user_id)


game_stats, cities = dict(), dict()
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.dirname(os.path.abspath(filename))
with open(path + '/resources/cities_game/cities.txt', 'r', encoding='utf8') as cities_file:
    for city in cities_file:
        if city[0] not in cities:
            cities[city[0]] = []
        cities[city[0]].append(city.upper().strip('\n'))