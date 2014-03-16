
from flask import Flask, redirect, session, request, Response, render_template, flash, url_for, g, abort
from flask import send_file
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
        processor = request.args.get("processor")
        if valid_user(user,password):
            sess = Session()
            sess.processor = processor 
            db_session.add(sess)
            db_session.commit()
            machines = Machine.query.all()
            return render_template('menu.txt',machines=machines,key=sess.key)
        else:
            return render_template('login.txt')

@app.route("/boot/<key>/<mtype>")
@returns_text
def boot(key,mtype):
    if Session.valid_key(key):
        # add the machine type into the session
        s = Session.get_session(key)
        s.name = mtype
        db_session.add(s)
        db_session.commit()        
        return render_template('boot.txt',key=key)
    else:
        return render_template('login.txt')      

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route("/iso")
def iso():
    # hand back the boot iso 
    return send_file('static/images/boot.iso',as_attachment=True,attachment_filename="boot.iso",mimetype='application/iso-image')
    
@app.route("/kernel/<key>")
def kernel(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        return send_file(
            'static/images/'+k.processor+'/linux',
            as_attachment=True,
            attachment_filename='linux'
            )

@app.route("/initrd/<key>")
def initrd(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        return send_file(
            'static/images/'+k.processor+'/initrd.gz',
            as_attachment=True,
            attachment_filename='initrd.gz'
            )
    
@app.route("/preseed/<key>")
@returns_text
def preseed(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        # TODO put proxy into config
        if config.has_proxy:
            proxy = config.proxy
        else:
            proxy = None
        return render_template('debian.prsd.txt',name=k.name,deb_proxy=proxy,key=key,password=k.processor) 

@app.route("/postinstall/<key>")
@returns_text
def postinstall(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        return render_template('postinstall.txt',key=k)

@app.route("/firstboot/<key>")
@returns_text
def firstboot(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        # TODO add script layout to machines
        scripts = ['saltstack',str(k.name)]
        rendered_script = ''
        for i in scripts:
            rendered_script += '# --------------------- start '+ i +' --------------------- # \n'
            rendered_script += render_template('install_scripts/'+i+'.txt',details=config,key=k)+'\n'
            rendered_script += '# --------------------- end '+ i +' --------------------- #\n\n'
        return render_template('firstboot.txt',script=rendered_script,key=k)
            
@app.route("/final/<key>")
@returns_text
def final(key):
    if Session.valid_key(key):
        # TODO update session to say completed.
        return 'finished'
        
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
