import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


load_dotenv()

from archivo_persona import Persona

class Alumno(Persona):
    def __init__(self):
        super().__init__()

    def fetch_data(self):
        scirpt_consulta = """
        select
            pr.fk_matricula_persona,
            p.dni_persona,
            p.nombre_persona,
            p.apellido_persona,
            ts.nombre_titulo_secundario,
            r.nombre_rol
        from persona p
        join alumno al on p.matricula_persona = al.matricula_alumno
        join persona_has_rol pr on al.matricula_alumno = pr.fk_matricula_persona
        join rol r on r.id_rol = pr.fk_rol
        join titulo_secundario ts on al.fk_titulo_secundario = ts.id_titulo_secundario
        where r.nombre_rol = 'Alumno'
        """

        self.cursor.execute(scirpt_consulta)
        return self.cursor.fetchall()
    

object_alumno = Alumno()
diccionario_alumno = object_alumno.fetch_data()

st.dataframe(diccionario_alumno)