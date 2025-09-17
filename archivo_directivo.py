import mysql.connector
import streamlit as st

from datetime import date
from dotenv import load_dotenv
import pandas as pd
import time
import os

if 'id_direccion' not in st.session_state:
    st.session_state['id_direccion'] = 0

if 'cadena_direccion' not in st.session_state:
    st.session_state['cadena_direccion'] = None

load_dotenv()

from archivo_persona import Persona
from archivo_pais import Pais
from archivo_provincia_estado import ProvinciaEstado
from archivo_ciudad import Ciudad
from archivo_calle import Calle
from archivo_direccion import Direccion
from archivo_rol import Rol
from archivo_titulo_superior import TituloSuperior

class Directivo(Persona):
    def __init__(self):
        super().__init__()

    def fetch_data(self):
        scirpt_consulta = """
            select
                pr.fk_matricula_persona as 'Matrícula',
                p.dni_persona as 'DNI',
                p.nombre_persona as 'Nombre',
                p.apellido_persona as 'Apellido',
                r.nombre_rol as 'Rol',
                tsup.nombre_titulo as 'Título'
            from persona p
            join directivo dir on p.matricula_persona = dir.matricula_directivo
            join persona_has_rol pr on dir.matricula_directivo = pr.fk_matricula_persona
            join rol r on r.id_rol = pr.fk_rol
            join directivo_has_titulo dht on dht.fk_matricula_directivo = dir.matricula_directivo
            join titulo_superior tsup on tsup.id_titulo = dht.fk_titulo
            where r.nombre_rol = 'Director' or r.nombre_rol = 'Preceptor'
            order by p.nombre_persona
        """

        self.cursor.execute(scirpt_consulta)
        return self.cursor.fetchall()

    def add_data(self, matricula_persona, nombre_persona, apellido_persona, dni_persona, fecha_nac_persona, genero_persona, email_persona, contraseña_persona, fk_direccion, rol, titulo):
        script_insert_persona = """
            insert into 
                persona (
                    matricula_persona, 
                    nombre_persona, 
                    apellido_persona, 
                    dni_persona, 
                    fecha_nac_persona, 
                    genero_persona, 
                    email_persona, 
                    contraseña_persona, 
                    fk_direccion
                )
                values
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                    )
        """
        self.cursor.execute(script_insert_persona, (matricula_persona, nombre_persona, apellido_persona, dni_persona, fecha_nac_persona, genero_persona, email_persona, contraseña_persona, fk_direccion))
        
        script_insert_directivo = """
            Insert into directivo (matricula_directivo) values (%s)
        """
        self.cursor.execute(script_insert_directivo,(matricula_persona,))
        
        script_insert_rol = """
            insert into persona_has_rol (fk_matricula_persona, fk_rol) values(%s,%s)
        """
        self.cursor.execute(script_insert_rol,(matricula_persona,rol))

        script_insert_titulo = """
            insert into directivo_has_titulo (fk_matricula_directivo, fk_titulo) values(%s,%s)
        """
        self.cursor.execute(script_insert_titulo,(matricula_persona,titulo))
        
        self.connection.commit()


class ComponentesDirectivo:
    def __init__(self):
        self.db_directivo = Directivo()
        self.db_pais = Pais()
        self.db_provincia = ProvinciaEstado()
        self.db_ciudad = Ciudad()
        self.db_calle = Calle()
        self.db_direccion = Direccion() 
        self.db_rol = Rol()
        self.db_tsup = TituloSuperior()

    def diplay_data_components(self):
        _contenedor_tabla_directivo = st.container(border= True)
        
        data_directivo = self.db_directivo.fetch_data()
        with _contenedor_tabla_directivo:
            st.write('#### Tabla de Directivos')
            st.dataframe(data_directivo,
                        height=600,
                        use_container_width= True,
                        selection_mode = 'single-row',
                        on_select='rerun'
                        )
        return data_directivo
    
    @st.dialog('Seleccionar Direccion')
    def seleccionar_direccion(self,lista_calles, diccionario_calles, calle_seleccionada,df_direcciones):
        diccionario_seleccionado = st.dataframe(df_direcciones,
                                            column_order=['nombre_calle','numero_direccion','departamento'],
                                            hide_index=True,
                                            selection_mode='single-row',
                                            on_select='rerun')
        
        indice_seleccion = diccionario_seleccionado['selection']['rows'][0] if len(diccionario_seleccionado['selection']['rows'])>0 else None
        if indice_seleccion != None:
            serie_direccion_seleccionada = df_direcciones.loc[indice_seleccion]
            id_seleccionado = serie_direccion_seleccionada.loc['id_direccion']
            st.write(id_seleccionado)
            lista_claves = ['nombre_calle', 'numero_direccion', 'departamento']
            valores = [str(serie_direccion_seleccionada.get(clave,''))for clave in lista_claves]
            cadena_direccion = str(valores[0])+' al '+ str(valores[1])
            if valores[2]!= 'None':
                cadena_direccion = cadena_direccion + ', departamento ' + valores[2]
            if st.button('Guardar dirección'):
                st.session_state['id_direccion'] = int(id_seleccionado)
                st.session_state['cadena_direccion'] = cadena_direccion
                st.rerun()
        else:
            st.warning('No se seleccionó ningún elemento')
    
    @st.dialog('Agregar Dirección',width='small')
    def agregar_direccion(self, diccionario_calles, df_direcciones, calle_seleccionada):
        
        st.dataframe(df_direcciones,
                        column_order = ['nombre_calle','numero_direccion','departamento'],
                        hide_index=True)

        nombre_calle = st.text_input('Nombre de la calle', value=calle_seleccionada, disabled = True)
        id_calle = diccionario_calles[nombre_calle] if diccionario_calles else None
        _col_num_direccion, _col_departamento = st.columns([3,2])
        with _col_num_direccion:
            numero_direccion = st.number_input('Ingresar Número: ', step=1)
        with _col_departamento:
            departamento = st.text_input('Nº Depto: ')
        if st.button('Guardar'):
            if nombre_calle and numero_direccion and departamento:
                self.db_direccion.insert_direccion(int(numero_direccion),departamento,int(id_calle))
                st.success('Datos agregados correctamente')
                time.sleep(2)
                st.rerun()
            elif nombre_calle and numero_direccion:
                self.db_direccion.insert_direccion(int(numero_direccion),None,int(id_calle))
                st.success('Datos agregados correctamente')
                time.sleep(2)
                st.rerun()

            else:
                st.error('Error: Faltan datos')

    def add_data_components(self):
        _container_formulario_directivo = st.container(border = True)
        with _container_formulario_directivo:
            st.write('#### Ingresar datos de Directivo')

            _columa_nombre, _columna_apellido = st.columns([2,2])
            with _columa_nombre:
                nombre_directivo = st.text_input("Ingresar Nombre: ", max_chars = 45)
            with _columna_apellido:
                apellido_directivo = st.text_input("Ingresar Apellido: ", max_chars = 45)
            
            _columna_dni,_columna_nacimiento,_columna_genero = st.columns([3,4,2])
            with _columna_dni:
                dni_directivo = st.number_input("DNI: ", step=100)
            with _columna_nacimiento:
                fecha_nacimiento_persona = st.date_input("Fecha de Nacimiento: ", format="DD/MM/YYYY", min_value= date(1910,1,1))
            with _columna_genero:
                lista_genero = ['M','F','O']
                genero_persona = st.selectbox("Género: ", lista_genero)
            
            email_persona = st.text_input("Correo Electrónico: ")
            
            _columna_contraseña, _columna_confirmar = st.columns(2)
            with _columna_contraseña:
                contraseña_persona = st.text_input("Ingrese Contraseña: ", type="password")
            with _columna_confirmar:
                confirmar_contraseña_persona = st.text_input("Confirmar Contraseña: ", type="password")
            
            _columa_pais, _columna_provincia = st.columns(2)

            with _columa_pais:
                lista_diccionario_pais = self.db_pais.fetch_data()
                
                # diccionario_paises = {}
                # for i in lista_diccionario_pais:
                #     diccionario_paises.update({i['nombre_pais']:i['id_pais']})

                # st.write(diccionario_paises)
                
                diccionario_pais = {diccionario['nombre_pais']: diccionario['id_pais'] for diccionario in lista_diccionario_pais}
                

                lista_paises = list(diccionario_pais.keys())

                pais_persona = st.selectbox("País de Residencia: ", lista_paises)

                id_pais = diccionario_pais[pais_persona]


            with _columna_provincia:
                lista_diccionario_provincias = self.db_provincia.fetch_data_fitro_pais(id_pais)

                diccionario_provincia = {diccionario['nombre_provincia']:diccionario['id_provincia'] for diccionario in lista_diccionario_provincias}
                
                lista_provincia = list(diccionario_provincia.keys())

                provincia_persona = st.selectbox("Provincia o Estado: ", lista_provincia)

                id_provincia_buscada = diccionario_provincia[provincia_persona] if provincia_persona !=None else None

            _columna_ciudad, _columna_calle = st.columns([3,3])
            

            #Acá me quedé la última clase
            with _columna_ciudad:
                lista_diccionario_ciudades = self.db_ciudad.fetch_data_filtro_provincia(id_provincia_buscada)

                diccionario_ciudades = {diccionario['nombre_ciudad']:diccionario['id_ciudad'] for diccionario in lista_diccionario_ciudades}
            
                lista_ciudades = list(diccionario_ciudades.keys())

                ciudad_seleccionada = st.selectbox("Ciudad: ", lista_ciudades)

                id_ciudad = diccionario_ciudades[ciudad_seleccionada] if ciudad_seleccionada != None else None

            with _columna_calle:
                lista_diccionario_calles = self.db_calle.fectch_data_por_ciudad(id_ciudad)
                diccionario_calles = {diccionario['nombre_calle']:diccionario['id_calle'] for diccionario in lista_diccionario_calles}
                
                lista_calles = list(diccionario_calles.keys())
                calle_seleccionada = st.selectbox('Calle: ', lista_calles)

                id_calle = diccionario_calles[calle_seleccionada] if calle_seleccionada != None else None

            lista_diccionario_direcciones = self.db_direccion.fetch_direccion_por_calle(id_calle)

            df_direcciones = pd.DataFrame(lista_diccionario_direcciones)


            st.write('---')
            _col_boton_agregar_direccion, _col_boton_seleccionar_direccion, _col_datos_direccion = st.columns([2,2,4])
            with _col_boton_agregar_direccion:
                if st.button('Nueva Dirección'):
                    self.agregar_direccion(diccionario_calles, df_direcciones, calle_seleccionada)
            with _col_boton_seleccionar_direccion:
                if st.button('Buscar Dirección'):
                    self.seleccionar_direccion(lista_calles, diccionario_calles, calle_seleccionada,df_direcciones)
            with _col_datos_direccion:
                if st.session_state['cadena_direccion']!=None:
                    st.write(f'###### {st.session_state['cadena_direccion']}')
                else:
                    st.write('###### ⚠️ No tiene una direccion seleccionada.')
            st.write('---')
            
            _columna_titulos, _columna_roles = st.columns(2)

            with _columna_titulos:
                lista_diccionarios_titulos = self.db_tsup.fetch_data()

                diccionario_titulos = {dic['nombre_titulo']:dic['id_titulo'] for dic in lista_diccionarios_titulos}

                lista_titulos = list(diccionario_titulos.keys())
                titulo_superior = st.selectbox('Seleccionar un título: ', lista_titulos)

                id_titulo = diccionario_titulos[titulo_superior]

            with _columna_roles:
                lista_diccionarios_roles = self.db_rol.fetch_data_directivo()

                diccionario_roles_directivos = {diccionario['nombre_rol']:diccionario['id_rol'] for diccionario in lista_diccionarios_roles}

                lista_roles_directivos = list(diccionario_roles_directivos.keys())

                rol_seleccionado = st.selectbox('Seleccionar Rol: ', lista_roles_directivos)

                id_rol = diccionario_roles_directivos[rol_seleccionado]
            # La matrícula va a ser una combinación de las tres primeras letras del nombre, las tres primeras letras del apellido
            # y los 6 últimos dígitos del dni
            _columna_relleno, _columna_guardar_datos = st.columns(2)
            
            with _columna_guardar_datos:
                if st.button('Guardar Directivo', use_container_width= True):
                    cadena_dni_directivo = str(dni_directivo)
                    matricula_directivo = nombre_directivo[0:3] +'-'+apellido_directivo[0:3]+'-'+cadena_dni_directivo[3:]
                    if nombre_directivo and apellido_directivo and dni_directivo and fecha_nacimiento_persona and genero_persona and email_persona:
                        if st.session_state['id_direccion']!=0:
                            if contraseña_persona and contraseña_persona == confirmar_contraseña_persona:
                                self.db_directivo.add_data(matricula_directivo, nombre_directivo, apellido_directivo, dni_directivo, fecha_nacimiento_persona, genero_persona, email_persona, contraseña_persona, st.session_state['id_direccion'], id_rol, id_titulo)
                                st.success('Directivo Guardado')
                            elif contraseña_persona and contraseña_persona != confirmar_contraseña_persona:
                                st.error('La contraseñas no coinciden')
                            elif contraseña_persona == None and confirmar_contraseña_persona == None:
                                self.db_directivo.add_data(matricula_directivo, nombre_directivo, apellido_directivo, dni_directivo, fecha_nacimiento_persona, genero_persona, email_persona, contraseña_persona, st.session_state['id_direccion'], id_rol, id_titulo)
                                st.success('Directivo Guardado')
                        else:
                            st.error('Falta una direccion')
                    else:
                        st.error('Faltan Datos')



objeto_componentes = ComponentesDirectivo()

objeto_componentes.diplay_data_components()
objeto_componentes.add_data_components()