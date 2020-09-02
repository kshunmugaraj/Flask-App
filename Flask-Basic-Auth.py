from flask import Flask, request , make_response
from functools import wraps

app = Flask(__name__)

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'password':
            return f(*args, **kwargs)
        return make_response('Could not verify the login',401,{'www-Authenticate': 'Basic realm="Login Required"'})
    return decorated
    
@app.route('/')
def index():
    pass
    
@app.route('/otherpage')
@auth_required
def page():
    return '<h1> You are on the other page </h1>'
    
@app.route('/page')
@auth_required
def page():
    return '<h1> You are on the page </h1>'

if __name__ == '_main_':
    app.run(debug=True)