import sys
import os 

sys.settrace
from app import app
app.run(port=4004, debug=True, host='0.0.0.0')
