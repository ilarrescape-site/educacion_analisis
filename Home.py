import streamlit as st
from archivo_login import formulario_login

st.set_page_config(
    layout='wide',
    page_icon='👨🏻‍🏫',
    page_title='Sistema de Gestión Acedémica'
)

formulario_login()