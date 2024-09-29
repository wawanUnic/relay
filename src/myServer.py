from __future__ import print_function

from flask import Flask
from flask import make_response
from flask import render_template
from flask_bootstrap import Bootstrap

from RPi import GPIO

error_msg = '{msg:"error"}'
success_msg = '{msg:"success"}'

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle/<int:relay>')
def api_toggle_relay(relay):
    print("Переключить", relay)
    GPIO.setup(relay, GPIO.OUT)
    GPIO.output(relay, not GPIO.input(relay))
    return make_response(success_msg, 200)

@app.route('/on/<int:relay>')
def api_relay_on(relay):
    print("Включить", relay)
    GPIO.setup(relay, GPIO.OUT)
    GPIO.output(relay, GPIO.HIGH)
    return make_response(success_msg, 200)

@app.route('/off/<int:relay>')
def api_relay_off(relay):
    print("Отключить", relay)
    GPIO.setup(relay, GPIO.OUT)
    GPIO.output(relay, GPIO.LOW)
    return make_response(success_msg, 200)

@app.route('/all_on/')
def api_relay_all_on():
    print("Все ВКЛ")
    return make_response(success_msg, 200)

@app.route('/all_off/')
def api_all_relay_off():
    print("Все ВЫКЛ")
    return make_response(success_msg, 200)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', the_error=e), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', the_error=e), 500

try:
    GPIO.setmode(GPIO.BCM)
    app.run(host='0.0.0.0', port=8888, debug=True)
except KeyboardInterrupt:
    print('Stop!')
    GPIO.cleanup()
finally:
    print('Bye!')
