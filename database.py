# database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ο φάκελος όπου βρίσκεται αυτό το αρχείο
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Αρχείο βάσης δεδομένων SQLite
DB_PATH = os.path.join(BASE_DIR, "erp.db")

# URL για τη δημιουργία του engine
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Δημιουργία του SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Βάση για τα declarative models
Base = declarative_base()

# Session factory
Session = sessionmaker(bind=engine)

# Δημιουργία όλων των πινάκων που έχουν οριστεί μέσω των Base subclasses
Base.metadata.create_all(engine)
