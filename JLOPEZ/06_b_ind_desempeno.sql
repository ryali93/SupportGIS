select * from 
(select a.periodo as per_lima, avg(a.monto_credito) as desemb_lima, avg(a.tasa_interes) as tasa_lima
	from public.desembolsos a
	inner join public.sucursales b
    on a.sucursal_id = b.sucursal_id
	where b.region = 'LIMA' and a.monto_credito > 10000 and a.tasa_interes > 9
	group by a.periodo) x
full join 
(select a.periodo as per_prov, avg(a.monto_credito) as desemb_prov, avg(a.tasa_interes) as tasa_prov
	from public.desembolsos a
	inner join public.sucursales b
    on a.sucursal_id = b.sucursal_id
	where b.region <> 'LIMA' and a.monto_credito > 10000 and a.tasa_interes > 9
	group by a.periodo) y
	on x.per_lima = y.per_prov
