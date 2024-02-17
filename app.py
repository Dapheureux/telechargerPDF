import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table

# Créer une connexion à la base de données
engine = create_engine('sqlite:///bdpdf.db')  # Remplace avec ton propre URI de base de données

# Définir le schéma de la table "client"
metadata = MetaData()
client_table = Table(
    'client',
    metadata,
    Column('idClient', Integer, primary_key=True),
    Column('nom', String),
    Column('prenom', String),
    # Ajoute d'autres colonnes selon tes besoins
)

# Créer la table si elle n'existe pas
metadata.create_all(engine)

app = dash.Dash(__name__)

# Charger les données depuis la table "client" dans la base de données
query = "SELECT * FROM client;"
df = pd.read_sql(query, engine)

# Mise en page de l'application
app.layout = html.Div([
    dash_table.DataTable(
        id='table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
    ),
    html.Button('Télécharger en PDF', id='btn-pdf'),
    dcc.Download(id='download-pdf')
])

# Fonction pour générer le PDF à partir des données de la table
def generate_pdf(df):
    buffer = BytesIO()

    # Utilisation de ReportLab pour générer le PDF
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, "Données de la Table")
    
    col_widths = [pdf.stringWidth(col, "Helvetica", 12) + 6 for col in df.columns]
    
    y_position = 720
    for col, width in zip(df.columns, col_widths):
        pdf.drawString(100, y_position, col)
        y_position -= 18
    
    for row in df.itertuples(index=False):
        y_position -= 18
        for col, width in zip(df.columns, col_widths):
            pdf.drawString(100, y_position, str(getattr(row, col)))
            pdf.rect(95, y_position - 12, width, 18, fill=False)
    
    pdf.save()

    buffer.seek(0)
    return buffer

# Callback pour gérer le téléchargement du PDF
@app.callback(
    Output('download-pdf', 'data'),
    [Input('btn-pdf', 'n_clicks')]
)
def download_pdf(n_clicks):
    if n_clicks is None:
        return dash.no_update

    # Générer le PDF à partir des données de la table
    pdf_buffer = generate_pdf(df)
    
    return dcc.send_bytes(pdf_buffer.read(), filename='table_data.pdf')

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
