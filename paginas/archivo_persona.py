import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import date
from random import random
import random
import time

if "cadena_direccion" not in st.session_state:
    st.session_state["cadena_direccion"] = None

if "id_direccion" not in st.session_state:
    st.session_state["id_direccion"] = 0



load_dotenv()


from ubicaciones.archivo_pais import Pais
from ubicaciones.archivo_provincia_estado import ProvinciaEstado
from ubicaciones.archivo_ciudad import Ciudad
from ubicaciones.archivo_calle import Calle
from pages.archivo_direccion import Direccion
from pages.archivo_rol import Rol
from pages.archivo_titulo_secundario import TituloSecundario

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
            ca.nombre_calle,
            dir.numero_direccion,
            dir.departamento,
            ci.nombre_ciudad,
            prov.nombre_provincia,
            p.nombre_pais
        
        from persona per
        join direccion dir on per.fk_direccion = dir.id_direccion
        join calle ca on  dir.fk_calle = ca.id_calle
        join ciudad_municipio ci on ca.fk_ciudad = ci.id_ciudad
        join provincia_estado prov on ci.fk_provincia = prov.id_provincia
        join pais p on prov.fk_pais = p.id_pais;
        """
        self.cursor.execute(script_consulta)
        result = self.cursor.fetchall()
        return result
    

    def add_data(self, matricula_persona, nombre_persona,apellido_persona, dni_persona, fecha_nac_persona, genero_persona, email_persona, contrasenia_persona, fk_direccion):
        script_into_persona = """
        insert into persona(
            matricula_persona,
            nombre_persona,
            apellido_persona,
            dni_persona,
            fecha_nac_persona,
            genero_persona,
            email_persona,
            contraseña_persona,
            fk_direccion
        ) values 
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
        );
        """

        self.cursor.execute(script_into_persona, (matricula_persona, nombre_persona, apellido_persona, dni_persona, fecha_nac_persona, genero_persona, email_persona, contrasenia_persona,fk_direccion))

        # script_into_persona_rol = """
        # INSERT INTO persona_has_rol (
        #     fk_matricula_persona,
        #     fk_rol)
        # VALUES
        #     (%s, %s);
        # """
        # self.cursor.execute(script_into_persona_rol, (matricula_persona, fk_rol))
        self.connection.commit()
        st.success('Persona agregada con exito')



class ComponentesPersona:
    def __init__(self):
        self.db_persona = Persona()
        self.db_pais = Pais()
        self.db_provincia = ProvinciaEstado()
        self.db_ciudad = Ciudad()
        self.db_calle = Calle()
        self.db_direccion = Direccion()
        self.db_titulo = TituloSecundario()
        self.db_rol = Rol()

    def mostrar_datos_persona(self):

        data_persona = self.db_persona.fetch_data()
        df_persona = pd.DataFrame(data_persona)

        
        _contenedor_tabla_persona = st.container(border = True)
        with _contenedor_tabla_persona:
            filtro = st.text_input('Ingrese un nombre para filtrar: ')  
            if filtro:
                df_persona = df_persona[df_persona["nombre_persona"].str.contains(filtro, case=False, na=False)]   
            
            st.write("### Info personas")
            dic_persona_seleccionada = st.dataframe(df_persona,
                                            height = 500,
                                            width = 750,
                                                selection_mode= 'single-row',
                                                on_select='rerun'
                                                )
        return df_persona, dic_persona_seleccionada 
    

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

        nombre_calle = st.text_input('Nombre de la calle', value=calle_seleccionada, disabled = False)
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
        


    def agregar_datos_persona(self):
        _container_formulario_persona = st.container(border = True)
        with _container_formulario_persona:
            st.write('#### Ingresar Datos Persona')

            _columna_nombre, _columna_apellido = st.columns([2,2])
            with _columna_nombre:
                nombre_persona = st.text_input("Ingrese nombre: ", max_chars = 45)
            with _columna_apellido:
                apellido_persona = st.text_input("Ingrese apellido: ", max_chars = 45)

            _columna_dni, _columna_fecha_nac, _columna_genero = st.columns([2,3,4])
            with _columna_dni:
                dni_persona = st.number_input('Ingrese DNI: ', step=100, min_value=0, max_value=99999999) 
            with _columna_fecha_nac:
                fec_nac_persona = st.date_input('Fecha de nacimiento ', format= "DD/MM/YYYY",min_value= date(1950,1,1)) 
            with _columna_genero:
                lista_genero = ['M','F','O']
                genero_persona = st.selectbox("Genero", lista_genero)

            email_persona = st.text_input('Ingrese su email: ')

            _columna_contrasenia, _columna_confirmar_contra = st.columns([2,2])

            with _columna_contrasenia:
                contrasenia_persona = st.text_input('Ingrese su contraseña', type='password')
            with _columna_confirmar_contra:
                confirmar_contrasenia = st.text_input('Confirme su contraseña', type='password')

            if contrasenia_persona and confirmar_contrasenia:
                if contrasenia_persona == confirmar_contrasenia:
                    st.success('Su contraseña son iguales')
                else:
                    st.error('Las contrasenias no coinciden')

            _columna_pais, _columna_provincia = st.columns([2,2])

            with _columna_pais:
                lista_diccionario_pais = self.db_pais.fetch_data()
                diccionario_pais = {diccionario['nombre_pais']: diccionario['id_pais'] for diccionario in lista_diccionario_pais}
                

                lista_paises = list(diccionario_pais.keys())

                pais_persona = st.selectbox("País de Residencia: ", lista_paises)

                id_pais = diccionario_pais[pais_persona]


            with _columna_provincia:
                lista_provincias = self.db_provincia.fetch_data_fitro_pais(id_pais)
                diccionario_prov = {diccionario['nombre_provincia']:diccionario['id_provincia'] for diccionario in lista_provincias}
                lista_provincias = list(diccionario_prov.keys())
                provincia_persona = st.selectbox("Provincia/Estado: ", lista_provincias)
                id_provincia_buscada = diccionario_prov[provincia_persona] if provincia_persona !=None else None

            _columna_ciudad, _columna_calle = st.columns([2,2]) 

            with _columna_ciudad:
                lista_diccionario_ciudades = self.db_ciudad.fetch_data_filtro_provincia(id_provincia_buscada)
                diccionario_ciudades = {diccionario['nombre_ciudad']:diccionario['id_ciudad'] for diccionario in lista_diccionario_ciudades}
                lista_ciudades = list(diccionario_ciudades.keys())
                ciudad_seleccionada = st.selectbox('Ciudad ', lista_ciudades)

                id_ciudad = diccionario_ciudades[ciudad_seleccionada] if ciudad_seleccionada !=None else None

            with _columna_calle:
                lista_diccionario_calle = self.db_calle.fetch_data_por_ciudad(id_ciudad)
                diccionario_calles = {diccionario['nombre_calle']:diccionario['id_calle'] for diccionario in lista_diccionario_calle}
                lista_calles = list(diccionario_calles.keys())
                calle_seleccionada = st.selectbox('Calle: ',  lista_calles)

                id_calle = diccionario_calles[calle_seleccionada] if ciudad_seleccionada !=None else None

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

            # _columna_titulos, _columna_rol = st.columns([2,8])

            # with _columna_titulos:
            #     lista_titulos = self.db_titulo.fetch_data()
            #     diccionario_titulos = {diccionario['nombre_titulo_secundario']:diccionario['id_titulo_secundario'] for diccionario in lista_titulos}
            #     lista_titulos = list(diccionario_titulos.keys())
            #     titulo_seleccionado = st.selectbox('Título Superior: ', lista_titulos)
            #     id_titulo = diccionario_titulos[titulo_seleccionado] 

            # with _columna_rol:
            #     lista_roles = Rol().fetch_data()
            #     diccionario_roles = {diccionario['nombre_rol']:diccionario['id_rol']for diccionario in lista_roles}
            #     lista_roles = list(diccionario_roles.keys())
            #     rol_seleccionado = st.selectbox('Rol: ', lista_roles)
            #     id_rol = diccionario_roles[rol_seleccionado]


            _columna_relleno2,_columna_guardar_datos = st.columns([5,3])

            with _columna_guardar_datos:
                if st.button('Guardar Persona', use_container_width= True):
                    matricula_persona = random.randint(10000000, 99999999)
                    if nombre_persona and apellido_persona and dni_persona and fec_nac_persona and genero_persona and email_persona:
                            if contrasenia_persona and contrasenia_persona == confirmar_contrasenia:
                                self.db_persona.add_data(matricula_persona,nombre_persona, apellido_persona, dni_persona, fec_nac_persona, genero_persona, email_persona, contrasenia_persona,st.session_state['id_direccion'])
                                st.success('Persona Guardado')
                            elif contrasenia_persona and contrasenia_persona != confirmar_contrasenia:
                                st.error('La contraseñas no coinciden')
                            elif contrasenia_persona == None and confirmar_contrasenia == None:
                                self.db_persona.add_data(matricula_persona, nombre_persona, apellido_persona, dni_persona, fec_nac_persona, genero_persona, email_persona, contrasenia_persona,st.session_state['id_direccion'])
                                st.success('Persona Guardado')
                            else:
                                st.error('Falta una direccion')
                    else:
                        st.error('Faltan Datos')


componentes_persona = ComponentesPersona()
componentes_persona.mostrar_datos_persona()
componentes_persona.agregar_datos_persona()
