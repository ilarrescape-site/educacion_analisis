
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os

import time

from ubicaciones.archivo_pais import Pais

class ProvinciaEstado:
    def __init__(self): 
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        
    def fetch_data(self):
        script_consulta = """
            select 
                pe.id_provincia as 'ID', 
                pe.nombre_provincia as 'Provincia', 
                p.nombre_pais as 'País'
            from provincia_estado pe
            join pais p on pe.fk_pais = p.id_pais
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result

    def fetch_data_fitro_pais(self,id_pais_buscado):
        script_filtro_persona ="""
            select 
                pe.id_provincia, 
                pe.nombre_provincia, 
                p.nombre_pais 
            from provincia_estado pe
            join pais p on pe.fk_pais = p.id_pais
            where p.id_pais = %s
        """
        self.cursor.execute(script_filtro_persona,(id_pais_buscado,))
        result = self.cursor.fetchall()
        return result
    
    def add_data(self, nombre_provincia, id_pais):
        script_insercion = """
            INSERT 
                into provincia_estado(nombre_provincia, fk_pais) 
            VALUES (%s,%s)
        """
        self.cursor.execute(script_insercion, (nombre_provincia,id_pais))
        self.connection.commit()



class ComponentesProvincias():
    def __init__(self):
        self.db_provincia = ProvinciaEstado()
        self.db_pais = Pais()

    def mostrar_datos_Provincias(self):
        dic_Provincias = self.db_provincia.fetch_data()
        df_Provincias = pd.DataFrame(dic_Provincias)
        dic_Provincia_seleccionada = st.dataframe(df_Provincias, 
                                            hide_index=True,
                                            selection_mode='single-row',
                                            on_select = 'rerun',
                                            height = 270)
    
    def agregar_datos_provincia(self):
        _contenedor_provincia = st.container(border=True,height= 270, vertical_alignment='center')
        with _contenedor_provincia:
            with st.form(clear_on_submit = True, key='guardar-nueva_provincia', border=False):
                txt_provincia = st.text_input('Ingresar el nombre del provincia/estado/departamento: ', max_chars=45)
                #btn_guardar_provincia = st.button('Guardar', icon='💾')
                
                dic_paises = {dic['Nombre']:dic['ID País'] for dic in self.db_pais.fetch_data()}

                lista_pais = list(dic_paises.keys())

                select_pais = st.selectbox('Seleccione el país: ', lista_pais)

                btn_guardar_provincia = st.form_submit_button('Guardar', icon='💾')

                lista_provincias = [{dic['Provincia'].title():dic['País']} for dic in self.db_provincia.fetch_data()]
                
                dic_nueva_provincia = {txt_provincia:select_pais}

                txt_provincia = txt_provincia.title().strip()
                if btn_guardar_provincia:
                    if txt_provincia:
                        if dic_nueva_provincia not in lista_provincias:
                            id_pais = dic_paises[select_pais]
                            self.db_provincia.add_data(txt_provincia, id_pais)
                            st.success('Los datos fueron ingresados con éxito')
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.warning('La provincia que usted ingresó ya existe en la base de datos')
                            time.sleep(2)
                            st.rerun()
                    else:
                        st.error('No tiene una provincia ingresada')
                        time.sleep(2)
                        st.rerun()

def main_provincia_estado():
    objeto_provincia = ComponentesProvincias()
    objeto_provincia.mostrar_datos_Provincias()
    objeto_provincia.agregar_datos_provincia()