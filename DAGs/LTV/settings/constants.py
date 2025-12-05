import os
from dotenv   import load_dotenv
load_dotenv("/app/.env")


IP              = os.getenv('IP_DATA', None)
PORT            = int(os.getenv('PORT_DATA', 8011))          # HTTP-порт (8123 в контейнере)
DB              = os.getenv('DB_DATA', None)
USERNAME        = os.getenv('USERNAME_DATA', None)
PASSWD          = os.getenv('PASSWD_DATA', None)
table_load_data = os.getenv('TABLE_LOAD_DATA', None)

HOST_BI     =  os.getenv('DB_HOST', None)
DB_BI       =  os.getenv('DB_NAME', None)
USERNAME_BI =  os.getenv('DB_USER', None)
PASSWD_BI   =  os.getenv('DB_PASS', None)
tablename   =  os.getenv('BI_tablename', None)


RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', None)
RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', None)
RABBITMQ_PASS = os.getenv('RABBITMQ_DEFAULT_PASS', None)
queue_name    = os.getenv('queue_name_LTV', None)

SCHEDULE_INTERVAL  = int(os.getenv('SCHEDULE_INTERVAL', 20)) #время между проверками очереди в секундах
MAX_PARALLEL_TASKS = int(os.getenv('MAX_PARALLEL_TASKS', 1)) #кол-во параллельных запусков

REVISION        = os.getenv('REVISION', None)
_correct_coef   = float(os.getenv('correct_coef', 0.2))
table_predict   = os.getenv('TABLE_PREDICT', None)
save_result     = os.getenv('save_result', None)  # сохранение результата в бд 'db', в файл 'parquet', 'csv', 'excel'

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



