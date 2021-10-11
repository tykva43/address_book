import os

url = os.environ.get('DATABASE_URL')

os.system('yoyo apply --database {} ./migrations'.format(url))
