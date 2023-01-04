import telebot
import discum
from sys import stderr
from loguru import logger
from config import telegram_token


logger.remove()
logger.add(stderr,
           format="<white>{time:HH:mm:ss}</white> | "
                  "<level>{level: <8}</level> | "
                  "<cyan>{line}</cyan> - "
                  "<white>{message}</white>")


tbot = telebot.TeleBot(telegram_token)  # TG bot
db = {'token': '', 'channel_id': '', 'user_id': ''}

logger.success('Tracker-Bot is working now')


@tbot.message_handler(commands=['start'])
def start_message(message):
    tbot.send_message(message.chat.id, 'Welcome to Tracker-Bot!')
    tbot.send_message(message.chat.id, 'Available commands:\n'
                                       '/stats - Check statistics\n'
                                       '/runbot - Start bot\n'
                                       '/stopbot - Stop bot\n'
                                       '/token EnterYourToken - Set discord token. Ex. (/token AsJlvprofDefeevlKdmr)\n'
                                       '/channel EnterYourChannelId - Set channel id. Ex. (/channel 1234567890123456)\n'
                                       '/user EnterYourUserId - Set user id. Ex. (/user 1234567890)\n')
    tbot.send_message(message.chat.id, 'Before you start, you need to configure the bot using the following commands: '
                                       '/token, /channel, /user')


@tbot.message_handler(commands=['token'])
def set_token(message):
    global dbot
    db['token'] = message.text[6:].strip()
    tbot.send_message(message.chat.id, f'Your discord token: {db["token"]}')
    dbot = discum.Client(token=db['token'], log=False)  # Discord bot
    dbot_run(message.chat.id)


@tbot.message_handler(commands=['channel'])
def set_channel_id(message):
    db['channel_id'] = message.text[8:].strip()
    tbot.send_message(message.chat.id, f'Your channel id: {db["channel_id"]}')


@tbot.message_handler(commands=['user'])
def set_user_id(message):
    db['user_id'] = message.text[5:].strip()
    tbot.send_message(message.chat.id, f'Your user id: {db["user_id"]}')


@tbot.message_handler(commands=['runbot'])
def run_bot(message):
    tbot.send_message(message.chat.id, 'Bot starting...')
    logger.success('Bot starting..')
    dbot.gateway.run(auto_reconnect=True)


@tbot.message_handler(commands=['stopbot'])
def stop_bot(message):
    tbot.send_message(message.chat.id, 'Bot stopping...')
    dbot.gateway.close()


@tbot.message_handler(commands=['stats'])
def check_stats(message):
    tbot.send_message(message.chat.id, f"Discord token: {db['token']}\n"
                                       f"Channel id: {db['channel_id']}\nUser id: {db['user_id']}")


def dbot_run(chat_id):
    @dbot.gateway.command
    def send_soup(resp):
        if all([db['token'], db['channel_id'], db['user_id']]):
            logger.success('Bot started')
            if resp.event.message:
                m = resp.parsed.auto()
                if 'channel_id' in m and m['channel_id'] == db['channel_id'] and m['author']['id'] == db['user_id']:
                    logger.success('Received new message')
                    tbot.send_message(chat_id, f'New message from {m["author"]["username"]}' + '\n'
                                                 'https://discord.com/channels/' +
                                                 m['guild_id'] + '/' + m['channel_id'])
        else:
            tbot.send_message(chat_id, 'Please configure bot before using')


tbot.polling(none_stop=True)

