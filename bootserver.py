
from flask import Flask, redirect, session, request, Response, render_template, flash, url_for, g, abort
from functools import wraps

from model import *
import config

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
def hello():
    user_agent = request.headers.get('User-Agent')
    if user_agent.startswith("iPXE"):
        return redirect(url_for('ipxe'))
    else:
        machines = Machine.query.all()
        return render_template('index.html',machines=machines)
    
@app.route("/ipxe")
@returns_text
def ipxe():
    return render_template('login.txt')
    
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
            return render_template('menu.txt',machines=machines,key=sess.key)
        else:
            return render_template('login.txt')

@app.route("/boot/<key>/<mtype>")
@returns_text
def boot(key,mtype):
    print key,mtype
    if valid_key(key):
        return render_template('boot.txt',key=key)
    else:
        return render_template('login.txt')      

@app.route("/iso")
def iso():
    return
    
@app.route("/kernel/<key>")
def kernel(key):
    print key
    return 
    
@app.route("/initrd/<key>")
def initrd(key):
    print key
    return 

@app.route("/preseed/<key>")
def preseed(key):
    print key
    return 

@app.route('/blah')
@returns_text
def blah():
    #return str(User.query.all())
    txt = ''
    for i in dir(request):
        try:
            txt = txt + str(i) + ' : ' + str(request.__dict__[i])+'\r\n'
        except:
            txt = txt + 'fail on '+str(i)+'\r\n'
    return txt

if __name__ == "__main__":
    app.run(host="0.0.0.0")
