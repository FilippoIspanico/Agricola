import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import pickle
import lifelines

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Table, text


def get_cows_to_cure(SF, threshold = 0.1):
    to_cure = []
    for cow in SF.columns:
        for time, prob in enumerate(SF[cow]):

            if prob < threshold:
                to_cure.append(cow)
    to_cure = np.unique(to_cure)
    print(f"We need to cure: {len(to_cure)} cows")
    print(f"this result in curing {len(to_cure)/len(SF.columns)*100} of cows")

    return to_cure


def execute_sa(threshold = 0.1):

    Base = declarative_base()
    engine = create_engine("sqlite:///cow.db", echo=True)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    QUERY_LIMIT = 5000  # we define this query limit here to avoid huge computing times and crashing.
    view_name = 'view_for_sa'

    query = f"SELECT * FROM {view_name} WHERE cow_id IS NOT NULL ORDER BY cow_id LIMIT {QUERY_LIMIT};"
    result = session.execute(text(query))
    dati = result.fetchall()

    dati = pd.DataFrame(dati)
    final_features = ['Flux0', 'Flux3', 'FluxMonotone', 'Prod', 'DifferentialCells',
                  'LastDifferentialCells', 'Urea', 'NumberPastMastitis', 'LactN']
    cow_id = dati['cow_id']
    time_healty = dati['days_healthy']
    dati = dati[final_features]
    dati = dati.apply(pd.to_numeric, errors='coerce')



    means = [4.42335601e-01, 2.99851305e+00, 1.31897119e+02, 2.71106507e+00,
       6.75809040e+03, 6.39875171e+03, 1.68571840e+01, 4.34842250e-01,
       2.23928077e+00]

    vars = [1.52877094e-01, 1.06462729e+00, 1.89108769e+04, 4.54284093e-02,
       1.18952462e+06, 5.24728664e+06, 1.25735307e+01, 6.38072712e-01,
       1.73665896e+00]

    df_std = pd.DataFrame()
    df_std.index = cow_id
    for idx, col in enumerate(final_features):
        entry_std = []
        for entry in dati[col]:
            entry_std.append((entry - means[idx])/(np.sqrt(vars[idx])))
        df_std[col] = entry_std

    df_std.fillna(0, inplace = True)
    df_std["Prod"] = [0.]*len(df_std.index)


    # Load the model from the file
    with open('fitted_model/survival_model_m2.pkl', 'rb') as f:
        m2 = pickle.load(f)

    SF = m2.predict_survival_function(df_std, conditional_after=time_healty) #, conditional_after = censored_subjects_last_obs

    to_cure = get_cows_to_cure(SF, threshold)
    plt.plot(SF)
    plt.savefig('static/all_lines.jpg')
    plt.clf()

    overall_survival = SF.mean(axis=1)
    plt.plot(SF.index, overall_survival, label = 'median surival')
    for cow in to_cure:
        plt.plot(SF.index, SF[cow], label = cow)
    plt.legend()
    plt.savefig('static/to_cure.jpg')
    plt.clf()
    return to_cure



print(execute_sa())
