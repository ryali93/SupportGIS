CREATE TABLE public.tb_sedapal_chinojosa
(
    "OFICINA" integer,
    "NIS" integer,
    "S_NIS" integer,
    "F_LECT" integer,
    "S_REC" integer,
    "TARIFA" double precision,
    "TR" character varying COLLATE pg_catalog."default",
    "ER" character varying COLLATE pg_catalog."default",
    "F_EMISO" integer,
    "F_VCTO" integer,
    "EC" character varying COLLATE pg_catalog."default",
    "NOMBRE_CLIENTE" character varying COLLATE pg_catalog."default",
    "DOMICILIO" character varying COLLATE pg_catalog."default",
    "DISTRITO" character varying COLLATE pg_catalog."default",
    "NUM_FACT" integer,
    "IMPORTE" double precision,
    "SIMBOLO_VA" character varying COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.tb_sedapal_chinojosa
    OWNER to postgres;