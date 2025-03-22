# Changelog

Bu dosya, Flask-SQLAlchemy-Database-Orchestration projesindeki tüm önemli değişiklikleri belgelemektedir.

## [1.0.0] - 2025-03-21

### Eklenenler
- SQLite veritabanı desteği
- Veritabanı oluşturma aracı (DbCreate.py)
- Veritabanı başlatma aracı (DbInit.py)
- Veritabanı migrasyon aracı (DbMigrade.py)
- Tek veya tüm veritabanları için migrasyon yönetimi
- Renkli terminal çıktıları
- Temel model sınıfları
- Örnek entity modelleri (TestUsers, TestAuthentications, TestUnits)
- Yapılandırma dosyaları (GeneralConfig.json, SQLiteConfig.json)
- Migrasyon klasörü otomatik oluşturma
- Veritabanı klasörü otomatik oluşturma
- Detaylı README.md

### Teknik Detaylar
- Flask 3.1.0 desteği
- Flask-SQLAlchemy 3.1.1 entegrasyonu
- Flask-Migrate 4.1.0 ile migrasyon yönetimi
- SQLAlchemy 2.0.39 ORM desteği
- BaseModel sınıfı ile model standartizasyonu
- HeroKit yardımcı sınıfı ile renkli terminal çıktıları
- Single ve Multiple sınıfları ile tekli veya çoklu veritabanı işlemleri

### Bilinen Sorunlar
- Şu anda yok

### Gelecek Sürümlerde Planlar
- Web arayüzü
- Daha fazla veritabanı tipi desteği
- Otomatik model oluşturma araçları
- Veritabanı şema görselleştirme
- Veritabanı yedekleme ve geri yükleme
