import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Límites de medios (Tips)
    TIP_IMG_MAX_MB = 2
    TIP_GIF_MAX_MB = 8
    TIP_VIDEO_MAX_MB = 150
    TIP_AUDIO_MAX_MB = 20
    TIP_DOC_MAX_MB = 25
    TIP_TOTAL_ATTACH_MAX_MB = 300
