from datetime import datetime
from zapv2 import ZAPv2

from flask_cors import CORS
from flask      import Flask, Blueprint

from routes.api import api 

from database import main    as sqlite_db
from database import queries as sqlite_queries


SQLITE_PATH   = "data/database.db"

app = Flask(__name__)
CORS( app )

app.register_blueprint(api)

@app.route("/")
def home(): return "200"


if __name__ == '__main__':
    #
    #   Initialization phase
    #
    sql_database_required_tables = {
        "ZapHistoryEntries" : sqlite_queries.create_zap_history_table,
        "ZapCookies"        : sqlite_queries.create_zap_cookies, 
        "ZapHeaders"        : sqlite_queries.create_zap_headers
    }
    sqlite_db.initialize_db( sql_database_required_tables, SQLITE_PATH )
    
    app.run(debug=True, host="0.0.0.0")
