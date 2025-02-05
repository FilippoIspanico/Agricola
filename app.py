from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os


from data3 import load_data3
from data4 import load_data4
from data5 import load_data5
from data6 import load_data6


from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dbInteractions import Mastitis, Fluxes, Urea, Differential

from survival_analysis import execute_sa

app = Flask(__name__)
app.secret_key = 'chiave_super_segretissima'

# Cartella dove salvare i file caricati temporaneamente
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

Base = declarative_base()
engine = create_engine("sqlite:///cow.db", echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()



@app.route('/carica-dati', methods=['POST'])
def carica_dati():
    tipo_dato = request.form.get('tipo_dato')
    file_dato = request.files.get('file_dato')

    if not file_dato or file_dato.filename == '':
        # Se non viene caricato alcun file, reindirizza alla pagina di upload con un messaggio di errore
        error_message = "Nessun file selezionato."
        return render_template('error.html', error_message=error_message)

    # Salva il file in una cartella temporanea
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_dato.filename)
    file_dato.save(file_path)

    try:
        if tipo_dato == 'dati3':
            load_data3(file_path)
        elif tipo_dato == 'dati4':
            load_data4(file_path)
        elif tipo_dato == 'dati5':
            load_data5(file_path)
        elif tipo_dato == 'dati6':
            load_data6(file_path)
        else:
            error_message = "Tipo di dato non valido."
            return render_template('error.html', error_message=error_message)

        # Se tutto va bene, mostra la pagina di successo
        return render_template('success.html')

    except Exception as e:
        # In caso di errore, mostra la pagina di errore con il messaggio
        error_message = f"Errore nel caricamento dei dati: {str(e)}"
        return render_template('error.html', error_message=error_message)

    finally:
        # Rimuove il file temporaneo per evitare di occupare spazio
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/aggiungi-dati')
def aggiungi_dati():
    return render_template('aggiungi_dati.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/visualizza-dati')
def visualizza_dati():
    return render_template('viusalizza_dati.html')

@app.route('/esegui-query')
def esegui_query():
    """
    We execute the selected query. A limit of 1000 entries is used to prevent problems with large file handling.
    :return: the serialization of the data as JSON
    """

    QUERY_LIMIT = 1000
    query_type = request.args.get('query', 'all')

    # Esempio di query in base al tipo selezionato
    if query_type == 'flussi':
        dati = session.query(Fluxes).limit(QUERY_LIMIT).all()
    elif query_type == 'mastiti':
        dati = session.query(Mastitis).limit(QUERY_LIMIT).all()
    elif query_type == 'dati5':
        dati = session.query(Urea).limit(QUERY_LIMIT).all()
    elif query_type == 'dati6':
        dati = session.query(Differential).limit(QUERY_LIMIT).all()

    else:

        dati = []

    risultati = [item.to_dict() for item in dati]

    return jsonify(risultati)

@app.route('/analisi-mastite')
def analisi_mastite():
    return render_template('analisi-mastite.html')


@app.route('/process-analysis', methods=['POST'])
def process_analysis():
    threshold = float(request.form.get('threshold', 0.1))
    to_cure = execute_sa(threshold)
    return render_template('sa_results.html',  cow_ids=to_cure)

if __name__ == '__main__':
    app.run(debug=True)
