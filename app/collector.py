import requests
import pandas as pd
import logging
import sqlite3 as db

# configuration section
DB_PATH = './db/database.db'
SITE_LOGIN = 'login'
SITE_PWD = 'password'

DOWNLOAD_URL = 'https://dnevnik2.petersburgedu.ru/api/filekit/file/download?p_uuid='
LOGFILE = './logs/collector.log'
INITIAL_RUN = False

# Logging configuration
logging.basicConfig(filename=LOGFILE, filemode='a', format='%(name)s - %(levelname)s - %(message)s')


# end of configuration section

def update_db(df_schedule):
    df_db = pd.read_sql(con=db_conn, sql='select identity,task_name from t_schooltasks')
    df_db_upd = pd.merge(
        df_schedule,
        df_db,
        on=['identity', 'task_name'],
        how="left",
        indicator=True
    ).query('_merge=="left_only"')[
        {'subject_name', 'task_name', 'identity', 'content_name', 'datetime_from', 'MSG_SENT'}]
    df_db_upd.to_sql(con=db_conn, name='t_schooltasks', if_exists='append', index=False)
    df_db_upd.to_csv('./logs/' + str(pd.to_datetime('now')) + '_log.csv')
    cur.execute(
        'update t_schooltasks set subject_name="Иностранный язык(Эспозито)" where subject_name="Иностранный язык"')
    db_conn.commit()


# start execution
logging.warning('start collection at: ' + str(pd.to_datetime('today')))

try:
    db_conn = db.connect(DB_PATH)
    cur = db_conn.cursor()
except:
    logging.error('Error when connect to DB')

# guathentificate on site
r_auth = requests.post('https://dnevnik2.petersburgedu.ru/api/user/auth/login',
                       json={'type': 'email',
                             'login': SITE_LOGIN,
                             'password': SITE_PWD})
# get information
payload = {'p_page': '1',
           'p_datetime_from': str((pd.to_datetime('today') - pd.to_timedelta(7, unit='d')).normalize()),
           'p_datetime_to': str((pd.to_datetime('today') + pd.to_timedelta(1, unit='d')).normalize()),
           'p_educations[]': '524879'}
r_get_diary = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/lesson/list-by-education', params=payload,
                           cookies=r_auth.cookies)
logging.warning('Site query result: ' + str(r_get_diary))

df_schedule = pd.DataFrame(r_get_diary.json()['data']['items'])
df_task = pd.DataFrame()

for index, row in df_schedule['tasks'].iteritems():
    msg = ''

    for item in range(0, len(df_schedule.loc[index].tasks)):
        task_name = str(df_schedule.loc[index].tasks[item]['task_name']).replace('None', '')
        files = ''
        if len(df_schedule.loc[index].tasks[item]['files']) > 0:
            for fileid in range(0, len(df_schedule.loc[index].tasks[item]['files'])):
                files = '<a href="' + DOWNLOAD_URL + df_schedule.loc[index].tasks[item]['files'][fileid]['uuid'] + \
                        '">' + df_schedule.loc[index].tasks[item]['files'][fileid]['file_name'] + '</a>' + '\n' + files
        msg = task_name + '\n' + msg + files
    df_task = df_task.append({'index': index, 'task_name': msg}, ignore_index=True)

df_task = df_task.drop('index', axis=1)
df_schedule = df_schedule.join(df_task)
df_schedule = df_schedule[{'identity', 'datetime_from', 'subject_name', 'content_name', 'task_name'}]
df_schedule['identity'] = df_schedule['identity'].apply(lambda d: d['id'])
df_schedule['MSG_SENT'] = 'N'

# initial update of DB
if INITIAL_RUN:
    df_schedule.to_sql(con=db_conn, name='t_schooltasks', if_exists='append', index=False)

update_db(df_schedule)
