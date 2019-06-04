# Package: AreaVol
# Version: 1.0
# Date: 2017-05-01
# Title: Area Volumen - Presas
# Author: Yali Samaniego Roy <ryali93@gmail.com> with contributions from Juan C. Rodriguez Mendoza.
# Maintainer: Yali Samaniego Roy <ryali93@gmail.com>
# Depends: R (>= 3.2.0), sp (>= 0.9-0)
# Description: Grafica las curvas área volumen.

install.packages("sp",dependencies = T)             # Correr una sóla vez
install.packages("rgdal",dependencies = T)          # Correr una sóla vez
install.packages("raster",dependencies = T)         # Correr una sóla vez
install.packages("grid",dependencies = T)           # Correr una sóla vez
install.packages("ggplot2",dependencies = T)        # Correr una sóla vez
library(raster)
library(ggplot2)
library(grid)

Avol = function(dem,intervalo){
  menor = min(getValues(dem),na.rm = T)
  mayor = max(getValues(dem),na.rm = T)
  intervalo = 2
  area = c()
  cota = c()
  a = seq(from = menor,to = mayor,by = intervalo)
  for(i in 1:(length(a)-1)){
    dem[dem <= a[i+1]] = (a[i]+a[i+1])/2
    val = (a[i]+a[i+1])/2
    x = length(dem[dem == val])*res(dem)[1]*res(dem)[2]
    cota = c(cota,val)
    area = c(area,x)
  }
  df = data.frame(cota,area)
  for(i in (length(df$area)):2){
    df$area[i] = (df$area[i]+df$area[i-1])/2
    df$Vol[i] = df$area[i]*intervalo
  }
  df$Vol[1] = 0
  df$VolAc[1] = df$Vol[1]
  for(i in 2:(length(df$area))){
    df$VolAc[i] = df$Vol[i]+df$VolAc[i-1]
  }
  return(df)
}                 # Correr una sóla vez
dem = raster("E:/Scripts_Roy/Avol/Dem.tif")         # Cambiar la ruta por un tif del área colectora de la presa
# intervalo = 2
df = Avol(dem, intervalo)                           # Intervalo es cada cuántos metros se quiere visualizar(2 metros está bien para presas pequeñas)
write.table(df,"E:/Scripts_Roy/Avol/tabla.xls")     # Cambiar la ruta dónde se guardará el excel


## Prueba plot
p1 <- ggplot(df, aes(y = cota))
p1 <- p1 + geom_line(aes(x = VolAc, colour = "blue"))
p1 <- p1 + scale_x_continuous(name = "Volumen") + theme(plot.background = element_rect(fill = "transparent")) + theme(panel.background = element_rect(fill = "transparent", colour = NA), plot.background = element_rect(fill = "transparent", colour = NA))
p2 <- ggplot(df, aes(y = cota))
p2 <- p2 + geom_line(aes(x = area, colour = "red"))
p2 <- p2 + scale_x_continuous(name = "Area",trans = "reverse",position = "top") + theme(plot.background = element_rect(fill = "transparent"))
