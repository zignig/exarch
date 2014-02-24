
from flask import Flask, redirect, session, request, Response, render_template, flash, url_for, g, abort
from functools import wraps

app = Flask(__name__)
app.debug = True

def returns_text(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/plain')
    return decorated_function


@app.route("/")
@returns_text
def hello():
    print request.headers.get('User-Agent')
    return render_template('boot.txt',host=request.host)

@app.route('/blah')
def blah():
    return request.host
    return str(dir(request))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
