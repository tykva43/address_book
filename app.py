import flask

app = flask.Flask(__name__)
app.config.from_object('settings')
port = app.config.get('PORT')
debug = app.config.get('DEBUG')


@app.route('/')
def main():
    return 'Hello'


if __name__ == '__main__':
    app.run(
        port=port,
        debug=debug
    )
