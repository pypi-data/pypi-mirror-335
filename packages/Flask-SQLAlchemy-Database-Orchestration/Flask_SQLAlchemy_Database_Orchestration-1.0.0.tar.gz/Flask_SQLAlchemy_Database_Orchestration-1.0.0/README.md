# Flask-SQLAlchemy-Database-Orchestration

[Türkçe](#türkçe) | [English](#english)

<a name="english"></a>
## English

Flask-SQLAlchemy-Database-Orchestration is a powerful tool developed for managing multiple database environments in Flask applications. This tool accelerates development processes by facilitating database creation, initialization, and migration operations.

### Features

- SQLite database support
- Automatic database creation
- Migration management for single or all databases
- Easy configuration
- User-friendly interface with colored terminal outputs

### Installation

1. Install the package:
```bash
# Windows
pip install Flask-SQLAlchemy-Database-Orchestration

# Linux/Mac
pip3 install Flask-SQLAlchemy-Database-Orchestration
```

2. Find the Installation Directory:

When the package is installed, all files will be copied to your current working directory.

3. Install Dependencies:

```bash
# Windows
pip install -r Requirements.txt

# Linux/Mac
pip3 install -r Requirements.txt
```

### Usage

#### Database Type Configuration

You can specify the database type in the `Utils/GeneralConfig.json` file:

```json
{
  "DB_TYPE": "SQLite"
}
```

Supported database types: `SQLite`

#### Database Configuration

Each database type has its own configuration file. For example, for SQLite: `Utils/SQLiteConfig.json`:

You can add as many databases as you want.

```json
{
  "DATABASES": {
    "local": {
      "DATABASE_NAME": "FlaskLocal.db"
    },
    "dev": {
      "DATABASE_NAME": "FlaskDev.db"
    },
    "test": {
      "DATABASE_NAME": "FlaskTest.db"
    }
  }
}
```

#### 1. Database Creation

To create databases:

```bash
python DbCreate.py

# Linux/Mac
python3 DbCreate.py
```

This command creates all databases defined in the relevant json file, such as `Utils/SQLiteConfig.json`, in the `Assets/Databases` folder according to the database type entered with DB_TYPE.

#### 2. Database Initialization

To initialize database migration folders:

```bash
python DbInit.py

# Linux/Mac
python3 DbInit.py
```

When this command is run:
1. Offers the option to initialize migration for a single database or all databases
2. Creates `Migrations/Migrations_{db_type}_{db_name}` folders for selected databases
3. Initializes database migration files with Flask-Migrate

#### 3. Database Migration

To apply model changes to the database:

```bash
python DbMigrade.py

# Linux/Mac
python3 DbMigrade.py
```

When this command is run:
1. Offers the option to migrate for a single database or all databases
2. Performs migration for selected databases
3. Reflects model changes to the database

### Model Definition

Models are defined in the `Models/Entity` folder. An example model:

```python
from Models.BaseModel.BaseModel import *
from Logix.DbManager.DbManager import db

class TestUsers(BaseModel, db.Model):
    __tablename__ = "TestUsers"

    Id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    UserId = db.Column(db.String(300), unique=True)
    Email = db.Column(db.String(100), unique=True)
    Name = db.Column(db.String(30))
    # ...

    def __init__(self, UserId, Email, Name, ...):
        self.UserId = UserId
        self.Email = Email
        self.Name = Name
        # ...

    def to_dict(self):
        return {prop: getattr(self, prop) for prop in dir(self) 
                if not prop.startswith('_') and not callable(getattr(self, prop))}
```

After creating a new model, don't forget to import it in the `Models/Entity/_EntityExport.py` file:

```python
from Models.Entity.TestUsers import TestUsers
from Models.Entity.TestAuthentications import TestAuthentications
# ...
```

### Project Structure

```
Flask-SQLAlchemy-Database-Orchestration/
├── Assets/
│   └── Databases/        # Database files
├── Logix/
│   ├── DbManager/        # Database management tools
│   └── Midware/          # Migration and helper tools
├── Migrations/           # Migration folders
├── Models/
│   ├── BaseModel/        # Base model classes
│   └── Entity/           # Database models
├── Utils/                # Configuration files
├── DbCreate.py           # Database creation
├── DbInit.py             # Migration initialization
├── DbMigrade.py          # Migration application
└── Requirements.txt      # Dependencies
```

### License

This project is licensed under the [MIT License](LICENSE).

---

<a name="türkçe"></a>
## Türkçe

Flask-SQLAlchemy-Database-Orchestration, Flask uygulamalarında çoklu veritabanı ortamlarını yönetmek için geliştirilmiş güçlü bir araçtır. Bu araç, veritabanı oluşturma, başlatma ve migrasyon işlemlerini kolaylaştırarak, geliştirme süreçlerini hızlandırır.

### Özellikler

- SQLite veritabanı desteği
- Otomatik veritabanı oluşturma
- Tek veya tüm veritabanları için migrasyon yönetimi
- Kolay yapılandırma
- Renkli terminal çıktıları ile kullanıcı dostu arayüz

### Kurulum

1. Paketi yükleyin:
```bash
# Windows
pip install Flask-SQLAlchemy-Database-Orchestration

# Linux/Mac
pip3 install Flask-SQLAlchemy-Database-Orchestration
```

2. Paketin Kurulu Olduğu Dizini Bulun:

Paket kurulduğunda, tüm dosyalar mevcut çalışma dizininize kopyalanacaktır.

3. Bağımlılıkları Yükleyin:

```bash
# Windows
pip install -r Requirements.txt

# Linux/Mac
pip3 install -r Requirements.txt
```

### Kullanım

#### Veritabanı Tipi Yapılandırması

Veritabanı tipini `Utils/GeneralConfig.json` dosyasında belirleyebilirsiniz:

```json
{
  "DB_TYPE": "SQLite"
}
```

Desteklenen veritabanı tipleri: `SQLite`

#### Veritabanı Yapılandırması

Her veritabanı tipi için kendi yapılandırma dosyası bulunmaktadır. Örneğin, SQLite için `Utils/SQLiteConfig.json`:

İstediğiniz kadar veri tabanı ekleyebilirsiniz.

```json
{
  "DATABASES": {
    "local": {
      "DATABASE_NAME": "FlaskLocal.db"
    },
    "dev": {
      "DATABASE_NAME": "FlaskDev.db"
    },
    "test": {
      "DATABASE_NAME": "FlaskTest.db"
    }
  }
}
```

#### 1. Veritabanı Oluşturma

Veritabanlarını oluşturmak için:

```bash
python DbCreate.py

# Linux/Mac
python3 DbCreate.py
```

Bu komut, DB_TYPE ile girilmiş olan veri tabanı tibine göre ilgili json dosyasındaki örneğin `Utils/SQLiteConfig.json` dosyasında tanımlanan tüm veritabanlarını `Assets/Databases` klasöründe oluşturur.

#### 2. Veritabanı Başlatma (Init)

Veritabanı migrasyon klasörlerini başlatmak için:

```bash
python DbInit.py

# Linux/Mac
python3 DbInit.py
```

Bu komut çalıştırıldığında:
1. Tek bir veritabanı veya tüm veritabanları için migrasyon başlatma seçeneği sunulur
2. Seçilen veritabanları için `Migrations/Migrations_{db_type}_{db_name}` klasörleri oluşturulur
3. Flask-Migrate ile veritabanı migrasyon dosyaları başlatılır

#### 3. Veritabanı Migrasyon

Model değişikliklerini veritabanına uygulamak için:

```bash
python DbMigrade.py

# Linux/Mac
python3 DbMigrade.py
```

Bu komut çalıştırıldığında:
1. Tek bir veritabanı veya tüm veritabanları için migrasyon seçeneği sunulur
2. Seçilen veritabanları için migrasyon işlemi gerçekleştirilir
3. Model değişiklikleri veritabanına yansıtılır

### Model Tanımlama

Modeller `Models/Entity` klasöründe tanımlanır. Örnek bir model:

```python
from Models.BaseModel.BaseModel import *
from Logix.DbManager.DbManager import db

class TestUsers(BaseModel, db.Model):
    __tablename__ = "TestUsers"

    Id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    UserId = db.Column(db.String(300), unique=True)
    Email = db.Column(db.String(100), unique=True)
    Name = db.Column(db.String(30))
    # ...

    def __init__(self, UserId, Email, Name, ...):
        self.UserId = UserId
        self.Email = Email
        self.Name = Name
        # ...

    def to_dict(self):
        return {prop: getattr(self, prop) for prop in dir(self) 
                if not prop.startswith('_') and not callable(getattr(self, prop))}
```

Yeni bir model oluşturduktan sonra, `Models/Entity/_EntityExport.py` dosyasına import etmeyi unutmayın:

```python
from Models.Entity.TestUsers import TestUsers
from Models.Entity.TestAuthentications import TestAuthentications
# ...
```

### Proje Yapısı

```
Flask-SQLAlchemy-Database-Orchestration/
├── Assets/
│   └── Databases/        # Veritabanı dosyaları
├── Logix/
│   ├── DbManager/        # Veritabanı yönetim araçları
│   └── Midware/          # Migrasyon ve yardımcı araçlar
├── Migrations/           # Migrasyon klasörleri
├── Models/
│   ├── BaseModel/        # Temel model sınıfları
│   └── Entity/           # Veritabanı modelleri
├── Utils/                # Yapılandırma dosyaları
├── DbCreate.py           # Veritabanı oluşturma
├── DbInit.py             # Migrasyon başlatma
├── DbMigrade.py          # Migrasyon uygulama
└── Requirements.txt      # Bağımlılıklar
```

### Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.