import telebot
import requests
import time
import os
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

additional_card_taken = False
dealer_visible_card_url = None
deck_id = None
player_cards = []
dealer_cards = []

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    welcome_message = """
    Привет! Я блекджек бот. Для начала игры в блекджек введите команду /game.
    """
    markup = types.InlineKeyboardMarkup()
    game_button = types.InlineKeyboardButton("Начать игру", callback_data='start_game')
    markup.add(game_button)

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)


def get_deck_id(deck_count):
    response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}")
    if response.status_code == 200:
        data = response.json()
        return data['deck_id']
    else:
        return None


@bot.message_handler(commands=['game'])
def start_game(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.KeyboardButton('Европейский блекджек'))
    msg = bot.send_message(message.chat.id, "Выберите тип блекджека:", reply_markup=markup)
    bot.register_next_step_handler(msg, choose_deck_count)


def get_initial_cards(deck_id, num_cards):
    url = f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={num_cards}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if 'cards' in data:
            return data['cards']
        else:
            print("Error: 'cards' key not found in the response.")
            return None
    else:
        print(f"Error: Unable to draw cards. Status code: {response.status_code}")
        return None


def get_card_value(card):
    if card['value'] not in ['ACE', 'JACK', 'QUEEN', 'KING']:
        return int(card['value'])
    elif card['value'] in ['JACK', 'QUEEN', 'KING']:
        return 10
    else:  # Туз
        return 11


def show_player_cards(message):
    global player_cards
    time.sleep(1)
    bot.send_message(message.chat.id, "Ваши карты:")

    photo_urls = []
    for card in player_cards:
        if isinstance(card, dict) and 'image' in card:
            photo_urls.append(card['image'])
        else:
            bot.send_message(message.chat.id, "Error: Invalid card data.")

    if photo_urls:
        media = [types.InputMediaPhoto(media=url) for url in photo_urls]
        bot.send_media_group(message.chat.id, media)

    player_total_value = calculate_total_value(player_cards)
    time.sleep(2)
    bot.send_message(message.chat.id, f"Общее Значение ваших карт: {player_total_value}")
    time.sleep(1)


def calculate_total_value(cards):
    total_value = 0
    for card in cards:
        if 'value' in card and card['value'] not in ['ACE', 'JACK', 'QUEEN', 'KING']:
            total_value += int(card['value'])
        elif card['value'] in ['JACK', 'QUEEN', 'KING']:
            total_value += 10
        else:
            total_value += 11 if total_value + 11 <= 21 else 1

    return total_value


def get_player_decision_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Взять карту"))
    markup.add(types.KeyboardButton("Остановиться"))
    return markup


def choose_deck_count(message):
    if message.text == 'Европейский блекджек':
        time.sleep(1)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(types.KeyboardButton('1 колода'), types.KeyboardButton('2 колоды'), types.KeyboardButton('4 колоды'),
                   types.KeyboardButton('6 колод'))
        msg = bot.send_message(message.chat.id, "Выберите количество колод:", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda msg: start_blackjack_game(msg))
    else:
        time.sleep(1)
        bot.send_message(message.chat.id, "Пока доступен только европейский блекджек. Пожалуйста, выберите его.")


def start_blackjack_game(message):
    global deck_id, player_cards, dealer_visible_card_url
    global dealer_cards, player_decision_message_id, player_decision_chat_id

    deck_count = int(message.text.split()[0])

    deck_id = get_deck_id(deck_count)

    player_cards = get_initial_cards(deck_id, 2)

    if calculate_total_value(player_cards) > 21:
        time.sleep(1)
        bot.send_message(message.chat.id, "Дилер выиграл. Игрок превысил 21.")
        return
        end_game(message)

    dealer_cards = get_initial_cards(deck_id, 2)

    dealer_visible_card_url = dealer_cards[0]['image']
    hidden_dealer_card = 'https://deckofcardsapi.com/static/img/back.png'
    bot.send_message(message.chat.id, "Карта дилера:")
    time.sleep(2)
    media_group = [
        types.InputMediaPhoto(media=dealer_visible_card_url),
        types.InputMediaPhoto(media=hidden_dealer_card)
    ]
    bot.send_media_group(message.chat.id, media=media_group)
    time.sleep(1)
    bot.send_message(message.chat.id, f"Значение карты дилера: {get_card_value(dealer_cards[0])}")
    time.sleep(1)
    show_player_cards(message)
    time.sleep(1)
    bot.send_message(message.chat.id, "Ваш ход. Выберите действие:", reply_markup=get_player_decision_markup())
#111

@bot.message_handler(func=lambda message: True)
def handle_player_decision(message):
    global deck_id, player_cards, dealer_cards, dealer_visible_card_url, additional_card_taken
    deck_count = 6
    deck_id = get_deck_id(deck_count)
    if message.text.lower() == 'взять карту':
        additional_cards = get_initial_cards(deck_id, 1)

        if isinstance(additional_cards, list) and len(additional_cards) > 0:
            additional_card = additional_cards[0]
            player_cards.append(additional_card)
            additional_card_taken = True

            time.sleep(1)
            bot.send_message(message.chat.id, "Вы взяли карту")
            time.sleep(1)
            bot.send_photo(message.chat.id, additional_card['image'])
            time.sleep(1)
            show_player_cards(message)

            if calculate_total_value(player_cards) > 21:
                time.sleep(1)
                bot.send_message(message.chat.id, "Дилер выиграл. Игрок превысил 21.")
                end_game(message)

    elif message.text.lower() == 'остановиться':
        additional_card_taken = True
        time.sleep(1)
        bot.send_message(message.chat.id, "Вы решили остановиться. Ход дилера.")
        time.sleep(1)
        while calculate_total_value(dealer_cards) < 17:
            additional_card = get_initial_cards(deck_id, 1)[0]
            dealer_cards.append(additional_card)
            time.sleep(1)
            bot.send_message(message.chat.id, "Дилер взял карту.")
            time.sleep(1)
            bot.send_photo(message.chat.id, additional_card['image'])
            time.sleep(1)

        bot.send_message(message.chat.id, "Итоговые карты дилера:")
        time.sleep(1)
        show_dealer_cards(message)
        time.sleep(1)
        determine_winner(message)

        end_game(message)


def show_dealer_cards(message):
    global dealer_cards
    media_group = [types.InputMediaPhoto(media=card['image']) for card in dealer_cards]
    bot.send_media_group(message.chat.id, media=media_group)
    time.sleep(1)
    bot.send_message(message.chat.id, f"Значение карт дилера: {calculate_total_value(dealer_cards)}")


def determine_winner(message):
    global player_cards, dealer_cards
    player_total_value = calculate_total_value(player_cards)
    dealer_total_value = calculate_total_value(dealer_cards)

    if player_total_value > 21:
        time.sleep(1)
        bot.send_message(message.chat.id, "Дилер выиграл. Игрок превысил 21.")
    elif dealer_total_value > 21:
        time.sleep(1)
        bot.send_message(message.chat.id, "Игрок выиграл. Дилер превысил 21.")
    elif player_total_value > dealer_total_value:
        time.sleep(1)
        bot.send_message(message.chat.id, "Игрок выиграл. Поздравляем!")
    elif player_total_value < dealer_total_value:
        time.sleep(1)
        bot.send_message(message.chat.id, "Дилер выиграл. Увы, попробуйте еще раз.")
    else:
        time.sleep(1)
        bot.send_message(message.chat.id, "Ничья! Попробуйте еще раз.")


def get_new_deck():
    global deck_id
    new_deck_url = "https://deckofcardsapi.com/api/deck/new/"
    response = requests.get(new_deck_url)
    data = response.json()
    if data.get('success'):
        deck_id = data['deck_id']
        return True
    return False


def start_new_game(message):
    global deck_id, player_cards, dealer_visible_card_url
    time.sleep(1)
    bot.send_message(message.chat.id, "Новая игра начинается!")
    choose_deck_count(message)


def end_game(message):
    markup = types.InlineKeyboardMarkup()
    new_game_button = types.InlineKeyboardButton("Начать новую игру", callback_data='new_game')
    exit_button = types.InlineKeyboardButton("Выйти из игры", callback_data='exit_game')
    markup.row(new_game_button, exit_button)
    time.sleep(1)
    bot.send_message(message.chat.id, "Игра закончилась. Выберите действие.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'start_game':
        start_game(call.message)
    elif call.data == 'new_game':
        start_game(call.message)
    elif call.data == 'exit_game':
        time.sleep(1)
        bot.send_message(call.message.chat.id, "Вы вышли из игры. Для новой игры введите команду /game.")


bot.polling()