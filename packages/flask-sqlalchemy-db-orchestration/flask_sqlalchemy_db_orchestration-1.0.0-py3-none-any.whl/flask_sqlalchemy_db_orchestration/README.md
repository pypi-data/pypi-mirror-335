# Flask-SQLAlchemy-Database-Orchestration

Flask-SQLAlchemy-Database-Orchestration, Flask uygulamalarında çoklu veritabanı ortamlarını yönetmek için geliştirilmiş güçlü bir araçtır. Bu araç, veritabanı oluşturma, başlatma ve migrasyon işlemlerini kolaylaştırarak, geliştirme süreçlerini hızlandırır.

## Özellikler

- Çoklu veritabanı desteği (SQLite, MySQL, PostgreSQL, MSSQL)
- Otomatik veritabanı oluşturma
- Tek veya tüm veritabanları için migrasyon yönetimi
- Kolay yapılandırma
- Renkli terminal çıktıları ile kullanıcı dostu arayüz

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/MuratBilginerSoft/Flask-SQLAlchemy-Database-Orchestration.git
cd Flask-SQLAlchemy-Database-Orchestration
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash

# Windows için
python -m venv VirtualEnv
VirtualEnv\Scripts\activate

# Linux/Mac için
python3 -m venv VirtualEnv
source VirtualEnv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r Requirements.txt

pip3 install -r Requirements.txt
```

## Kullanım

### Veritabanı Tipi Yapılandırması

Veritabanı tipini `Utils/GeneralConfig.json` dosyasında belirleyebilirsiniz:

```json
{
  "DB_TYPE": "SQLite"
}
```

Desteklenen veritabanı tipleri: `SQLite`

### Veritabanı Yapılandırması

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

### 1. Veritabanı Oluşturma

Veritabanlarını oluşturmak için:

```bash
python DbCreate.py

python3 DbCreate.py
```

Bu komut, DB_TYPE ile girilmiş olan veri tabanı tibine göre ilgili json dosyasındaki örneğin `Utils/SQLiteConfig.json` dosyasında tanımlanan tüm veritabanlarını `Assets/Databases` klasöründe oluşturur.

### 2. Veritabanı Başlatma (Init)

Veritabanı migrasyon klasörlerini başlatmak için:

```bash
python DbInit.py

python3 DbInit.py
```

Bu komut çalıştırıldığında:
1. Tek bir veritabanı veya tüm veritabanları için migrasyon başlatma seçeneği sunulur
2. Seçilen veritabanları için `Migrations/Migrations_{db_type}_{db_name}` klasörleri oluşturulur
3. Flask-Migrate ile veritabanı migrasyon dosyaları başlatılır

### 3. Veritabanı Migrasyon

Model değişikliklerini veritabanına uygulamak için:

```bash
python DbMigrade.py

python3 DbMigrade.py
```

Bu komut çalıştırıldığında:
1. Tek bir veritabanı veya tüm veritabanları için migrasyon seçeneği sunulur
2. Seçilen veritabanları için migrasyon işlemi gerçekleştirilir
3. Model değişiklikleri veritabanına yansıtılır

## Model Tanımlama

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

## Proje Yapısı

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

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
