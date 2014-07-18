"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask, make_response, request
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

import os, urllib2

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route('/listenv')
def listenv():
    envstr = '\r\n'.join(["%s=%s" % (k, v) for k,v in os.environ.iteritems()])
    return make_response(envstr, 200, {"Content-Type": "text/plain;charset=utf-8"})
    
@app.route('/test-ip')
def test_ip():
    t = int(request.args.get('t', 10))
    ip_list = {}
    for ip in range(t):
        ip = urllib2.urlopen("http://www.telize.com/ip").read().strip()
        ip_list[ip] = ip_list.get(ip, 0) + 1
    return make_response(str(ip_list), 200, {"Content-Type": "text/plain;charset=utf-8"})
