-- SELECT J.x_imp, J.y_imp, (J.x_imp + J.y_imp)
-- FROM (
-- 	SELECT sum(X."IMPORTE") as x_imp, sum(Y."IMPORTE") as y_imp
-- 	FROM 
-- 	public.tb_sedapal_chinojosa AS X
-- 	FULL JOIN public.tb_sedapal_chinojosa_2 AS Y
-- 	on X."NIS" = Y."NIS"
-- 	where X."TR" not in ('TR130', 'TR090', 'TR148')
-- ) AS J

select SUM(X."IMPORTE"), SUM(Y."IMPORTE"), SUM(X."IMPORTE") + SUM(Y."IMPORTE") from
select COUNT(*) from
(SELECT *  FROM 
	public.tb_sedapal_chinojosa
	where "TR" not in ('TR130', 'TR090', 'TR148')
) as X union
(SELECT *  FROM 
	public.tb_sedapal_chinojosa_2
 	WHERE "REPORTE" = 'RE15'
) as Y
on X."NIS" = Y."NIS"


-- select * from 
-- (
-- 	(SELECT "IMPORTE" from public.tb_sedapal_chinojosa where "TR" not in ('TR130', 'TR090', 'TR148')) as T1
-- 	(SELECT "IMPORTE" from public.tb_sedapal_chinojosa_2 WHERE "REPORTE" = 'RE15') as T2
-- )
-- 1879811 + 108069

SELECT * FROM public.tb_sedapal_chinojosa WHERE "TR" not in ('TR130', 'TR090', 'TR148') limit 5

COPY
(
--SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE", "F_LECT", "F_EMISO", "F_VCTO"
SELECT*
  FROM (
    (SELECT "F_LECT", "F_EMISO", "F_VCTO", cast(null as int) AS "F_CORTE","OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE", "S_NIS", "TR", "ER", "EC", "DOMICILIO", "NUM_FACT", "SIMBOLO_VA", null AS "TIPO_DEUDA", null AS "RECIBOS"FROM public.tb_sedapal_chinojosa WHERE "TR" not in ('TR130', 'TR090', 'TR148'))
    UNION ALL
    (SELECT cast(null as int) AS "F_LECT", cast(null as int) AS "F_EMISO", cast(null as int) AS "F_VCTO", "F_CORTE", "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE", null AS "S_NIS", null AS "TR", null AS "ER", null AS "EC", null AS "DOMICILIO", null AS "NUM_FACT", null AS "SIMBOLO_VA", "TIPO_DEUDA", "RECIBOS" FROM public.tb_sedapal_chinojosa_2 WHERE "REPORTE" = 'RE15')
   ) c
   WHERE c."OFICINA" = 5111 --and c."TARIFA" in ('T03', 'T04', 'T05')
)
TO 'E:\SupportGIS\CHINOJOSA\data_con_5111.txt' DELIMITER '|' CSV HEADER;


select* FROM public.tb_sedapal_chinojosa_2 WHERE "REPORTE" = 'RE15'
SELECT * FROM public.tb_sedapal_chinojosa limit 5

select* FROM public.tb_sedapal_chinojosa_2 limit 5

-- 213,734,776 con
-- 214,697,833 sin

-- 88,836,430
-- 125,861,403

select sum(R."IMPORTE") from (
	SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE"
  FROM (
    (SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" FROM public.tb_sedapal_chinojosa WHERE "TR" not in ('TR130', 'TR090', 'TR148'))
    UNION ALL
    (SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" FROM public.tb_sedapal_chinojosa_2 WHERE "REPORTE" = 'RE15')
   ) c
   WHERE c."OFICINA" <> 5111
) as R where R."TARIFA" in ('T03', 'T04', 'T05')



SELECT sum(c."IMPORTE")
  FROM (
    (SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" FROM public.tb_sedapal_chinojosa WHERE "TR" not in ('TR130', 'TR090', 'TR148'))
    UNION ALL
    (SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" FROM public.tb_sedapal_chinojosa_2 WHERE "REPORTE" = 'RE15')
   ) c
   WHERE c."OFICINA" <> 5111 and c."TARIFA" in ('T03', 'T03   ', 'T04', 'T04   ', 'T05', 'T05   ')





SELECT SUM(TX_1.T1_IMPORTE), SUM(TX_1.T2_IMPORTE), SUM(TX_1.T1_IMPORTE) + SUM(TX_1.T2_IMPORTE) FROM 
(
	SELECT TB_1."F_EMISO", TB_1."F_VCTO", TB_1."OFICINA", TB_1."NIS", TB_1."NOMBRE_CLIENTE", TB_1."TARIFA", TB_1."IMPORTE" AS T1_IMPORTE,
		   TB_2."OFICINA", TB_2."NIS", TB_2."NOMBRE_CLIENTE", TB_2."TARIFA", TB_2."IMPORTE" AS T2_IMPORTE
	SELECT SUM(TB_1."IMPORTE") AS T1_IMPORTE, SUM(TB_2."IMPORTE") AS T2_IMPORTE, SUM(TB_1."IMPORTE") + SUM(TB_2."IMPORTE")
	FROM 
	(
		SELECT "F_LECT", "F_EMISO", "F_VCTO", "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" 
		FROM public.tb_sedapal_chinojosa 
		WHERE "TR" not in ('TR130', 'TR090', 'TR148') AND "OFICINA" = 5111 and "TARIFA" in ('T03', 'T03   ', 'T04', 'T04   ', 'T05', 'T05   ')
	) AS TB_1
	FULL JOIN (
		SELECT "OFICINA", "NIS", "NOMBRE_CLIENTE", "TARIFA", "IMPORTE" 
		FROM public.tb_sedapal_chinojosa_2 
		WHERE "REPORTE" = 'RE15' AND "OFICINA" = 5111 AND "TARIFA" in ('T03', 'T03   ', 'T04', 'T04   ', 'T05', 'T05   ')
	) AS TB_2
	ON TB_1."NIS" = TB_2."NIS"
) AS TX_1


--  76,637,852
--  26,240,860
-- 102,878,713

