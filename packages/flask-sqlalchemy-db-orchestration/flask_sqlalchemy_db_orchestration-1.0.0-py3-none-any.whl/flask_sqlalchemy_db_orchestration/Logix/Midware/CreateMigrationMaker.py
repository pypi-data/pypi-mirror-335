# region Import Packages

import os

# endregion

# region CreateMigrationMaker Class

class CreateMigrationMaker:

    # region Init

    def __init__(self):
        pass
    
    # endregion

    # region Main

    def main(self, dbType, config):
        migrationMakerPath = os.path.join(os.getcwd(), "Logix", "Temp", "MigrationMaker.py")
        
        with open(migrationMakerPath, "w") as f:
            
            if dbType.lower() == "sqlite":
                dbPath = os.path.join(os.getcwd(), "Assets", "Databases", config.get('DATABASE_NAME', 'FlaskLocal.db'))
                configSQLite = dict(config)
                configSQLite["DATABASE_NAME"] = dbPath
                configStr = str(configSQLite)
            else:
                configStr = str(config)
                
            f.write(f"""from flask import Flask
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Logix.DbManager.DbManager import db, migrate, initApp
from Models.Entity._EntityExport import * 

app = Flask(__name__)
initApp(app, "{dbType}", {configStr})

if __name__ == "__main__":
    app.run()
""")

    # endregion

# endregion