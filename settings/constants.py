import os
from dotenv   import load_dotenv
load_dotenv("/app/.env")

HOST     =  os.getenv('DB_HOST', None)
DB       =  os.getenv('DB_NAME', None)
USERNAME =  os.getenv('DB_USER', None)
PASSWD   =  os.getenv('DB_PASS', None)
tablename = os.getenv('BI_tablename', None)
PORT      = int(os.getenv('DB_PORT', 5432))

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', None)
RABBITMQ_USER = os.getenv('RABBITMQ_DEFAULT_USER', None)
RABBITMQ_PASS = os.getenv('RABBITMQ_DEFAULT_PASS', None)

# время ожидания подключения к RabbitMQ
retry_delay   = int(os.getenv('retry_delay', 5))
# максимальное кол-во попыток подключения к RabbitMQ
max_retries   = int(os.getenv('max_retries', 15))

external_IP   = os.getenv('external_IP', None)
external_port = int(os.getenv('external_port', 8000))

scheme_forms = {'LTV': {
                            'CURRDATE': {
                                            'type'     : 'datetime',
                                            'required' : True
                                         },
                            'RESEARCH_PERIOD': {
                                            'type'     : 'int',
                                            'required' : True
                                         }

                        },
                'LAL': {
                            'CURRDATE': {
                                            'type'     : 'datetime',
                                            'required' : True
                                         },
                            'RESEARCH_PERIOD': {
                                            'type'     : 'int',
                                            'required' : True
                                         }

                        }
                # 'ChurnRate': {}

                }

status_name = {
                    0: 'добавлен',
                    1: 'в очереди',
                    2: 'на обработке',
                    3: 'успешно',
                    4: 'ошибка'
              }