import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


load_dotenv()

class Rol:
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
            r.id_rol,
            r.nombre_rol
        from rol r
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result
    def fetch_data_directivo(self):
        script_consulta = """
        select 
            r.id_rol,
            r.nombre_rol
        from rol r
        Where r.nombre_rol = "Director" or r.nombre_rol = "Regente" or r.nombre_rol = "Secretario" or r.nombre_rol = "Preceptor"
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result