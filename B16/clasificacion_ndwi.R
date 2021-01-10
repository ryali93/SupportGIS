library(rgee)
library(mapview)
library(sf)
library(mapedit)
library(raster)
library(tidyverse)
library(rasterVis)

ee_Initialize(drive = T)

area <- editMap()
area_sf <- area
area_ee <- sf_as_ee(area_sf)

get_ndwi <- function(year_in, month_in){
  dataset = ee$ImageCollection('LANDSAT/LT05/C01/T1_8DAY_NDWI')$
    filterDate(sprintf('%s-01-01', year_in), sprintf('%s-12-31', year_in))$
    filter(ee$Filter$calendarRange(month_in, month_in, "month"))$
    median()
  colorized = dataset$select('NDWI')$clip(area_ee)
  
  ndwi_drive = ee_as_raster(colorized, 
                            region=area_ee$geometry(), 
                            via = "drive",
                            scale = 30)
  return(ndwi_drive)
}


classify_ndwi <- function(imagen, year_in, month_in){
  # year_in = 2010
  # month_in = 2
  # ndwi_month <- ndwi_2010_2[[1]]
  ndwi_month <- imagen[[1]]
  ndwi_month[ndwi_month <= 0] = 0
  ndwi_month[ndwi_month > 0 & ndwi_month <= 0.1] = 10
  ndwi_month[ndwi_month > 0.1 & ndwi_month <= 0.2] = 20
  ndwi_month[ndwi_month > 0.2 & ndwi_month <= 0.4] = 30
  ndwi_month[ndwi_month > 0.4 & ndwi_month <= 0.6] = 40
  ndwi_month[ndwi_month > 0.6 & ndwi_month <= 1] = 50
  
  ndwi_sf = rasterToPolygons(ndwi_month, dissolve = T) %>% 
    st_as_sf()
  
  ndwi = ndwi_sf %>%
    st_drop_geometry() %>%
    mutate(area = st_area(ndwi_sf),
           area_ha = area/10000,
           year = year_in,
           month = month_in)
  
  return(ndwi)
}

ndwi_2005_3 <- get_ndwi(2005, 3)
ndwi_2006_3 <- get_ndwi(2006, 3)
ndwi_2008_3 <- get_ndwi(2008, 3)
ndwi_2010_2 <- get_ndwi(2010, 2)

ndwi_2005_3_c <- classify_ndwi(ndwi_2005_3, 2005, 3)
ndwi_2006_3_c <- classify_ndwi(ndwi_2006_3, 2006, 3)
ndwi_2008_3_c <- classify_ndwi(ndwi_2008_3, 2008, 3)
ndwi_2010_2_c <- classify_ndwi(ndwi_2010_2, 2010, 2)

# Crear graficos
st_ndwi <- stack(ndwi_2005_3, ndwi_2006_3, ndwi_2008_3, ndwi_2010_2)
names(st_ndwi) <- c("2005_3","2006_3", "2008_3","2010_2")
rasterVis::levelplot(st_ndwi)

ndwi_df <- rbind(ndwi_2005_3_c,
                 ndwi_2006_3_c,
                 ndwi_2010_2_c,
                 ndwi_2008_3_c)

ndwi_df <- ndwi_df %>%
  mutate(mes_anno = as.Date(sprintf("%s-%s-01", year, month)),
         area_ha = as.vector(area_ha))

ggplot(ndwi_df, aes(y = area_ha, x=mes_anno, color=NDWI))+
  geom_point()

class(ndwi_df$area_ha)
as.vector(ndwi_df$area_ha)

write.csv(ndwi_df, "E:/SupportGIS/B16/ndwi.csv")
