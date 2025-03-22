# region Import Packages

from Logix.Midware.RunMigration import RunMigration
from Logix.Midware.HeroKit import HeroKit

# endregion

# region Multiple Class

class Multiple:

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

        self.RunMigrations = RunMigration()
        self.HeroKits = HeroKit()
    
    # endregion

    # region Main

    def main(self, dbType, operation):
        environments = self.HeroKits.listDatabases(dbType)

        print(f"\n{dbType} databases:")
        for i, env in enumerate(environments, 1):
            print(f"{i}. {env}")
        
        for env in environments:

            fullDbConfig = self.HeroKits.loadDbConfig(dbType)
            selectedDbconfig = fullDbConfig["DATABASES"][env]

            if selectedDbconfig:
                self.RunMigrations.main(dbType, selectedDbconfig, operation)
            else:
                print("Invalid database selection!")
    
    # endregion

# endregion