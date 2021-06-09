from app.app import create_app
from app.extensions import socketio,scheduler
from app.settings import DevConfig
# call config service
# CONFIG = DevConfig if os.environ.get('FLASK_DEBUG') == '1' else ProdConfig
CONFIG = DevConfig


app = create_app(config_object=CONFIG)

if __name__ == '__main__':

    scheduler.remove_all_jobs()
    scheduler.start()
    socketio.run(app, host='localhost', debug=True, port=4321)
    