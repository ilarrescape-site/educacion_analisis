import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


from archivo_pais import Pais
from archivo_provincia_estado import ProvinciaEstado
from archivo_ciudad import Ciudad

class Direccion:
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
                ca.nombre_calle, 
                dir.numero_direccion,
                dir.departamento,
                c.nombre_ciudad, 
                pe.nombre_provincia, 
                p.nombre_pais
            from direccion dir 
            join calle ca on dir.fk_calle = ca.id_calle
            join ciudad_municipio c on ca.fk_ciudad = c.id_ciudad
            join provincia_estado pe on c.fk_provincia = pe.id_provincia
            join pais p on pe.fk_pais = p.id_pais
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result


object_direccion = Direccion()

df_direccion = pd.DataFrame(object_direccion.fetch_data())

st.dataframe(df_direccion)