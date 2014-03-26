import sys
sys.path.insert(0, '/opt/bootserver/')
import bootserver
from model import *
init_db()
application = bootserver.app
