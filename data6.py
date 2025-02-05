import pandas as pd
import tabula
import re
import pdfplumber
from pathlib import Path

from dbInteractions import Differential

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


##############################################
############# CONNECTION TO DB ###############
##############################################


Base = declarative_base()
engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()



def load_data6(path_to_file: str):

    path_to_file = Path(path_to_file)

    with pdfplumber.open(path_to_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages])


    dates = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", text)

    dates = [pd.Timestamp(date) for date in dates]

    analysis_date = min(dates)
    print(analysis_date)

    dfs = tabula.read_pdf(path_to_file, pages='all')
    print("Pdf conversion completed!")


    COLUMNS_11 = ['Gr', 'Matricola', 'Nome', 'Id', 'LactN', 'DataParto', 'DaysInLactation', 'Latte', 'CelluleSomatiche', 'LS', 'CelluleDifferenziali']
    COLUMNS_12 = COLUMNS_11 + ['Semaforo']

    for idx, df in enumerate(dfs):

        if len(df.columns) == 11:
            df.columns = COLUMNS_11
        elif len(df.columns) == 12:
            df.columns = COLUMNS_12

        df['CelluleDifferenziali'] = pd.to_numeric(df['CelluleDifferenziali'].str.replace(',', '.', regex=True), errors='coerce')
        #df['Id'] = pd.to_numeric(df['Id'], errors='coerce')

        for cow in df['Id'].dropna().unique():

            cow_data = df[df['Id'] == cow]


            try:
                differential_cells: float = cow_data['CelluleDifferenziali'].values[0]
                lactN: int = cow_data['LactN'].iloc[0]
                if not pd.isna(differential_cells) and not pd.isna(lactN):

                    entry = Differential(
                        date = analysis_date,
                        cow_id = str(cow),
                        differential_cells = differential_cells,
                        lactN = int(lactN)
                    )

                    session.add(entry)

            except Exception:
                pass

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            print(f"skipping df {idx}")

load_data6('/home/filippo/Downloads/1370806_PST_GetLA13_CelluleDifferenziali_MS_ViaEmail_20200618095821187.pdf')