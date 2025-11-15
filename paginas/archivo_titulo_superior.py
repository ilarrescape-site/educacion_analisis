import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


class TituloSuperior:
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
                tsup.id_titulo,
                tsup.nombre_titulo 
            from titulo_superior tsup
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result
