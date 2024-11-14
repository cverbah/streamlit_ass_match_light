import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
from dotenv import load_dotenv

# env
load_dotenv()
URL_MATCH_LIGHT = os.environ["URL_MATCH_LIGHT"]

st.set_page_config(
    page_title="Match asistido light",
    page_icon=":robot_face:",
    layout="wide",
)
st.title('Match asistido light ALL in ONE')
st.write('Primero seleccione los parámetros en el menú de la izquierda')

# load available retails
df_retails = pd.read_csv('retails_ass_match.csv')
client_id = 0  # por ahora default 0, da igual si es cliente o no
competitors_only = 0  # por ahora default 0, da igual si es cliente o no
if 'namespace' not in st.session_state:
    st.session_state.namespace = 'pet_supermarket_retails'

if 'selected_type' not in st.session_state:
    st.session_state.selected_type = 'mascotas'

if 'selected_retail_to_search' not in st.session_state:
    st.session_state.selected_retail_to_match = ''

if 'selected_neighbours' not in st.session_state:
    st.session_state.selected_neighbours = 50

if 'selected_distance' not in st.session_state:
    st.session_state.selected_distance = 0.93

if 'selected_var_price' not in st.session_state:
    st.session_state.selected_var_price = 0.3

if 'selected_active_skus' not in st.session_state:
    st.session_state.selected_active_skus = 'skus activos'

if 'selected_retails_to_search' not in st.session_state:
    st.session_state.selected_retails_to_search = ''

with st.sidebar:
    st.title(':gear: Parámetros')
    # tipo
    retails_type = df_retails.tipo.unique().tolist()
    st.session_state.selected_type = st.selectbox('Tipo retail:', retails_type)

    # retail to match
    retails = df_retails[df_retails.tipo == st.session_state.selected_type].name.unique().tolist()
    st.session_state.selected_retail_to_match = st.selectbox('Retail a matchear:', sorted(retails))
    st.session_state.retail_id_to_match = df_retails[df_retails.name == st.session_state.selected_retail_to_match].retail_id.tolist()[0]

    # retails to search
    retails_available = sorted(list(filter(lambda x: x != st.session_state.selected_retail_to_match, retails)))
    st.session_state.selected_retails_to_search = st.multiselect('Retails a buscar:', retails_available)
    retails_to_search = df_retails[df_retails.name.isin(st.session_state.selected_retails_to_search)].retail_id.tolist()
    format_retails_to_search = ''.join([f'retails_to_search={i}&' for i in retails_to_search])
    # date time
    start_date = st.date_input("Skus a matchear creados Desde:", key='start_date')
    start_date_str = start_date.strftime("%Y-%m-%d")
    default_time = '00:00:00'

    # active skus?
    st.session_state.selected_active_skus = st.selectbox('Buscar skus:', ['skus activos', 'skus activos e inactivos'])
    if st.session_state.selected_active_skus == 'skus activos':
        active_skus = 1
    else:
        active_skus = 0

    # neighbours
    st.write('')
    st.write('')
    st.session_state.selected_neighbours = st.selectbox('Vecinos cercanos:', [30, 40, 50, 60])
    # cosine
    st.session_state.selected_distance = st.slider("Cosine distance:",
                                                      min_value=0.85, max_value=1.0, step=0.01,
                                                      value=st.session_state.selected_distance)
    # var price
    st.session_state.selected_var_price = st.slider("Máxima variación de precio:",
                                                   min_value=0.0, max_value=1.0, step=0.01,
                                                   value=st.session_state.selected_var_price)


## search

url = f'https://{URL_MATCH_LIGHT}?q_neighbours={st.session_state.selected_neighbours}&client_id={client_id}\
&retail_id={st.session_state.retail_id_to_match}&cosine_distance={st.session_state.selected_distance}&max_price_var={st.session_state.selected_var_price}&\
start_date_to_search={start_date_str}&start_time_to_search={default_time}&{format_retails_to_search}&competitors_only={competitors_only}&\
pinecone_namespace={st.session_state.namespace}&active_skus={active_skus}'
#st.write(url)

if st.button('Buscar candidatos'):
    with st.spinner('Buscando candidatos.. (esto puede demorar dependiendo de la fecha seleccionada principalmente)'):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    try:
                        df = pd.DataFrame(data)
                        print(f'candidates found with the selected parameters')
                        st.dataframe(df)
                    except:
                        st.warning(f'No se han encontrado productos nuevos o candidatos con los parámetros seleccionados')
                else:
                    st.write('No se han encontrado productos nuevos o candidatos con los parámetros seleccionados')
            else:
                st.error({response.status_code})
        except Exception as e:
            st.error(f'Se ha producido un error: {e}')





