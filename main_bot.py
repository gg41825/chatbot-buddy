from waitress import serve
from app import create_app
from app import config
if __name__ == '__main__':
    app = create_app()
    host = config.APP_HOST
    port = int(config.APP_PORT)

    print(f"Starting server on {host}:{port}")
    serve(app, host=host, port=port)
