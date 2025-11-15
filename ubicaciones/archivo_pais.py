
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os
import time
from collections import defaultdict

if 'eliminar_pais_completo' not in st.session_state:
    st.session_state['eliminar_pais_completo'] = None

import time

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
                p.id_pais as 'ID País', 
                p.nombre_pais as 'Nombre' 
            from pais p
        """

        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result

    def add_data(self, nombre_pais):
        script_insercion = """
            INSERT 
                into pais(nombre_pais) 
            VALUES (%s)
        """
        self.cursor.execute(script_insercion, (nombre_pais,))
        self.connection.commit()

    def _fetch_arbol(self, pk_pais):
        """
        Trae TODA la jerarquía con LEFT JOIN para incluir nodos sin hijos.
        """
        sql = """
        SELECT 
            p.id_pais, p.nombre_pais,
            pr.id_provincia, pr.nombre_provincia,
            c.id_ciudad, c.nombre_ciudad,
            ca.id_calle, ca.nombre_calle,
            d.id_direccion, d.numero_direccion, d.departamento
        FROM pais AS p
        LEFT JOIN provincia_estado AS pr ON pr.fk_pais = p.id_pais
        LEFT JOIN ciudad_municipio AS c ON c.fk_provincia = pr.id_provincia
        LEFT JOIN calle AS ca ON ca.fk_ciudad = c.id_ciudad
        LEFT JOIN direccion AS d ON d.fk_calle = ca.id_calle
        WHERE p.id_pais = %s
        ORDER BY 
            pr.nombre_provincia IS NULL, pr.nombre_provincia,
            c.nombre_ciudad IS NULL, c.nombre_ciudad,
            ca.nombre_calle IS NULL, ca.nombre_calle,
            d.numero_direccion IS NULL, d.numero_direccion;
        """
        self.cursor.execute(sql, (pk_pais,))
        rows = self.cursor.fetchall()
        return rows

    def delete_data(self, pk_pais):
        # -> Eliminar las direcciones
        script_eliminar_paises = """
        delete pais from pais
            where id_pais = %s
        """
        self.cursor.execute(script_eliminar_paises, (pk_pais,))
        self.connection.commit()
    def edit_data(self, nombre_pais, pk_pais):
        script_edicion_paises = """
               update 
                    pais 
                set 
                    nombre_pais = %s
                where 
                    id_pais = %s;
        """
        self.cursor.execute(script_edicion_paises, (nombre_pais, pk_pais))
        self.connection.commit()

class ComponentesPais():
    def __init__(self):
        self.db_pais = Pais()
    
    @st.dialog("Eliminar País")
    def formulario_eliminar(self, serie):
        txt_pais_a_modificar = st.text_input('Nombre del país: ', value=serie['Nombre'], disabled= True)
        diccionario_pais = {dic_pais['Nombre']:dic_pais['ID País']  for dic_pais in self.db_pais.fetch_data()}
        id_pais = diccionario_pais[txt_pais_a_modificar]
        self.mostrar_arbol_pais(id_pais)
        btn_confirmar = st.button("Confirmar", type='primary')
        if btn_confirmar:
            self.db_pais.delete_data(id_pais)
            st.write('Datos eliminados correctamente')
            time.sleep(2)
            st.rerun()

    @st.dialog('Modificar País')
    def formulario_modificar(self, serie):
        txt_pais_a_modificar = st.text_input('Ingrese el nuevo nombre: ', value=serie['Nombre'])
        _col_relleno, _col_editar  = st.columns(2)
        with _col_editar:
            btn_editar = st.button('Guardar Edición', use_container_width=True)
        if btn_editar:
            if txt_pais_a_modificar:
                lista_nombres = [dic_pais['Nombre'] for dic_pais in self.db_pais.fetch_data()]
                if txt_pais_a_modificar in lista_nombres:
                    st.warning('⚠️ El país ingresado ya se encuentra en la base de datos')
                else:
                    self.db_pais.edit_data(txt_pais_a_modificar, int(serie['ID País']))
                    st.success('El país fue editado con éxito 😎')
                    time.sleep(2)
                    st.rerun()

            else:
                st.warning('⚠️ El campo de texto no contiene valores')
        

    
    def mostrar_datos_pais(self):
        dic_pais = self.db_pais.fetch_data()
        df_pais = pd.DataFrame(dic_pais)

        dic_pais_seleccionado = st.dataframe(
                                                df_pais,
                                                hide_index=True,
                                                height=220,
                                                selection_mode='single-row',
                                                on_select= 'rerun')
        
        indice_selccionado = dic_pais_seleccionado['selection']['rows'][0] if dic_pais_seleccionado['selection']['rows'] else None

        
        serie_seleccionada = df_pais.loc[indice_selccionado] if indice_selccionado!= None else None
        
        if indice_selccionado!= None:
            _col_relleno, _col_eliminación, _col_edicion = st.columns([2,1,1])
            with _col_eliminación:
                btn_eliminar = st.button("Eliminar", use_container_width=True, icon='🗑️')
                if btn_eliminar:
                    self.formulario_eliminar(serie_seleccionada)
            with _col_edicion:
                btn_editar = st.button("Editar", use_container_width=True, icon='✏️')
                if btn_editar:
                    self.formulario_modificar(serie_seleccionada)
    
    def mostrar_arbol_pais(self, pk_pais_a_eliminar):
        rows = self.db_pais._fetch_arbol(pk_pais_a_eliminar)
        arbol = {}
        markdown = ""
        ultimo_pais, ultimo_prov, ultimo_ciudad, ultimo_calle = None, None, None, None

        for r in rows:
            pais = r["nombre_pais"]
            prov = r["nombre_provincia"]
            ciudad = r["nombre_ciudad"]
            calle = r["nombre_calle"]
            dir_id = r["id_direccion"]
            numero = r["numero_direccion"]
            depto = r["departamento"]

            if pais and pais!=ultimo_pais:
                # markdown += f"- {pais}\n"
                arbol[pais] = {}
                ultimo_pais, ultimo_prov, ultimo_ciudad, ultimo_calle = pais, None, None, None

            if prov and prov!=ultimo_prov:
                markdown+= f"   - {prov}\n"
                arbol[pais][prov] = {}
                ultimo_prov, ultimo_ciudad, ultimo_calle = prov, None, None

            if ciudad and ciudad!=ultimo_ciudad:
                markdown +=f"       - {ciudad}\n"
                arbol[pais][prov][ciudad] = {}
                ultimo_ciudad, ultimo_calle = ciudad, None

            if calle and calle != ultimo_calle:
                markdown += f"          - {calle}\n"
                arbol[pais][prov][ciudad][calle] = []
                ultimo_calle = calle
    
        cantidad_lineas = len(markdown.splitlines())
        if markdown!="":
            _contenedor_eliminar = st.container(border= False, height=250 if cantidad_lineas > 8 else cantidad_lineas+125)
            with _contenedor_eliminar:
                cadena_titulo = f"""
                    ##### Importante: Si elimina el país {ultimo_pais}, usted eliminará
                """
                cadena_markdown = f"{markdown}"
                st.error(cadena_titulo)
                st.write(cadena_markdown)
            st.write('---')
        else:
            st.info('El país no tiene dependencias cargadas')


    def agregar_datos_pais(self):
        _contenedor_pais = st.container(border=True,height= 220, vertical_alignment='center')
        with _contenedor_pais:
            with st.form(clear_on_submit = True, key='guardar-nuevo-pais', border=False):
                txt_pais = st.text_input('Ingresar el nombre del país: ', max_chars=45)
                #btn_guardar_pais = st.button('Guardar', icon='💾')
                
                btn_guardar_pais = st.form_submit_button('Guardar', icon='💾')

                lista_paises = [dic['Nombre'].title() for dic in self.db_pais.fetch_data()]
                
                txt_pais = txt_pais.title().strip()
                if btn_guardar_pais:
                    if txt_pais:
                        if txt_pais not in lista_paises:
                            self.db_pais.add_data(txt_pais)
                            st.success('Los datos fueron ingresados con éxito')
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.warning('El país que usted ingresó ya existe en la base de datos')
                            time.sleep(2)
                            st.rerun()
                    else:
                        st.error('No tiene un país ingresado')
                        time.sleep(2)
                        st.rerun()
def main_paises():
    st.subheader('Manejo de países')    
    _col_formulario_pais, _col_tabla_pais = st.columns(2)
    objeto_pais = ComponentesPais()
    with _col_formulario_pais:
        objeto_pais.agregar_datos_pais()
    with _col_tabla_pais:
        objeto_pais.mostrar_datos_pais()
