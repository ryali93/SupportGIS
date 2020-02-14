select distinct(a.analista_credito)
	from public.desembolsos a
	inner join public.sucursales b
	on a.sucursal_id = b.sucursal_id
    where a.tasa_interes > 12 
	and b.region IN ('LAMBAYEQUE', 'TUMBES', 'CAJAMARCA', 'PIURA', 'LA LIBERTAD')
