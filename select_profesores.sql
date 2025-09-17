select 
    pe.id_provincia, 
    pe.nombre_provincia, 
    p.nombre_pais 
from provincia_estado pe
join pais p on pe.fk_pais = p.id_pais
where p.id_pais = 2