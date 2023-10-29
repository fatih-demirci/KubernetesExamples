from flask import Flask
import socket

app = Flask(__name__)


@app.route('/')
def hello_world():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)

    return f'Hostname: {host_name} Hostip: {host_ip} \n'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
