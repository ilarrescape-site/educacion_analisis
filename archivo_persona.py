import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os


load_dotenv()

#from archivo_rol import Rol
#from archivo_direccion import Direccion

# matricula_persona, 
# nombre_persona, 
# apellido_persona, 
# dni_persona, 
# fecha_nac_persona, 
# genero_persona, 
# email_persona, 
# contraseña_persona, 
# fk_direccion



class Persona:
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
            per.matricula_persona,
            per.nombre_persona,
            per.apellido_persona,
            per.dni_persona,
            per.fecha_nac_persona,
            per.genero_persona,
            per.email_persona,
            per.contraseña_persona,
            r.nombre_rol,
            ca.nombre_calle,
            dir.numero_direccion,
            dir.departamento,
            ci.nombre_ciudad,
            prov.nombre_provincia,
            p.nombre_pais
        
        from persona per
        join direccion dir on per.fk_direccion = dir.id_direccion
        join calle ca on  dir.fk_calle = ca.id_calle
        join persona_has_rol phr on per.matricula_persona = phr.fk_matricula_persona
        join rol r on phr.fk_rol = r.id_rol
        join ciudad_municipio ci on ca.fk_ciudad = ci.id_ciudad
        join provincia_estado prov on ci.fk_provincia = prov.id_provincia
        join pais p on prov.fk_pais = p.id_pais;
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result


objeto_persona = Persona()
st.dataframe(objeto_persona.fetch_data())