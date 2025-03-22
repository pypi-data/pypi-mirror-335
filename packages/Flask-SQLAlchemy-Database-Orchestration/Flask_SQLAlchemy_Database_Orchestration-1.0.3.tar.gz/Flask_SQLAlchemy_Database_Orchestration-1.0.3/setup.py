from setuptools import setup
import os
import sys
import shutil
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        
        target_dir = os.getcwd()
        package_dir = os.path.join(self.install_lib, "Flask_SQLAlchemy_Database_Orchestration")
        
        if os.path.exists(package_dir):
            print(f"Files are being copied to {target_dir} directory...")
            
            for item in os.listdir(package_dir):
                s = os.path.join(package_dir, item)
                d = os.path.join(target_dir, item)
                
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
                    
            print("Installation Completed!")
        else:
            print(f"Warning: Package directory {package_dir} not found.")

# README.md dosyasını oku
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Flask_SQLAlchemy_Database_Orchestration",
    version="1.0.3",
    description="A powerful tool for managing multiple database environments in Flask applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Murat Bilginer",
    author_email="mbilginer@brainytech.net",
    url="https://github.com/MuratBilginerSoft/Flask-SQLAlchemy-Database-Orchestration",
    packages=["Flask_SQLAlchemy_Database_Orchestration"],
    include_package_data=True,
    package_data={
        'Flask_SQLAlchemy_Database_Orchestration': ['*.*', '**/*.*', '**/**/*.*'],
    },
    install_requires=[
        'alembic==1.15.1',
        'blinker==1.9.0',
        'click==8.1.8',
        'colorama==0.4.6',
        'Flask==3.1.0',
        'Flask-Migrate==4.1.0',
        'Flask-SQLAlchemy==3.1.1',
        'greenlet==3.1.1',
        'importlib_metadata==8.6.1',
        'itsdangerous==2.2.0',
        'Jinja2==3.1.6',
        'Mako==1.3.9',
        'MarkupSafe==3.0.2',
        'psycopg2==2.9.10',
        'PyMySQL==1.1.1',
        'pyodbc==5.2.0',
        'SQLAlchemy==2.0.39',
        'typing_extensions==4.12.2',
        'Werkzeug==3.1.3',
        'zipp==3.21.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    python_requires=">=3.6",
)