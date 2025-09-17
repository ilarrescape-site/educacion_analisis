
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

class Pais:
    def __init__(self): 
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        #Sirve para que los resultados de las consultas se devuelvan como diccionarios
        #Podría establecer que la forma de los resultados sea tuplas, pero en este caso es más conveniente usar diccionarios
        self.cursor = self.connection.cursor(dictionary=True)
    
    def fetch_data(self):
        script_consulta = """
            select 
                p.id_pais, 
                p.nombre_pais 
            from pais p
        """

        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result
