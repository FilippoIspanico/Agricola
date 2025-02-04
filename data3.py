from pathlib import Path
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


from dbInteractions import Mastitis, Fluxes


##############################################
############# CONNECTION TO DB ###############
##############################################

Base = declarative_base()
engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


def get_milk_session(milk_session: str) -> bool:
    """
    Returns true if the milk_session is a first milk_session. False otherwise
    :param milk_session: string of the milk_session
    :return: Bool
    """
    return milk_session.split('_')[1] == '1'


def get_date(milk_session: str) -> pd.Timestamp:
    """
    Returns the date of the current milk_session
    :param milk_session: str
    :return: pd.Timestamp of the date
    """
    date = milk_session.split('_')[0]
    return pd.Timestamp(date)




def prepare_data3(path_to_file: str) -> dict:
    path = Path(path_to_file)
    data = pd.read_excel(path_to_file,  skiprows=[1], usecols="C,D,I,J,K,L",
                         sheet_name=None,
                         skipfooter = 2,
                         dtype= {
                             'Vacca ID': str,
                             'QuantitÓ di latte': float,
                             'Vel. flu': float,
                             'Vel. flu..1:': float,
                             'Vel. flu..2': float,
                             'Vel. flu..3': float
                         })
    # data here is a dict where the key is the name of the sheet and the value is the associated pandas df
    return data


def add_data3_to_db(data: dict):

    for milk_session in data.keys():

        date = get_date(milk_session)
        first_milk_session = get_milk_session(milk_session)
        milk_session_data = data[milk_session]

        for cow in milk_session_data['Vacca ID'].dropna().unique():
            cow_data = milk_session_data[milk_session_data['Vacca ID'] == cow]
            #import pdb; pdb.set_trace()

            milk_qty = cow_data['QuantitÓ di latte'].values[0]

            flux0  = cow_data['Vel. flu.'].values[0]
            flux1 = cow_data['Vel. flu..1'].values[0]
            flux2 = cow_data['Vel. flu..2'].values[0]
            flux3 = cow_data['Vel. flu..3'].values[0]
            flux_monotone = flux0 < flux1 < flux2 < flux3

            fluxes = Fluxes(first_session=first_milk_session,
                            date=date,
                            cow_id=cow,
                            milk_qty=milk_qty,
                            flux0=flux0,
                            flux3=flux3,
                            flux_monotone=flux_monotone)
            session.add(fluxes)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"skipping sheet {milk_session} since it is already present into the db")

def load_data3(path: str):
    data = prepare_data3(path)
    add_data3_to_db(data)
