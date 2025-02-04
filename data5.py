from pathlib import Path
import pandas as pd


from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from dbInteractions import Urea

##############################################
############ CONSTANT DEFINITIONS ############
##############################################


UREA_COLUMN = 'Urea'
DATE_COLUMN_IDX = 0
COW_ID_COLUMN_IDX = 1

##############################################
############# CONNECTION TO DB ###############
##############################################


Base = declarative_base()
engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


def load_data5(path_to_file: str, sheet_name = None) -> None:
    """
    This function takes as input a path to a file containing data5 information as excel. This excel contains a lot of
    sheets in generals, hence the function will process each one of them and try to add them to the db.
    This process allows for easier UI dev since there will be no information asked the user about which sheet to process,
    however will result in more code for error management and slower times
    :param sheet_name:
    :param path_to_file:
    :return: pd.Dataframe
    """

    path: Path = Path(path_to_file)
    data: dict = pd.read_excel(path, sheet_name = sheet_name, header = 0)  # parse_dates=[DATE_COLUMN]

    sheets = data.keys()
    for sheet in sheets:
        df = data[sheet]
        #import pdb; pdb.set_trace()
        df[UREA_COLUMN] = pd.to_numeric(df[UREA_COLUMN], errors='coerce')

        COW_ID_COLUMN = df.columns[COW_ID_COLUMN_IDX]
        DATE_COLUMN = df.columns[DATE_COLUMN_IDX]

        for cow in df[COW_ID_COLUMN].dropna().unique():
            cow_data = df[df[COW_ID_COLUMN] == cow]
            urea = cow_data[UREA_COLUMN].values[0]
            date = cow_data[DATE_COLUMN].values[0]

            entry = Urea(
                cow_id=str(cow),
                date = pd.Timestamp(date),
                urea = urea
            )

            session.add(entry)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"skipping sheet {sheet} since it is already present into the db")


# load_data5('Dati5.xlsx', sheet_name=[1, 2])
# load_data5('Dati5.xlsx', sheet_name=[2, 3])