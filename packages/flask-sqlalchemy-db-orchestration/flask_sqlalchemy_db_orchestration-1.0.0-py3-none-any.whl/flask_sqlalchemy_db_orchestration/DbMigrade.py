# region Import Packages

import os

from Logix.Midware.Multiple import Multiple
from Logix.Midware.HeroKit import HeroKit
from Logix.Midware.Single import Single

Multiples = Multiple()
HeroKits = HeroKit()
Singles = Single()


# endregion

# region Start

def start():

    migrationFolderList = []

    HeroKits.initialCreateFolders()

    generalConfig = HeroKits.loadGeneralConfig()
    dbType = generalConfig["DB_TYPE"]
    databases = HeroKits.listDatabases(dbType)

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m' 

    print(f"{YELLOW}\n*** Flask SQLAlchemy Database Orchestration Tool ***{RESET}")
   
    migrationType = HeroKits.choiceMigrationType("Db Migrate Type Selection")
    
    if migrationType == "1":

        print(f"\n{dbType} databases:")
        for i, database in enumerate(databases, 1):
            print(f"{i}. {database}")
        
        dbChoice = input(f"\nSelection (1-{len(databases)}): ")

        dbIndex = int(dbChoice) - 1
        
        if dbIndex < 0 or dbIndex >= len(databases):
            print("Invalid selection!")
            return

        fullDbConfig = HeroKits.loadDbConfig(dbType)
        selectedDbconfig = fullDbConfig["DATABASES"][databases[dbIndex]]
        
        dbName = HeroKits.getDbName(dbType, selectedDbconfig)

        migrationFolder = os.path.join(os.getcwd(), "Migrations",f"Migrations_{dbType.lower()}_{dbName.lower()}")

        if not os.path.exists(migrationFolder):
            print(f"{RED}\nMigrations_{dbType.lower()}_{dbName.lower()} : You do not have a migration folder, first run DbInit.py and create a migration folder. run 'python DbInit.py' {RESET}")
            return

        Singles.main(dbType, "migrate", dbIndex)

    elif migrationType == "2":

        fullDbConfig = HeroKits.loadDbConfig(dbType)
        migrationFolderList = []
        
        for i in range(len(databases)):
            selectedDbconfig = fullDbConfig["DATABASES"][databases[i]]
            dbName = HeroKits.getDbName(dbType, selectedDbconfig)
            migrationFolder = os.path.join(os.getcwd(), "Migrations",f"Migrations_{dbType.lower()}_{dbName.lower()}")

            if not os.path.exists(migrationFolder):
                migrationFolderList.append(f"Migrations_{dbType.lower()}_{dbName.lower()}")

        if migrationFolderList:
            for item in migrationFolderList:
                print(f"{RED}\n{item} : You do not have a migration folder, first run DbInit.py and create a migration folder. run 'python DbInit.py' {RESET}")

        else:
            Multiples.main(dbType, "migrate")

    else:
        print(f"{RED}Invalid selection!{RESET}")

# endregion

if __name__ == "__main__":
    start()
