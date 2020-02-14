create table public.Sucursales(
	SUCURSAL_ID INT,
	SUCURSAL CHAR(50),
	REGION CHAR(50)
);

COPY public.Sucursales from 'E:\SupportGIS\JLOPEZ\Sucursales.csv' with csv header;