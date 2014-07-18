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

@app.route('/ed2k/<string:action>')
def ed2kcwl(action):
    import ed2000crawler
    from json import dumps
    data = ""
    ivd_arg_data = dumps({'ret': -1, 'errmsg': 'Invalid arguments'})
    if action == 'lastlist':
        data = ed2000crawler.get_last_archive_page()
    elif action == 'list':
        lid = request.args.get('id')
        if lid is None:
            data = ivd_arg_data
        else:
            data = ed2000crawler.fetch_list(lid)
    elif action == 'page':
        pid = request.args.get('id')
        if pid is None:
            data = ivd_arg_data
        else:
            data = ed2000crawler.fetch_page(pid)
    else:
        data = dumps({'ret': -1, 'errmsg': 'Unsupported action'})
    return make_response((data, 200, {'Content-Type': 'application/json;charset=UTF-8'}))