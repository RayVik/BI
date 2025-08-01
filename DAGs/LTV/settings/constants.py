import os
from dotenv   import load_dotenv
load_dotenv("/app/.env")

# IP       = os.getenv('IP_DATA', '83.239.206.206')
# PORT     = int(os.getenv('PORT_DATA', 8011))          # HTTP-порт (8123 в контейнере)
# DB       = os.getenv('DB_DATA', 'ASH')
# USERNAME = os.getenv('USERNAME_DATA', 'user6525')
# PASSWD   = os.getenv('PASSWD_DATA', '34SwkLaaEi7aHfj0')
IP       = '83.239.206.206'
PORT     = 8011          # HTTP-порт (8123 в контейнере)
DB       = 'ASH'
USERNAME = 'user6525'
PASSWD   = '34SwkLaaEi7aHfj0'

# HOST_BI     =  os.getenv('DB_HOST', 'db')
# DB_BI       =  os.getenv('DB_NAME', 'BI')
# USERNAME_BI =  os.getenv('DB_USER', 'bitask_user')
# PASSWD_BI   =  os.getenv('DB_PASS', 'bitask_pass')
# tablename   =  os.getenv('BI_tablename', 'bi__task_register')
HOST_BI     =  'db'
DB_BI       =  'BI'
USERNAME_BI =  'bitask_user'
PASSWD_BI   =  'bitask_pass'
tablename   =  'bi__task_register'

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_DEFAULT_PASS', 'mq_pass')
queue_name    = os.getenv('queue_name_LTV', 'DAGs/LTV')

SCHEDULE_INTERVAL  = int(os.getenv('SCHEDULE_INTERVAL', 20)) #время между проверками очереди в секундах
MAX_PARALLEL_TASKS = int(os.getenv('MAX_PARALLEL_TASKS', 1)) #кол-во параллельных запусков

REVISION        = os.getenv('REVISION', 'v20250522')
_correct_coef   = float(os.getenv('_correct_coef', 0.2))
table_predict   = os.getenv('table_predict', 'BIG_DATA_LTV_ONLINE_OFFLINE_PREDICT')
save_result     = os.getenv('save_result', ['db', 'parquet', 'excel'])  # сохранение результата в бд 'db', в файл 'parquet', 'csv', 'excel'

passport_of_models = [
    # модель которая обучена на 3 тензора по данным 1-3 заказа

    {
        'revision': '_ltv__v31072025__dataslicing_1-3d_ten3__all1gen',  # с 22052025
        'type_of_model': 'LTV',
        'categorical_features': [],
        'sequence_number': (1, 3)
    },

    # для заказов от 4
    {
        'revision': '_ltv__v31072025__dataslicing_4-10d_ten10__all1gen',  # с 22052025
        'type_of_model': 'LTV',
        'categorical_features': [],
        'sequence_number': (4, 10)
    }

]



