install.packages("raster")
library(raster)
library(ggplot2)

dem = raster("E:/2018/BRENDA/parametros/dem.tif")
ends = shapefile("E:/2018/BRENDA/parametros/GPT_RedHidrica_Ends.shp")
cuenca = shapefile("E:/2018/BRENDA/parametros/GPO_Cuenca.shp")
LongRio = 148618.05069

endPoints = extract(dem, ends)
AltMaxRio = max(endPoints, na.rm=T)
AltMinRio = 0

crs = "+proj=utm +zone=17 +south +datum=WGS84 +units=m +no_defs"
demUTM = projectRaster(dem, crs = crs)

alt_media_8 = function(dem){
  meanDem = mean(getValues(dem), na.rm=TRUE)
  return(meanDem)
}

pend_media_rio_12 = function(dem){
  lc = (AltMaxRio+AltMinRio)/(LongRio)
  return(lc)
}

pend_media_cuenca_13 = function(dem){
  slope = terrain(dem, opt = "slope", unit = "degrees") #degrees, radians, tangent
  slopeVal = mean(getValues(slope), na.rm = T)
  return(slopeVal)
}

# dec_equiv_const_14 = function(dem){
#   Tm = 
#   slopeVal = mean(getValues(slope), na.rm = T)
#   return(slopeVal)
# }

curva_hipsom_9 = function(demUTM){
  intervalo = 100
  hipsom = function(dem,intervalo){
    menor = min(getValues(dem),na.rm = T)
    mayor = max(getValues(dem),na.rm = T)
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
    return(df)
  }
  df = hipsom(demUTM, intervalo)
  p2 <- ggplot(df, aes(y = cota))
  p2 <- p2 + geom_line(aes(x = area, colour = "red"))
  p2 <- p2 + scale_x_continuous(name = "Area (Km2)") + theme(plot.background = element_rect(fill = "transparent"))
  print(df)
  return(p2)
}

coef_masiv_17 = function(dem, cuenca){
  hm = mean(getValues(dem), na.rm=TRUE)
  A = cuenca$AREA
  cm = hm/A
  return(cm)
}


q8 = alt_media_8(dem)
q9 = curva_hipsom_9(demUTM)
q12 = pend_media_rio_12(dem)
q13 = pend_media_cuenca_13(dem)
q17 = coef_masiv_17(dem, cuenca)
# perfil_long_15(dem) --> grafico ya está