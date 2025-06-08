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
    
objeto_rol = Rol()

st.dataframe(objeto_rol.fetch_data())