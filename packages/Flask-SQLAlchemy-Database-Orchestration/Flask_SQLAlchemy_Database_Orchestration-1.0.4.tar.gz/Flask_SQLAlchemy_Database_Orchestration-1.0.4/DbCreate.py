#!/usr/bin/env python
# -*- coding: utf-8 -*-

# region Import Packages

import os
import sqlite3

from Logix.Midware.HeroKit import HeroKit

# endregion

# region Variables

HeroKits = HeroKit()

# endregion

# region Functions

def createSQLiteDatabases(config):

    HeroKits.initialCreateFolders()
    
    DB_DIR = os.path.join(os.getcwd(), "Assets", "Databases")
    
    for dbEnv, dbConfig in config["DATABASES"].items():
        dbName = dbConfig.get("DATABASE_NAME")
        
        if not dbName:
            print(f"{HeroKits.RED}Error: DATABASE_NAME not found for {dbEnv}{HeroKits.RESET}")
            continue
            
        dbPath = os.path.join(DB_DIR, dbName)
        
        if not os.path.exists(dbPath):
            try:
                conn = sqlite3.connect(dbPath)
                conn.close()
                print(f"{HeroKits.GREEN}Created SQLite database: {dbPath}{HeroKits.RESET}")
            except Exception as e:
                print(f"{HeroKits.RED}Error creating SQLite database {dbPath}: {e}{HeroKits.RESET}")
        else:
            print(f"{HeroKits.BLUE}SQLite database already exists: {dbPath}{HeroKits.RESET}")

# endregion

# region Main

def main():
   
    print(f"{HeroKits.YELLOW}\n*** Flask SQLAlchemy Database Creation Tool ***{HeroKits.RESET}")
    
    generalConfig = HeroKits.loadGeneralConfig()
    dbType = generalConfig.get("DB_TYPE")
    
    if not dbType:
        print(f"{HeroKits.RED}Error: DB_TYPE not found in GeneralConfig.json{HeroKits.RESET}")
        return
    
    print(f"\nActive database type: {HeroKits.GREEN}{dbType}{HeroKits.RESET}")
    
    dbConfig = HeroKits.loadDbConfig(dbType)
    
    if not dbConfig:
        print(f"{HeroKits.RED}Error: Could not load config for {dbType}{HeroKits.RESET}")
        return
    
    if dbType == "SQLite":
        createSQLiteDatabases(dbConfig)
    else:
        print(f"{HeroKits.RED}Error: Unsupported database type: {dbType}{HeroKits.RESET}")
        return
    
    print(f"\n{HeroKits.GREEN}Database creation completed!{HeroKits.RESET}")

# endregion

if __name__ == "__main__":
    main()