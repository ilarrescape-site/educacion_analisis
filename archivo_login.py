import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import date
from random import random
from paginas.archivo_rol import Rol

import random
import time

class Login:
    def __init__(self): 
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def recuperar_datos_usuario(self, per_matricula, per_email, per_pass):
        
        # -- INPUT -> Credenciales a ingresar
        # -- -- matricula
        # -- -- correo electrónico
        # -- -- rol
        # -- -- contraseña

        # -- OUTPUT -> Lo que vamos a recuperar
        # -- -- Nombre
        # -- -- Apellido
        # -- -- dni
        # -- -- fecha_nacimiento
        # -- -- genero
        # -- -- matricula
        # -- -- correo electrónico
        # -- -- estado
        # -- -- rol
        query_recuperar = """
        select  persona.nombre_persona as 'Nombre',
                persona.apellido_persona as 'Apellido',
                persona.dni_persona as 'DNI',
                persona.fecha_nac_persona as 'Fecha de Nacimiento',
                persona.genero_persona as 'Género',
                persona.matricula_persona as 'Matrícula',
                persona.email_persona as 'Correo electrónico',
                persona.estado as 'Estado',
                rol.nombre_rol as 'Rol'

        from    persona
        join    persona_has_rol on persona_has_rol.fk_matricula_persona = persona.matricula_persona
        join    rol on rol.id_rol = persona_has_rol.fk_rol

        where   persona.matricula_persona = %s and persona.email_persona = %s
                and persona.contraseña_persona = %s
        """
        self.cursor.execute(query_recuperar,(per_matricula, per_email, per_pass))
        return self.cursor.fetchone()

def formulario_login():
    objeto_login = Login()

    _col_relleno_iz, _col_formulario, _col_relleno_derecha = st.columns([3,3,3])
    with _col_formulario:
        _contenedor_login = st.container(border= True)
        with _contenedor_login:
            txt_email = st.text_input('Ingrese el correo electrónico: ')
            _col_matricula, _col_rol = st.columns(2)
            with _col_matricula:
                txt_matrícula = st.text_input('Ingrese su matrícula: ')
            with _col_rol:
                objeto_rol = Rol()
                lista_dic_roles = objeto_rol.fetch_data()
                dic_roles = {dic['nombre_rol']:dic['id_rol'] for dic in lista_dic_roles}
                lista_rol = list(dic_roles.keys())
                select_rol = st.selectbox("Seleccionar Rol", options= lista_rol)
            txt_contraseña = st.text_input("Ingrese contraseña: ", type='password')
            _col_inicio_sesion, _col_registro_usuario = st.columns(2)
            with _col_inicio_sesion:
                btn_iniciar_sesion = st.button('Inciar Sesión', type='primary', use_container_width=True)
            with _col_registro_usuario:
                btn_registrar_usuario = st.button('Registrarse', type='secondary', use_container_width= True)
            if btn_iniciar_sesion:
                if not(txt_email and txt_contraseña and txt_matrícula):
                    st.error('Falta ingresar datos')
                    st.stop()
                

                dic_login = objeto_login.recuperar_datos_usuario(txt_matrícula, txt_email, txt_contraseña)
                if dic_login:
                    if dic_login['Estado'] == 'inactivo':
                        st.error('Ha sido suspendido por inactividad. Comunícarse con un directivo')
                        st.stop()
                    if dic_login['Estado'] == 'suspendido':
                        st.error('Ha sido suspendido por conducta. Comunícarse con un directivo')
                        st.stop()
                    if dic_login['Estado'] == 'pendiente':
                        st.error('Usted está pendiente de aprobación. Comunícarse con un directivo')
                        st.stop()
                    if dic_login['Rol'] != select_rol:
                        st.error(f'Su rol es incorrecto. Comunícarse con un directivo')
                        st.stop()
                    st.success('Inicio de sesión exitoso')
                    st.write(objeto_login.recuperar_datos_usuario(txt_matrícula, txt_email, txt_contraseña))
                else:
                    st.error('Las credenciales son incorrectas')