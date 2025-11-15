import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


load_dotenv()

from pages.archivo_persona import Persona

class Profesor(Persona):
    def __init__(self):
        super().__init__()

    def fetch_data(self):
        scirpt_consulta = """
            select
                pr.fk_matricula_persona,
                p.dni_persona,
                p.nombre_persona,
                p.apellido_persona,
                r.nombre_rol,
                tsup.nombre_titulo
            from persona p
            join profesor prof on p.matricula_persona = prof.matricula_persona
            join persona_has_rol pr on prof.matricula_persona = pr.fk_matricula_persona
            join rol r on r.id_rol = pr.fk_rol
            join profesor_has_titulo pht on pht.fk_matricula_profesor = prof.matricula_persona
            join titulo_superior tsup on tsup.id_titulo = pht.fk_titulo
            where r.nombre_rol = 'Profesor'
        """

        self.cursor.execute(scirpt_consulta)
        return self.cursor.fetchall()
    
objeto_profesor = Profesor()

st.dataframe(objeto_profesor.fetch_data())
