# coding: utf-8
from telebot import TeleBot
import sqlite3 as db
import pandas as pd
import logging


#configuration section
DB_PATH='./db/database.db'
BOT_KEY=''
LOGFILE='./logs/bot.log'

logging.basicConfig(filename=LOGFILE, filemode='a', format='%(name)s - %(levelname)s - %(message)s')

logging.warning(str(pd.to_datetime('today'))+'Starting bot.. ')

bot = TeleBot(BOT_KEY)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Я буду отправлять тебе задания из электронного дневника. Если хочешь отменить подписку отправь мне команду /bye  ')
    logging.warning(str(pd.to_datetime('today'))+' Add user to DB:'+str(message.chat.id)+ '  '+ str(message.from_user))
    try:
        db_conn = db.connect(DB_PATH)
    except:
        logging.error('DB connection problem')
    cur=db_conn.cursor()
    cur.execute(('insert or ignore into t_chats (chatid) VALUES (%s)' % message.chat.id ))
    db_conn.commit()
    db_conn.close()
	
@bot.message_handler(content_types=['text'])
def send_text(message):
  try:
        db_conn = db.connect(DB_PATH)
  except:
    logging.error('DB Connection problem')

  cur=db_conn.cursor()

  if message.text.lower() == '/bye':
       bot.send_message(message.chat.id, 'Вы удалены из списка рассылки. \n До свидания!')	
       logging.warning(str(pd.to_datetime('today'))+' Delete user from DB:'+str(message.chat.id))
       cur.execute(('delete from t_chats  where chatid="%s"' % message.chat.id ))
       db_conn.close()
  else:

     logging.warning(str(pd.to_datetime('now'))+
                         ' '+ str(message.chat.id) +
                         ' ' + str(message.from_user) +
                         ' ' +str(message.text))


bot.polling()
