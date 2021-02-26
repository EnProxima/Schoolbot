# coding: utf-8
from telebot import TeleBot, types
import pandas as pd
import logging
import sqlite3 as db
import time
#config
BOT_KEY='1624811717:AAFXjzWIiEAiMFqnkHy0NcseKZoaxRZzO5w'
DB_PATH='./db/database.db'
LOGFILE='./logs/sender.log'

# end of config
logging.basicConfig(filename=LOGFILE, filemode='a', format='%(name)s - %(levelname)s - %(message)s')

logging.warning(str(pd.to_datetime('today'))+'Starting sender.. ')
try:
    db_conn = db.connect(DB_PATH)
    logging.warning('Connected to: '+ str(db_conn))
except:
    logging.error('Error when connect to DB')

cur=db_conn.cursor()

bot = TeleBot(BOT_KEY)
try:
 df_subs=pd.read_sql(con=db_conn,sql='select chatid from t_chats')
 df_message = pd.read_sql(con=db_conn,
                               sql='select datetime_from,subject_name, \
                                   task_name,identity from t_schooltasks\
                                    where MSG_SENT="N"  order by datetime_from')
 df_m_sent = pd.read_sql(con=db_conn,
                          sql='select identity from t_schooltasks\
                                     where MSG_SENT="Y" or MSG_SENT="I"')
 for row in df_message.iterrows():
     if row[1][2]!='\n':
         if row[1][3] in tuple(df_m_sent.identity):
             msg = '<b>' + str(pd.to_datetime(row[1][0]).date()) + ' Обновление </b> \n '  # Date
         else:
            msg = '<b>'+str(pd.to_datetime(row[1][0]).date()) + '</b> \n ' #Date
         msg=msg  +'<b>'+row[1][1] + '</b> \n'  # Class name
         msg=msg+ str(row[1][2])+'\n' # task
         msg=msg+'#'+row[1][1].partition(' ')[0] #tag

         for chatid in df_subs.iterrows():

            try:
             bot.send_message(chatid[1][0], msg,parse_mode='HTML')
             logging.warning(str(pd.to_datetime('today'))+' Send tasks to:'+str(chatid))
             time.sleep(1) # Sleep 1 sec according to Telegram recommendations
            except:
             logging.error(str(pd.to_datetime('today'))+' Send error  to:'+str(chatid))

         cur.execute(('''update t_schooltasks set MSG_SENT="Y" where  identity="%s" ''' % row[1][3]))

     else:
      cur.execute(('''update t_schooltasks set MSG_SENT="I" where  identity="%s" ''' % row[1][3]))

finally:
 db_conn.commit()
 db_conn.close() 
