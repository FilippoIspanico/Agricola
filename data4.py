from pathlib import Path
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dbInteractions import Mastitis

##############################################
############# CONNECTION TO DB ###############
##############################################


Base = declarative_base()
engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


def prepare_data4(path_to_file: str) -> pd.DataFrame:
    path = Path(path_to_file)
    data = pd.read_excel(path, skiprows=[0], usecols="A,B,E,H,K", index_col=0, dtype={
        'Vacca': str,
        'Vacca.1': str,
        'Vacca.2': str,
        'Vacca.3': str
    })
    data.columns = ["A", "B", "C", "D"]
    data = data.dropna(how='all')

    return data


def add_data4_to_db(data: pd.DataFrame) -> None:

    for date in data.index:
        for case in data.loc[date].dropna().values:
            mastitis_case = Mastitis(cow_id=case, date=date)
            session.add(mastitis_case)

    session.commit()


def load_data4(path: str) -> int:

    try:
        data = prepare_data4(path)
        add_data4_to_db(data)
        return 0

    except Exception as e:
        print(f"Error processing data: {e}")
        return 1


# process_data_4('Dati 4.xlsx')
