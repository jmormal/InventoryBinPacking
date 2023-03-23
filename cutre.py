from waitress import serve
from index import app

serve(app.server, host='0.0.0.0', port=8080)