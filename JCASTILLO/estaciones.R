rm(list=ls())

library(dplyr)
library(ggplot2)

df = as.data.frame(read.csv("E:/2019/DELCASTILLO/2016-wavelet_tmp2.csv", sep = ";", stringsAsFactors=FALSE))
df$fecha = as.POSIXct(paste(df$dia, df$hora), format="%d/%m/%Y %H:%M")
plot(df$fecha, df$hum, "l")

df = df %>% mutate(fecha = as.Date(fecha, format="%d/%m/%Y %H:%M"))
df = df %>% mutate(hum = as.numeric(hum))
df = df %>% mutate(pp = as.numeric(pp))

ggplot(head(df, 40), aes(x=fecha,y=hum)) +
  geom_line() +
  scale_x_date()
head(df)
