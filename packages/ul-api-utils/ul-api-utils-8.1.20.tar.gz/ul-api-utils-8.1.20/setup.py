from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul-api-utils',
    version='8.1.20',
    description='Python api utils',
    author='Unic-lab',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='',
    packages=find_packages(),
    package_data={
        "ul_api_utils": [
            'py.typed',
            "utils/flask_swagger_ui/templates/*.html",
            "utils/flask_swagger_ui/static/*.html",
            "utils/flask_swagger_ui/static/*.js",
            "utils/flask_swagger_ui/static/*.css",
            "utils/flask_swagger_ui/static/*.png",
            "utils/flask_swagger_ui/static/*.map",
            "conf/ul-debugger-main.js",
            "conf/ul-debugger-ui.js",
        ],
    },
    entry_points={
        "console_scripts": [
            'ulapiutls=ul_api_utils.main:main',
        ],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    platforms='any',
    install_requires=[
        "ul-unipipeline==2.0.6",
        "jinja2==3.1.2",
        "flask==2.1.3",
        "flask-wtf==1.0.1",
        "flask-limiter==2.5.1",
        "flask-caching==2.1.0",
        "flask-swagger-ui==4.11.1",
        "flask-monitoringdashboard==3.1.2",
        "pycryptodome==3.15.0",
        "pyjwt==2.4.0",
        "gunicorn==20.1.0",
        "gevent==24.2.1",
        "gevent-websocket==0.10.1",
        "pyyaml==6.0",
        "requests==2.28.1",
        "cryptography==38.0.1",
        "colored==1.4.3",
        "flask-socketio==5.3.6",
        "ormsgpack==1.8.0",
        "msgpack==1.0.4",
        "msgpack-types==0.2.0",
        "fastavro==1.7.0",
        "factory-boy==3.3.0",
        "sentry-sdk[flask]==1.9.2",
        "faker==24.8.0",
        "types-requests==2.28.8",
        "types-jinja2==2.11.9",
        "xlsxwriter==3.2.0",
        "werkzeug==2.3.7",
        "frozendict==2.4.4",
        "wtforms==3.0.1",
        "wtforms-alchemy==0.18.0",
        "pathvalidate==3.2.0",

        # "opentelemetry-sdk==1.8.0",
        # "opentelemetry-api==1.8.0",
        # "opentelemetry-instrumentation-flask==0.27b0",
        # "opentelemetry-instrumentation-requests==0.27b0",
        # "opentelemetry-exporter-jaeger==1.8.0",
        # "opentelemetry-instrumentation-sqlalchemy==0.27b0",
        # "ul-db-utils==4.0.2",        # ACTUALIZE, BUT DO NOT UNCOMMENT PLEASE
        # "ul-py-tool==2.1.3",        # ACTUALIZE, BUT DO NOT UNCOMMENT PLEASE
    ],
)
