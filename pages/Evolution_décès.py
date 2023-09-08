import pandas as pd
import plotly  
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import streamlit as st

from cleaning_script import clean_data
from datetime import date, datetime, timedelta
from utils.streamlit_elements import page_config
from utils.streamlit_elements import FormElements, LayoutElements

# Use the cleaned data in your Streamlit pages
# For example:
st.title("Evolution Décès")


def show():
    st.title("Evolution Décès")
    st.write("Contenu de la page 1")


############################# Page config ############################

# ========================
# Filters
# ========================
# selection du site

with LayoutElements.custom_sidebar():
  with st.form("ca_form"):
    st.subheader("Paramètres de récupération de données")
    

    st.subheader("Paramètres d'analyses")

    period = FormElements.periodicity_field(
      label="Quelle périodicité pour le **volume** ?",
      options=("Année", "Mois")
    )

    n_rows = st.slider(
      label="Nombre de lignes",
      min_value=4,
      max_value=25,
      value=10
    )

    st.form_submit_button("Valider")



################# script qui permet de créer les tabs ################
(
  national,
  département,
  pays


) = st.tabs([
  "national",
  "département",
  "pays"
])

################# script data ################

# Load and clean the data
cleaned_data = clean_data()

# Streamlit page to use the cleaned data
# Convert the from_date to datetime64[ns]
from_date = st.date_input("Depuis le", datetime(2019, 1, 1))
from_date = pd.to_datetime(from_date)

# Load and clean the data
cleaned_data = clean_data()
current_data = cleaned_data[cleaned_data['date_deces'] >= from_date]

# compute the number of death per period
deces_period = current_data.groupby(period).count()['nomprenom'].reset_index()
deces_period = deces_period.rename(columns={'nomprenom': 'Nombre de décès'})

# compute the number of death per period and per departement
deces_period_dpt=current_data.groupby(['departement',period])['nomprenom'].count().reset_index().fillna('inconnu')

# compute chart with bar that shows all the departement
deces_period_dpt_chart = px.bar(deces_period_dpt, x=period, y='nomprenom', color='departement')

# compute the number of deceased person by country origin
db_ville_pays_naissance=current_data.groupby(['pays',period])['nomprenom'].count().reset_index().fillna('inconnu')

# compute chart with bar that shows all the countries
deces_period_pays_chart = px.bar(db_ville_pays_naissance, x=period, y='nomprenom', color='pays')

# Calculate the period multiplier based on the selected period
if period == "Année":
    period_multiplier = 1
elif period == "Mois":
    period_multiplier = 12
else:
    period_multiplier = 1  # Default to 1 if period is neither "Année" nor "Mois"

# Calculate the annualized growth rate using the period multiplier
deces_period['variation'] = round(deces_period['Nombre de décès'].pct_change(period_multiplier) * 100, 2)

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

color = 'LightSkyBlue'

# Add traces
fig.add_trace(
    go.Bar(x=deces_period[period], y=deces_period["Nombre de décès"], name="Nombre de décès par période",
          marker_color=color), 
)
# i'd like to add the parameter color in scatter but it doesn't work

fig.add_trace(
    go.Scatter(x=deces_period[period], y=deces_period["variation"], name="Croissance par rapport à l'année précédente"), 
    secondary_y=True, 
)
# Add figure title
fig.update_layout(
    title_text="Evolution du nombre de déccès",
)

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1))

# Load and clean the data with progress bar
with st.spinner("Loading and cleaning data..."):
    cleaned_data = clean_data()

# Show a message when data processing is done
st.success("Data loading and processing completed.")

with national:
  st.subheader("Evolution des décès au niveau national")
  #st.write(deces_period.tail(10))
  st.plotly_chart(fig, use_container_width=True)

with département:
  st.subheader("Evolution des décès au niveau département")
#  st.write(deces_period_dpt)
  st.plotly_chart(deces_period_dpt_chart, use_container_width=True)

with pays:
  st.subheader("Evolution des décès par pays d'origine")
  #st.write(db_ville_pays_naissance)
  st.plotly_chart(deces_period_pays_chart, use_container_width=True)

