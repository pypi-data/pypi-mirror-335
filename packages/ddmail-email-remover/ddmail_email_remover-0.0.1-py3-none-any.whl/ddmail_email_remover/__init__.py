import os
import sys
import toml
from flask import Flask
import logging
from logging.config import dictConfig
from logging import FileHandler


def create_app(config_file=None, test_config=None):
    """Create and configure an instance of the Flask application ddmail_email_remover."""

    # Configure logging.
    log_format = '[%(asctime)s] %(levelname)s in %(module)s %(funcName)s %(lineno)s: %(message)s'
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': log_format
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__, instance_relative_config=True)

    toml_config = None

    # Check if config_file has been set.
    if config_file is None:
        print("Error: you need to set path to configuration file in toml format")
        sys.exit(1)

    # Parse toml config file.
    with open(config_file, 'r') as f:
        toml_config = toml.load(f)

    # Set app configurations from toml config file.
    mode = os.environ.get('MODE')
    print("Running in MODE: " + mode)
    if mode == "PRODUCTION":
        app.config["SECRET_KEY"] = toml_config["PRODUCTION"]["SECRET_KEY"]
        app.config["PASSWORD_HASH"] = toml_config["PRODUCTION"]["PASSWORD_HASH"]
        app.config["EMAIL_ACCOUNT_PATH"] = toml_config["PRODUCTION"]["EMAIL_ACCOUNT_PATH"]

        # Configure logging.
        file_handler = FileHandler(filename=toml_config["PRODUCTION"]["LOGFILE"])
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)
    elif mode == "TESTING":
        app.config["SECRET_KEY"] = toml_config["TESTING"]["SECRET_KEY"]
        app.config["PASSWORD_HASH"] = toml_config["TESTING"]["PASSWORD_HASH"]
        app.config["EMAIL_ACCOUNT_PATH"] = toml_config["TESTING"]["EMAIL_ACCOUNT_PATH"]

        # Configure logging.
        file_handler = FileHandler(filename=toml_config["TESTING"]["LOGFILE"])
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)
    elif mode == "DEVELOPMENT":
        app.config["SECRET_KEY"] = toml_config["DEVELOPMENT"]["SECRET_KEY"]
        app.config["PASSWORD_HASH"] = toml_config["DEVELOPMENT"]["PASSWORD_HASH"]
        app.config["EMAIL_ACCOUNT_PATH"] = toml_config["DEVELOPMENT"]["EMAIL_ACCOUNT_PATH"]

        # Configure logging.
        file_handler = FileHandler(filename=toml_config["DEVELOPMENT"]["LOGFILE"])
        file_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(file_handler)
    else:
        print("Error: you need to set env variabel MODE to PRODUCTION/TESTING/DEVELOPMENT")
        sys.exit(1)

    app.secret_key = app.config["SECRET_KEY"]

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Apply the blueprints to the app
    from ddmail_email_remover import application
    app.register_blueprint(application.bp)

    return app
