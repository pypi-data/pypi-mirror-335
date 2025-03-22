#region Import Packages

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from Logix.Midware.HeroKit import HeroKit

# endregion

# region Initialize

HeroKits = HeroKit()

db = SQLAlchemy()
migrate = Migrate()

# endregion

# region initApp

def initApp(app, dbType=None, dbConfig=None):
    if dbType and dbConfig:
        app.config["SQLALCHEMY_DATABASE_URI"] = HeroKits.createDbURL(dbType, dbConfig)
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        
        db.init_app(app)
        migrate.init_app(app, db)
        
        return True
    return False

# endregion
