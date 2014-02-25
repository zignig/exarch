
from flask import Flask, redirect, session, request, Response, render_template, flash, url_for, g, abort
from functools import wraps

from model import *
 

app = Flask(__name__)
app.debug = True

def returns_text(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/plain')
    return decorated_function

def valid_user(user,passwd):
    u = User.query.filter(User.name == user).first()
    
    return u
    
@app.route("/")
@returns_text
def hello():
    user_agent = request.headers.get('User-Agent')
    if user_agent == "iPXE/1.0.0+ (d4c0)":  
        return render_template('boot.txt',host=request.host)
    else:
        return 'web browser'

@app.route("/login")
@returns_text
def login():
    if request.method == "GET":
        user = request.args.get("user")
        print valid_user(user,'')
    machines = Machine.query.all()
    return render_template('menu.txt',machines=machines,host=request.host_url)
    
@app.route('/blah')
@returns_text
def blah():
    return str(User.query.all())
    return str(dir(request))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
