from flask import Flask
app = Flask(__name__)

from flask import Response
from functools import wraps

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
    return "Hello World!"


if __name__ == "__main__":
    app.run()
