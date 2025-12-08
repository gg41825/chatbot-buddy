from waitress import serve
from app import create_app
from app.config import get_config_value

if __name__ == '__main__':
    app = create_app()
    host = get_config_value('app', 'host', '0.0.0.0')
    port = int(get_config_value('app', 'port', '80'))

    print(f"Starting server on {host}:{port}")
    serve(app, host=host, port=port)
