# boot server 
from flask import Flask, redirect, session, request, Response, render_template, flash, url_for, g, abort
from flask import send_file
from functools import wraps
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from wtforms import Form, RadioField, BooleanField, TextField, FloatField, PasswordField, validators, IntegerField, SelectField

from model import *
import redis 
import config

pxe_menu = yaml.load(open(config.menu))
distros = yaml.load(open('config/image_urls.txt'))
r = redis.Redis()

login_manager = LoginManager()
login_manager.login_view = "auth_user"

global app
app = Flask(__name__)
app.debug = True
login_manager.init_app(app)
app.secret_key = "asdf;lkasdflksgal88"

# Some forms 

class LoginForm(Form):
    username = TextField('username')
    password = TextField('password')
    
class AdminForm(Form):
    proxy = TextField('apt_proxy')
    login = BooleanField('login')
    salt_stack = BooleanField('saltstack')
    salt_master = TextField('saltmaster')

# Login manager parts

@login_manager.user_loader
def load_user(userid):
    uid = int(userid)
    u = User.query.filter(User.id == uid).first()
    return u
    
def returns_text(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/plain')
    return decorated_function

def check_user(user,passwd):
    u = User.query.filter(User.name == user).first()
    if u == None:
        return None
    else:
        # check password 
        return u
        
def valid_user(user,passwd):
    u = User.query.filter(User.name == user).first()    
    if u == None:
        return False
    else:
        # check password 
        return True

# Authentication login

@app.route('/auth', methods=["GET", "POST"])
def auth_user():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = check_user(form.username.data,form.password.data)
        if user == None:
            flash("Username or Password incorrect")
            return render_template('web_login.html')
        else:
            login_user(user)
            flash("Logged in successfully.")
            print "login worked"
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('web_interface/web_login.html')

# root page with agent switch 
    
@app.route("/")
def hello():
    user_agent = request.headers.get('User-Agent')
    if user_agent.startswith("iPXE"):
        return redirect(url_for('ipxe'))
    else:
        machines = Machine.query.all()
        return render_template('web_interface/index.html',machines=machines)

@app.route("/installs")
#@login_required
def installs():
    sess = Session.query.all()
    return render_template('web_interface/installs.html',sess=sess)


    
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
            return render_template('ipxe/menu.txt',machines=machines,key=sess.key)
        else:
            return render_template('login.txt')
            

@app.route("/ipxe")
@returns_text
def ipxe():
    return render_template('login.txt')
    
@app.route("/mac/<processor>/<mac_address>")
@returns_text
def mac(processor='',mac_address=''):
    if request.method == "GET":
        sess = Session()
        sess.macaddress = mac_address
        sess.processor = processor
        db_session.add(sess)
        db_session.commit()
        machines = Machine.query.all()
        return render_template('ipxe/menu.txt',machines=machines,key=sess.key)
    return ''
    
@app.route("/boot/<key>/<mtype>")
@returns_text
def boot(key,mtype):
    if Session.valid_key(key):
        # add the machine type into the session
        s = Session.get_session(key)
        s.name = mtype
        db_session.add(s)
        db_session.commit()    
        # TODO select plaform
        return render_template('os/debian/boot.txt',key=key)
    else:
        return render_template('ipxe/login.txt')      

@app.route('/instructions')
def instructions():
    return render_template('web_interface/instructions.html')

@app.route('/admin',methods=["GET", "POST"])
@login_required
def admin():
    form = AdminForm(request.form)
    return render_template('web_interface/admin.html',form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("hello"))

@app.route("/iso")
#@login_required
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
        # TODO , select the image from platform config
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
        if config.has_proxy:
            proxy = config.proxy
        else:
            proxy = None
        # TODO select platform
        return render_template('debian.prsd.txt',details=config,name=k.name,deb_proxy=proxy,key=key,password=k.processor) 

@app.route("/postinstall/<key>")
@returns_text
def postinstall(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        # TODO select platform
        return render_template('postinstall.txt',key=k)

@app.route("/firstboot/<key>")
@returns_text
def firstboot(key):
    if Session.valid_key(key):
        k = Session.get_session(key)
        # TODO add script layout to machines and break into platforms
        scripts = ['saltstack',str(k.name)]
        rendered_script = ''
        for i in scripts:
            rendered_script += '# --------------------- start '+ i +' --------------------- # \n'
            try:
                rendered_script += render_template('install_scripts/'+i+'.txt',details=config,key=k)+'\n'
            except:
                rendered_script += '\n# '+ i + ' has no template, please write and install\n\n'
            rendered_script += '# --------------------- end '+ i +' --------------------- #\n\n'
        return render_template('firstboot.txt',script=rendered_script,key=k)
            
@app.route("/final/<key>")
@returns_text
def final(key):
    if Session.valid_key(key):
        # TODO update session to say completed.
        fin = Session.get_session(key)
        fin.close() 
        # add machine into local redis database for pending
        # thatch suggests this is not the way to do it
        # salt-virt has better magic key handling
        r.sadd('machines',fin.name)
        return 'finished'

@app.route('/menu/')
@app.route('/menu/<first>')
@app.route('/menu/<first>/<second>')
@app.route('/menu/<first>/<second>/<third>')
def selector(first='',second='',third=''):
    data = distros
    if first == '' and second == '' and third== '':
        # first level
        return render_template('ipxe/layered_menu.txt',items=data.keys())
    if second == '' and third== '' and (first in pxe_menu):        
        return render_template('ipxe/layered_menu.txt',items=data[first],first=first)
    if third== '' and (first in data):
        if type(pxe_menu[first]) == type({}):        
            return render_template('ipxe/layered_menu.txt',first=data[first],second=data[first][second])
        if type(pxe_menu[first]) == type([]):
            return 'it is a list'            
    return str(data.keys())
        
@app.route('/blah')
@returns_text
def blah():
    return yaml.dump(distros)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0")
