
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
def hello():
    user_agent = request.headers.get('User-Agent')
    if user_agent.startswith("iPXE"):
        return render_template('boot.txt') 
    else:
        return render_template('index.html')
    
@app.route("/test")
def test():
    return render_template('boot.txt')
    
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
            return render_template('boot.txt')

@app.route("/boot/<key>/<mtype>")
@returns_text
def boot(key,mtype):
    print key,mtype
    #if valid_key(key):
    #    return '#!ipxe \n\necho stuff $$ read test'
    #else:
    return render_template('boot.txt')
    
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
