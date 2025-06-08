import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


from archivo_pais import Pais
from archivo_provincia_estado import ProvinciaEstado


class Ciudad:
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
                c.id_ciudad, 
                c.nombre_ciudad, 
                pe.nombre_provincia, 
                p.nombre_pais 
            from ciudad_municipio c
            join provincia_estado pe on c.fk_provincia = pe.id_provincia
            join pais p on pe.fk_pais = p.id_pais
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result
    
