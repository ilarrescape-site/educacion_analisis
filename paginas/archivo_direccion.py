import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


from ubicaciones.archivo_pais import Pais
from ubicaciones.archivo_provincia_estado import ProvinciaEstado
from ubicaciones.archivo_ciudad import Ciudad

class Direccion:
    def __init__(self): 
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        
    def insert_direccion(self, numero_direccion, departamento, fk_calle):
        script_insert_direccion = """
            insert into 
                direccion (numero_direccion, departamento, fk_calle)
                values
                (
                    %s, 
                    %s, 
                    %s
                )
        """
        self.cursor.execute(script_insert_direccion,(numero_direccion,departamento,fk_calle))
        self.connection.commit()

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

    def fetch_direccion_por_calle(self, id_calle):
        script_consulta = """
            select
                dir.id_direccion,
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
            where ca.id_calle = %s
        """
        self.cursor.execute(script_consulta,(id_calle,))
        result = self.cursor.fetchall()
        return result
