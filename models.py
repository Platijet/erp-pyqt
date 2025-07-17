# models.py

from sqlalchemy import Column, Integer, String, Float
from database import Base, engine

class Product(Base):
    __tablename__ = "products"

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    sku_manufacturer         = Column(String, unique=True, nullable=True)
    sku_supplier             = Column(String, unique=True, nullable=True)
    supplier                 = Column(String, nullable=False)
    name                     = Column(String, nullable=False)
    description              = Column(String, nullable=False)
    size                     = Column(String, nullable=True)
    color                    = Column(String, nullable=True)
    sku                      = Column(String, unique=True, nullable=False)
    season                   = Column(String, nullable=False)
    quantity                 = Column(Integer, nullable=False)
    low_stock_notification   = Column(Integer, nullable=False, default=0)
    position                 = Column(String, nullable=False)
    category                 = Column(String, nullable=False)
    vat                      = Column(String, nullable=False)
    cost_ex                  = Column(Float, nullable=False)
    price_inc                = Column(Float, nullable=False)
    discount1_inc            = Column(Float, nullable=False)
    discount2_inc            = Column(Float, nullable=False)
    format_str               = Column(String, nullable=False)

# Δημιουργία του πίνακα (αν δεν υπάρχει ήδη)
Base.metadata.create_all(engine)
