select a.periodo, b.sucursal, sum(monto_credito) as desem
	from public.desembolsos a
	inner join public.sucursales b
	on a.sucursal_id = b.sucursal_id
	group by b.sucursal, a.periodo
	order by desem desc;