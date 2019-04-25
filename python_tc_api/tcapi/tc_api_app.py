import os
from logging import DEBUG
import sys
from flask import Flask
from flask_cors import CORS

from tcapi import db
from tcapi.tc_api_api import tcapi_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, '/root/tc_api_db.sqlite'),
    )
    CORS(app, origins=['https://example.com', 'https://example.com'],
         supports_credentials=False, allow_headers='*', methods=['GET', 'PUT', 'DELETE'], vary_header=False)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.logger.setLevel(DEBUG)
    app.register_blueprint(tcapi_blueprint, url_prefix='/api/terms_and_cond/v1.0/')

    db.init_app(app)

    return app


auto_app = create_app()


def main():
    # if len(sys.argv) != 2:
    #     print('Syntax: tcapi-server <config.yml>')
    #     raise Exception('Configuration file argument is missing')

    # app = create_app(sys.argv[1])
    app = create_app()

    # Note: Threaded does not work for the standalone server version (use gunicorn or similar)
    app.run(host='::', port=8042, debug=False, threaded=True)


if __name__ == '__main__':
    main()
