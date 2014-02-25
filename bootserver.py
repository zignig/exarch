
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
    if u == None:
        return False
    else:
        # check password 
        return True

def valid_key(key):
    k = Session.query.filter(Session.key == key).first()
    if k != None:
        return True
    else:
        return False

@app.route("/")
@returns_text
def hello():
    user_agent = request.headers.get('User-Agent')
    if user_agent == "iPXE/1.0.0+ (d4c0)":  
        return render_template('boot.txt',host=request.host_url)
    else:
        return 'web browser'

@app.route("/login")
@returns_text
def login():
    if request.method == "GET":
        user = request.args.get("user")
        password = request.args.get("password")
        if valid_user(user,password):
            sess = Session()
            db_session.add(sess)
            db_session.commit()
            machines = Machine.query.all()
            return render_template('menu.txt',machines=machines,key=sess.key,host=request.host_url)
        else:
            return render_template('boot.txt',host=request.host)


@app.route("/boot/<key>/<mtype>")
@returns_text
def boot(key,mtype):
    print key,mtype
    return '#!ipxe \nreboot'
    
@app.route('/blah')
@returns_text
def blah():
    return str(User.query.all())
    return str(dir(request))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
