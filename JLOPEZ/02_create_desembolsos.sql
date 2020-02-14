create table public.Desembolsos(
	PERIODO INT,
	CREDITO_ID CHAR(50),
	SUCURSAL_ID INT,
	NOMBRE_CLIENTE CHAR(100),
	CLIENTE_ID INT,
	ANALISTA_CREDITO CHAR(100),
	MONTO_CREDITO NUMERIC,
	TASA_INTERES CHAR(20)
);

COPY public.Desembolsos from 'E:\SupportGIS\JLOPEZ\Base_Clientes.csv' with csv header;
