# necessary imports to setup the database
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_database_url():
    """Get database URL with proper SSL settings"""
    db_url = config("SQLALCHEMY_DB_URL")
    connect_args = {
        'connect_timeout': 10,  # 10 seconds timeout
        'keepalives': 1,       # Enable keepalives
        'keepalives_idle': 30, # Send keepalive after 30 seconds of idle
        'keepalives_interval': 10, # Send keepalive every 10 seconds
        'keepalives_count': 5  # Try 5 times before giving up
    }
    
    # If it's a remote database, add SSL configuration
    if not any(local in db_url for local in ('localhost', '127.0.0.1')):
        connect_args.update({
            'sslmode': 'require',
            'sslcert': None,  # Path to client certificate if needed
            'sslkey': None,   # Path to client key if needed
            'sslrootcert': None  # Path to root certificate if needed
        })
    
    return db_url, connect_args


# create the engine and session to connect to the database
SQLALCHEMY_DB_URL, connect_args = get_database_url()
engine = create_engine(
    SQLALCHEMY_DB_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,        # Maximum number of connections
    max_overflow=20      # Allow up to 20 extra connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
