import pandas as pd
import streamlit as st

def clean_data():
    # Read data from different CSV files
    df_2019 = pd.read_csv("data/deces_2019.csv", sep=';', encoding='utf-8', low_memory=False)
    df_2020 = pd.read_csv("data/deces_2020.csv", sep=';', encoding='utf-8', low_memory=False)
    df_2021 = pd.read_csv("data/deces_2021.csv", sep=';', encoding='utf-8', low_memory=False)
    df_2022 = pd.read_csv("data/deces_2022.csv", sep=';', encoding='utf-8', low_memory=False)
    df_01_2023 = pd.read_csv("data/Deces_2023_M01.csv", sep=';', encoding='utf-8', low_memory=False)

    
    # Concatenate cleaned data frames
    #cleaned_data = pd.concat([df_2019, df_2020, df_2021, df_2022, df_01_2023], ignore_index=True)
    cleaned_data = pd.concat([df_01_2023], ignore_index=True)
    
    # je récupère le numéro du département à 2 chiffres (attention aux 10 premiers départements)
    def get_department(postal_code):
        postal_code = str(postal_code)
        
        try:
            
            if postal_code[:2] not in ['2A', '2B'] and int(postal_code[:2]) >= 97: # DOM TOM
                return postal_code[:3]
            return postal_code[:2]
        except:
            return ''
    
    # Renomage des colonnes
    cleaned_data = cleaned_data.rename(columns={
                            #'nomprenom':'nom',
                            'datenaiss':'date_naiss',
                            'lieunaiss':'dpt_lieu_naiss',
                            'sexe':'sexe',
                            'commnaiss':'ville',
                            'paysnaiss':'pays',
                            'datedeces':'date_dc',
                            'lieudeces':'dpt_lieu_dc',
                            'actedeces':'dpt_lieu_deces'})
    # je récupère les numéros de départements simplifiés pour les décès
    cleaned_data['dpt_deces'] = cleaned_data['dpt_lieu_dc'].apply(lambda x : get_department(x))
    
    # je récupère les numéros de départements simplifiés pour les naissance
    cleaned_data['dpt_lieu_naiss'] = cleaned_data['dpt_lieu_naiss'].apply(lambda x : get_department(x))

    # Transformer la data décès au bon format pour manipuler cette donnée 
    # clean date de décès
    cleaned_data['date_deces'] = pd.to_datetime(cleaned_data['date_dc'], format='%Y%m%d', errors='coerce')
    cleaned_data = cleaned_data.dropna(subset=['date_deces'])
    cleaned_data['date_deces'] = pd.to_datetime(cleaned_data['date_deces']).apply(lambda x: x.strftime('%Y-%m-%d'))
    cleaned_data['Mois'] = pd.to_datetime(cleaned_data['date_deces']).apply(lambda x: x.strftime('%Y-%m'))
    cleaned_data['Année'] = pd.to_datetime(cleaned_data['date_deces']).apply(lambda x: x.strftime('%Y'))
    cleaned_data = cleaned_data.drop('date_dc', axis=1)

    # clean date de naissance
    cleaned_data['date_naissance'] = pd.to_datetime(cleaned_data['date_naiss'], format='%Y%m%d', errors='coerce')
    cleaned_data = cleaned_data.dropna(subset=['date_naissance'])
    cleaned_data['date_naissance'] = pd.to_datetime(cleaned_data['date_naissance']).apply(lambda x: x.strftime('%Y-%m-%d'))
    cleaned_data = cleaned_data.drop('date_naiss', axis=1)

    # Complète Pays naissance
    cleaned_data['pays'] = cleaned_data['pays'].fillna('France')

    # Replace values in the 'sexe' column
    cleaned_data['sexe'] = cleaned_data['sexe'].replace({1: 'Masculin', 2: 'Féminin'})

    # add to the database the column deptament name
    departements_info = pd.read_excel('data/departements-francais.xls')
    departement_to_region = departements_info[['NOM', 'REGION']].set_index('NOM').to_dict()['REGION']
    number_to_departement = departements_info.set_index('NUMÉRO')['NOM'].to_dict()

    # Nettoyage des déparmtents
    cleaned_data = cleaned_data.rename(columns={'dpt_deces':'departement_number'})

    # Convert 'departement_number' to string
    cleaned_data['departement_number'] = cleaned_data['departement_number'].astype(str)

    # Update keys in the dictionary to be strings
    number_to_departement = {str(key): value for key, value in number_to_departement.items()}

    # Convert 'departement' to string
    cleaned_data['departement'] = cleaned_data['departement_number'].apply(lambda x: number_to_departement.get(x, "")).fillna('na')

    # je modifie les noms des départements qui ne sont pas corrects
    cleaned_data['departement'] = cleaned_data['departement'].str.replace("Val-D'Oise", "Val-d'Oise")
    cleaned_data['departement'] = cleaned_data['departement'].str.replace( 'Seine-St-Denis', "Seine-Saint-Denis")
    cleaned_data['departement'] = cleaned_data['departement'].str.replace( "Côtes d'Armor", "Côtes-d'Armor")
    cleaned_data['departement'] = cleaned_data['departement'].str.replace( "Vandée", "Vendée")

    # add a column with the city name
    commune_2021 = pd.read_csv('data/commune_2021.csv', sep=',', encoding='utf-8')
    commune_2021=commune_2021[['COM','NCC','NCCENR']]
    commune_2021 = commune_2021.rename(columns={'COM':'dpt_lieu_dc'})
    cleaned_data= pd.merge(cleaned_data, commune_2021, how='left', on = 'dpt_lieu_dc')
    commune_2021=commune_2021.rename(columns = {'NCCENR':'Nom de la communer'})

    # Convert 'date_deces' and 'date_naissance' columns to datetime
    cleaned_data['date_deces'] = pd.to_datetime(cleaned_data['date_deces'])
    cleaned_data['date_naissance'] = pd.to_datetime(cleaned_data['date_naissance'])

    # Calculate the difference in days between 'date_deces' and 'date_naissance'
    cleaned_data['diff_in_days'] = (cleaned_data['date_deces'] - cleaned_data['date_naissance']).dt.days
    cleaned_data['diff_in_years'] = round(cleaned_data['diff_in_days'] / 365,1)

    # organise the name / surname of the database
    cleaned_data[['nom_famille', 'prénom']]=cleaned_data.nomprenom.str.split('*', n=1, expand=True)
    cleaned_data[['prénom_1', 'prénom_2']]=cleaned_data.prénom.str.split(' ', n=1, expand=True)

    # je voudrais supprimer les slash dans les colonnes prénom / prénom_1 / prénom_2  , peut on faire une boucle for pour le faire ?
    cleaned_data['prénom'] = cleaned_data['prénom'].str.replace("/", "").fillna('')
    cleaned_data['prénom_1'] = cleaned_data['prénom_1'].str.replace("/", "").fillna('')
    cleaned_data['prénom_2'] = cleaned_data['prénom_2'].str.replace("/", "").fillna('')

    # j'aimerais changer la colonne nom de famille en mettant seuelement en majuscul la première lettre
    cleaned_data['nom_famille'] = cleaned_data['nom_famille'].str.capitalize()
    cleaned_data['prénom'] = cleaned_data['prénom'].str.capitalize()
    cleaned_data['prénom_1'] = cleaned_data['prénom_1'].str.capitalize()
    cleaned_data['prénom_2'] = cleaned_data['prénom_2'].str.capitalize()


    return cleaned_data
