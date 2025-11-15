import streamlit as st

from ubicaciones.archivo_pais import main_paises
from ubicaciones.archivo_provincia_estado import main_provincia_estado
from ubicaciones.archivo_ciudad import main_ciudad
from ubicaciones.archivo_calle import main_calle

tab_paises, tab_provincias, tab_ciudades, tab_calle = st.tabs(['Países', 'Provincias', 'Ciudades', 'Calles'])

with tab_paises:
    main_paises()
with tab_provincias:
    main_provincia_estado()
with tab_ciudades:
    main_ciudad()
with tab_calle:
    main_calle()