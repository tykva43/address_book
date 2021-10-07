from flask import Flask

from urls import urls_blueprint

app = Flask(__name__)
app.config.from_object('settings')
port = app.config.get('PORT')
debug = app.config.get('DEBUG')
host = app.config.get('HOST')
app.register_blueprint(urls_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(
        port=port,
        debug=debug,
        host=host,
    )
