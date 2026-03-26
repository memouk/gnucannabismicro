import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD", "root")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DATABASE", "gnucannabis")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}"
        f"@{mysql_host}:{mysql_port}/{mysql_db}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")
    AUTH0_ALGORITHMS = [a.strip() for a in os.getenv("AUTH0_ALGORITHMS", "RS256").split(",")]
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
    AUTH0_SECRET = os.getenv("AUTH0_SECRET", SECRET_KEY)
    AUTH0_REDIRECT_URI = os.getenv("AUTH0_REDIRECT_URI", "http://localhost:5000/callback")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_LOGIN_URL = os.getenv("BACKEND_LOGIN_URL", "http://localhost:5000/")
