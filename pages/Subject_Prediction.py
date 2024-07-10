import streamlit as st
import pandas as pd
import openai
import base64
import openpyxl
import numpy
import io 
import os
import time
import pdfkit
from jinja2 import Environment, FileSystemLoader
import openai
import pandas as pd
from io import StringIO
import base64
######################## ################################################################################################################################################################################

openai.api_key =openai.api_key

st.set_page_config(layout="wide")

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown("""
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    """, unsafe_allow_html=True)



st.markdown(
    """
    <style>
    
    body {
        background-color: #ffffff; /* Couleur de fond par défaut */
        color: #000000; /* Couleur de texte par défaut */
        font-family: Arial, sans-serif;
        padding: 1rem;
    }
    .video-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 500px; /* Ajustez la hauteur de la vidéo selon vos besoins */
    }
    
    
.stApp {
    /* Utilisez l'URL de votre image comme valeur de background-image */
    background-image: url('https://cdn.pixabay.com/photo/2023/05/24/17/49/ai-generated-8015425_640.jpg');
    background-size: contain; /* Ajuste la taille de l'image pour qu'elle soit contenue dans l'arrière-plan */
    background-repeat: no-repeat; /* Empêche la répétition de l'image */
    background-position: center center; /* Centre l'image horizontalement et verticalement */
    color: #ffffff;
    font-family: Arial, sans-serif;
    padding: 1rem;
}

    .stButton button {
        background-color:#866ef0;
        color:white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 0.25rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .stButton button:hover {
        background-color:#D3F7F4;
    }

    .stHeader {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    
    </style>
    """,
    unsafe_allow_html=True
)

######################## ################################################################################################################################################################################


def update_comments(df):
    openai.api_key = openai.api_key

    # Initialiser les nouvelles colonnes dans le DataFrame si elles n'existent pas encore
    if 'Résumé' not in df.columns:
        df['Résumé'] = ''
    if 'Titre' not in df.columns:
        df['Titre'] = ''
    if 'Points' not in df.columns:
        df['Points'] = ''
    if 'Script' not in df.columns:
        df['Script'] = ''

    for index, row in df.iterrows():
        commentaire = row['Comment']
        
        print(f"Traitement du commentaire à l'index {index}: {commentaire}")  # Debug

        try:
            # Générer le résumé du commentaire
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui aide à résumer des commentaires en français."},
                    {"role": "user", "content": f"Résume le commentaire suivant NB: écris uniquement en langue française n'écris surtout pas en anglais : \"{commentaire}\""}
                ],
                max_tokens=150,
                temperature=0.5,
                n=1,
            )
            resume_commentaire = response['choices'][0]['message']['content'].strip()
            print(f"Résumé pour l'index {index}: {resume_commentaire}")  # Debug

            # Générer le titre de la vidéo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui aide à créer des titres de vidéos YouTube en français."},
                    {"role": "user", "content": f"Via ce résumé de commentaire, donne un titre de vidéo YouTube NB: écris uniquement en langue française n'écris surtout pas en anglais : \"{resume_commentaire}\""}
                ],
                max_tokens=60,
                temperature=0.5,
            )
            titre_video = response['choices'][0]['message']['content'].strip()
            print(f"Titre pour l'index {index}: {titre_video}")  # Debug

            # Générer les points à aborder
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui aide à créer des points à aborder dans des vidéos YouTube en français."},
                    {"role": "user", "content": f"Donne les différents points que devrait aborder une vidéo basée sur ce titre. NB: écris uniquement en langue française n'écris surtout pas en anglais : \"{titre_video}\""}
                ],
                max_tokens=150,
                temperature=0.5,
            )
            points = response['choices'][0]['message']['content'].strip()
            print(f"Points pour l'index {index}: {points}")  # Debug

            # Générer le script de la vidéo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un générateur de script de vidéos YouTube."},
                    {"role": "user", "content": f"Considère que tu es un générateur de script de vidéos YouTube !! Rédige alors un script de vidéo YouTube africanisé basé sur les points que tu as donnés précédemment. NB: écris uniquement en langue française n'écris surtout pas en anglais : \"{points}\""}
                ],
                max_tokens=150,
                temperature=0.5,
            )
            script = response['choices'][0]['message']['content'].strip()
            print(f"Script pour l'index {index}: {script}")  # Debug

            # Mettre à jour le DataFrame avec les nouvelles informations
            df.at[index, 'Résumé'] = resume_commentaire
            df.at[index, 'Titre'] = titre_video
            df.at[index, 'Points'] = points
            df.at[index, 'Script'] = script

        except openai.OpenAIError as e:
            print(f"Une erreur d'API est survenue pour l'index {index}: {str(e)}")
        except Exception as e:
            print(f"Une erreur est survenue pour l'index {index}: {str(e)}")

    return df



######################## ################################################################################################################################################################################


def generate_html(df):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('prediction3.html')
    html = template.render(data=df.to_dict('records'))

    return html    


######################## ################################################################################################################################################################################


def main():
    html_titre = """ 
        <div style="padding: 13px; background-color: #866ef0; border: 5px solid #0d0c0c; border-radius: 10px;">
        <h1 style="color:#0d0c0c; text-align: center; background: linear-gradient(to right, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1));">🤖 ANALYSEUR DE SENTIMENT ET PREDICATEUR DE SUJETS🤖<small><br> Powered by An\'s Learning </h3></h1></h1>
        </div> 
        </div> 
        """
    
    st.markdown(html_titre, unsafe_allow_html = True)

    st.markdown('<p style="text-align: center;font-size:15px;" > <bold><center><h1 style="color:#D3F7F4"> <bold>UPLOADER LE FICHIER DONT VOUS VOULEZ AVOIR LA PREDICTION DE SUJET DE VIDEO YOUTUBE<h1></bold><p>', unsafe_allow_html=True)
 
    output_dir = 'Subjets_Prediction_Of_Videos'
    os.makedirs(output_dir, exist_ok=True)  

    uploaded_file = st.file_uploader("Entrer le fichier Excel", type=['xls', 'xlsx'])

    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        file_name = os.path.splitext(uploaded_file.name)[0]
        
        if st.button('Prediction'):
            updated_data = update_comments(data)

            html_content = generate_html(updated_data)
            html_file = StringIO(html_content)
            html_file.seek(0)
            
            b64 = base64.b64encode(html_file.read().encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="subject_Prediction_of_{file_name}.html">Télécharger les predictions</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.snow()
            

# Exécuter la fonction principale
if __name__ == "__main__":
    main()


######################## ################################################################################################################################################################################
