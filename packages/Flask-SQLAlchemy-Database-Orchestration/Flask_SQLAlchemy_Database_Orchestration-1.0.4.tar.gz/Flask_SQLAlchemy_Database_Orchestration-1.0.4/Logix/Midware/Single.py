# region Import Packages

from Logix.Midware.RunMigration import RunMigration
from Logix.Midware.HeroKit import HeroKit

# endregion

# region Single Class

class Single:

    # region Init

    def __init__(self):

        self.RunMigrations = RunMigration()
        self.HeroKits = HeroKit()

    # endregion

    # region Main

    def main(self, dbType, operation, dbIndex):

        databases = self.HeroKits.listDatabases(dbType)

        fullDbConfig = self.HeroKits.loadDbConfig(dbType)
        selectedDbconfig = fullDbConfig["DATABASES"][databases[dbIndex]]

        if selectedDbconfig:
            print(f"\n{dbType} database ({databases[dbIndex]}) {operation} process started...")

            self.RunMigrations.main(dbType, selectedDbconfig, operation)

            print(f"{dbType} database ({databases[dbIndex]}) {operation} process completed.")
        else:
            print("Invalid database selection!")

    # endregion

# endregion