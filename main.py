import streamlit as st
from cleaning_script import clean_data



# Contenu de la page
st.title("Bienvenue sur Data Impromptus Glance (DIG)")
st.write("Evidemment je suis responsable de rien, c'est à vous de vous faire votre analyse",
         "attention le premier chargement peut être un peu long mais après c'est assez rapide")

# Load and clean the data
cleaned_data = clean_data()

# Streamlit page to use the cleaned data
st.write("Voici à quoi ressemble la BDD")
st.write(cleaned_data.sample(5))
