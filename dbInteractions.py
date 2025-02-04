from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import pandas as pd
from datetime import datetime



Base = declarative_base()

# TODO: cow_id in urea table is in some strange format, please fix it


class Urea(Base):

    __tablename__ = "urea"

    cow_id = Column("cow_id", String, primary_key=True)
    date = Column("date", DateTime, primary_key=True)
    urea = Column("urea", Float)


    def __init__(self, cow_id: str, date: pd.Timestamp, urea: float):
        # date is in format: numpy.datetime64
        self.cow_id = cow_id
        self.date = pd.Timestamp(date)
        self.urea = urea

    def __repr__(self):
        return f"{self.cow_id}"

    def to_dict(self):
        return {
            'cow_id': self.cow_id,
            'date': self.date,
            'urea': self.urea
        }


class Mastitis(Base):

    __tablename__ = 'mastitis'
    cow_id = Column("cow_id", String, primary_key=True)
    date = Column("date", DateTime, primary_key=True)

    def __init__(self, cow_id: str, date: pd.Timestamp):
        self.cow_id = cow_id
        self.date = pd.Timestamp(date)

    def __repr__(self):
        return f"cow_id: { self.cow_id}; date: {self.date}"

    def to_dict(self):
        return {
            'cow_id': self.cow_id,
            'date': self.date.isoformat() if isinstance(self.date, datetime) else str(self.date)
            # Ensure JSON serialization
        }


class Fluxes(Base):
    """
    Even tough this class and table is called fluxes it contains also the data about total production.
    """

    __tablename__ = 'fluxes'
    first_session = Column("session", Boolean, primary_key=True)
    date = Column("date", DateTime, primary_key=True)
    cow_id = Column("cow_id", String, primary_key=True)
    milk_qty = Column("milk_qty", Float)
    flux0 = Column("flux0", Float)
    flux3 = Column("flux3", Float)
    flux_monotone = Column("flux_monotone", Boolean)

    def __init__(self, first_session: bool, date: pd.Timestamp, cow_id: str, milk_qty: float,
                 flux0: float, flux3: float, flux_monotone: bool):

        self.first_session = first_session
        self.date = pd.Timestamp(date)
        self.cow_id = cow_id
        self.milk_qty = milk_qty
        self.flux0 = flux0
        self.flux3 = flux3
        self.flux_monotone = flux_monotone

    def __repr__(self):
        return f"Id: {self.cow_id}"

    def to_dict(self):
        return {
            "first_session": self.first_session,
            "date": self.date.isoformat() if self.date else None,  # Ensure JSON serializable date
            "cow_id": self.cow_id,
            "milk_qty": self.milk_qty,
            "flux0": self.flux0,
            "flux3": self.flux3,
            "flux_monotone": self.flux_monotone
        }


class Differential(Base):

    __tablename__ = "differential"
    date = Column("date", DateTime, primary_key=True)
    cow_id = Column("cow_id", String, primary_key=True)
    differential_cells = Column("differential_cells", Float)
    lactN = Column("lactN", Integer)

    def __repr__(self):
        return f"{self.cow_id}, {self.date}, {self.differential_cells}, {self.lactN}"

    def to_dict(self):
        return {
            "date": self.date,
            "cow_id": self.cow_id,
            "differential_cells": self.differential_cells,
            "lactN": self.lactN
        }


engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind = engine)

#Session = sessionmaker(bind=engine)
#session = Session()

#cow = Cow('2', 2)
#session.add(cow)
#session.commit()