# region Import Packages

import json
import os

# endregion

# region HeroKit Class

class HeroKit:

    # region Init

    def __init__(self):
        
        self.YELLOW = '\033[93m'
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.RED = '\033[91m'
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.RESET = '\033[0m'  

    # endregion

    # region Initial Create Folders
    
    def initialCreateFolders(self):

        migrationFolder = os.path.join(os.getcwd(), "Migrations")
        databases = os.path.join(os.getcwd(), "Assets" , "Databases")

        if not os.path.exists(migrationFolder):
            os.makedirs(migrationFolder)
        
        if not os.path.exists(databases):
            os.makedirs(databases)

    # endregion

    # region Load General Config

    def loadGeneralConfig(self):
        path = "Utils/GeneralConfig.json"
        
        with open(path, "r") as f:
            generalConfig = json.load(f)
        
        return generalConfig
    
    # endregion

    # region Load DB Config
    
    def loadDbConfig(self, dbType):
        path = f"Utils/{dbType}Config.json"
        
        with open(path, "r") as f:
            dbConfig = json.load(f)
        
        return dbConfig 
    
    # endregion
    
    # region List Databases

    def listDatabases(self, dbType):
        config = self.loadDbConfig(dbType)
        return list(config["DATABASES"].keys())
    
    # endregion
    
    # region Get DB Name
    
    def getDbName(self, dbType, config):
        dbName = ""
        
        if dbType.lower() == "sqlite":
            dbName = config.get("DATABASE_NAME", "unknown").replace(".db", "")

        return dbName
    
    # endregion
    
    # region Create Migration Folder

    def createMigrationFolder(self, dbType, dbName, operation):
        
        migrationFolder = os.path.join("Migrations", f"Migrations_{dbType.lower()}_{dbName.lower()}")

        if not os.path.exists(migrationFolder) and operation == "init":
            os.makedirs(migrationFolder)

        return migrationFolder
    
    # endregion

    # region Create DB URL
    
    def createDbURL(self, dbType, dbConfig):
        if dbType.lower() == "sqlite":
            return f"sqlite:///{dbConfig['DATABASE_NAME']}"
        else:
            return None
    
    # endregion
    
    # region Choice Migration Type
    
    def choiceMigrationType(self, text):
        print(f"{self.PURPLE}\n{text}\n{self.RESET}")
        print("1. Single Database")
        print("2. All Databases")
        
        migrationType = input(f"{self.WHITE}\nSelection (1/2): {self.RESET}")
        
        return migrationType
    
    # endregion
    
# endregion