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
            dir.fk_calle,
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