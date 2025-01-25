import os

class Config:
    # Konfigurasi database PostgreSQL
    DB_USER = os.getenv('DB_USER', 'postgres') 
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Kurnia2905')  # Ganti 'yourpassword' dengan password database Anda
    DB_HOST = os.getenv('DB_HOST', 'localhost')  # Lokasi database, default localhost
    DB_PORT = os.getenv('DB_PORT', '5432')  # Port database PostgreSQL, default 5432
    DB_NAME = os.getenv('DB_NAME', 'phishing_dt')  # Nama database Anda

    # Connection URI untuk SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
