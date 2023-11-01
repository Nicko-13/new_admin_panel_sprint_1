import os


SOURCE_PATH = os.environ.get('SOURCE_PATH')

TARGET_DNS = {
    'dbname': os.environ.get('TARGET_NAME'),
    'user': os.environ.get('TARGET_USER'),
    'password': os.environ.get('TARGET_PASSWORD'),
    'host': os.environ.get('TARGET_HOST'),
    'port': 5432,
    'options': '-c search_path=content',
}
BATCH_SIZE = 100
