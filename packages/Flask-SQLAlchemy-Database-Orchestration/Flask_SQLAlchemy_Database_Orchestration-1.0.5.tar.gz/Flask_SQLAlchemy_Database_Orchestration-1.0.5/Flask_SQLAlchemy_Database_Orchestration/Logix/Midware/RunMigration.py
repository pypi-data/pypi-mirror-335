# region Import Packages

import subprocess
import os

from Logix.Midware.CreateMigrationMaker import CreateMigrationMaker
from Logix.Midware.HeroKit import HeroKit

# endregion

# region RunMigration Class

class RunMigration:

    # region Init

    def __init__(self) -> None:

        self.YELLOW = '\033[93m'
        self.GREEN = '\033[92m'
        self.BLUE = '\033[94m'
        self.RED = '\033[91m'
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.WHITE = '\033[97m'
        self.RESET = '\033[0m'  

        self.CreateMigrationMakers = CreateMigrationMaker()
        self.HeroKits = HeroKit()

    # endregion

    # region Main

    def main(self, dbType, selectedDBConfig, operation):

        dbName = self.HeroKits.getDbName(dbType, selectedDBConfig)
        migrationMaker = os.path.join(os.getcwd(), "Logix", "Temp", "MigrationMaker.py")

        migrationFolder = self.HeroKits.createMigrationFolder(dbType, dbName, operation)

        self.CreateMigrationMakers.main(dbType, selectedDBConfig)

        try:
            if operation == "init":
                print(f"{self.YELLOW}---{self.RESET}")
                print(f"\n{self.YELLOW}{dbType} database ({dbName}) init process started...{self.RESET}\n")

                subprocess.run(["flask", "--app", migrationMaker, "db", "init", "--directory", migrationFolder], check=True)
                print(f"{self.CYAN}Migration Folder Successfully Created: {migrationFolder}{self.RESET}")

                subprocess.run(["flask", "--app", migrationMaker, "db", "migrate", "--directory", migrationFolder], check=True)
                print(f"\n{self.BLUE}DB Migrate Successfully{self.RESET}\n")

                subprocess.run(["flask", "--app", migrationMaker, "db", "upgrade", "--directory", migrationFolder], check=True)
                print(f"\n{self.BLUE}DB Upgrade Successfully{self.RESET}\n")

            elif operation == "migrate":
                print(f"{self.YELLOW}---{self.RESET}")

                print(f"\n{self.YELLOW}{dbType} database ({dbName}) migrate process started...{self.RESET}\n")

                subprocess.run(["flask", "--app", migrationMaker, "db", "migrate", "--directory", migrationFolder], check=True)
                print(f"\n{self.BLUE}DB Migrate Successfully{self.RESET}\n")
                
                subprocess.run(["flask", "--app", migrationMaker, "db", "upgrade", "--directory", migrationFolder], check=True)
                print(f"\n{self.BLUE}DB Upgrade Successfully{self.RESET}\n")

            else:
                print(f"Invalid operation: {operation}")

        except subprocess.CalledProcessError as e:
            print(f"Migration process failed: {e}")
        
        finally:
            if os.path.exists(migrationMaker):
                os.remove(migrationMaker)
            if os.path.exists("__pycache__") and os.path.isdir("__pycache__"):
                for file in os.listdir("__pycache__"):
                    if file.startswith("MigrationMaker"):
                        os.remove(os.path.join("__pycache__", file))
    
    # endregion

# endregion