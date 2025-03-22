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

    HeroKits.initialCreateFolders()

    generalConfig = HeroKits.loadGeneralConfig()
    dbType = generalConfig["DB_TYPE"]
    databases = HeroKits.listDatabases(dbType)

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m' 
    BLUE = '\033[94m'
    
    print(f"{YELLOW}\n*** Flask SQLAlchemy Database Orchestration Tool ***{RESET}")
    
    migrationType = HeroKits.choiceMigrationType("Db Init Type Selection")
    
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

        print(f"\nSelected database: {dbName}")

        migrationFolder = os.path.join(os.getcwd(), "Migrations",f"Migrations_{dbType.lower()}_{dbName.lower()}")

        if os.path.exists(migrationFolder):
            print(f"{RED}\nMigrations_{dbType.lower()}_{dbName.lower()} : This database has already been initialized {RESET}")
            return

        Singles.main(dbType, "init", dbIndex)

    elif migrationType == "2":

        fullDbConfig = HeroKits.loadDbConfig(dbType)
        migrationFolderTrueList = []
        migrationFolderFalseList = []
        dbIndexList = []

        for i in range(len(databases)):
            selectedDbconfig = fullDbConfig["DATABASES"][databases[i]]
            dbName = HeroKits.getDbName(dbType, selectedDbconfig)
            migrationFolder = os.path.join(os.getcwd(), "Migrations",f"Migrations_{dbType.lower()}_{dbName.lower()}")

            if not os.path.exists(migrationFolder):
                dbIndexList.append(i)
                migrationFolderFalseList.append(migrationFolder.replace("\\", "/").split("/")[-1])
            else:
                migrationFolderTrueList.append(migrationFolder.replace("\\", "/").split("/")[-1])


        if dbIndexList:
            for dbIndex in dbIndexList:
                Singles.main(dbType, "init", dbIndex)

        if migrationFolderTrueList:
            for migrationFolder in migrationFolderTrueList:
                print(f"{RED}\n{migrationFolder} : This database has already been initialized {RESET}")

        if migrationFolderFalseList:
            for migrationFolder in migrationFolderFalseList:
                print(f"{BLUE}\nCreated {migrationFolder} Folder. {RESET}")

    else:
        print(f"{RED}Invalid selection!{RESET}")

# endregion

if __name__ == "__main__":
    start()
