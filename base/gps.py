from math import radians, cos, sin, asin, sqrt 
def distance(lat1, lat2, lon1, lon2): 
      
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 
       
    # Haversine formula  
    dlon = lon2 - lon1  
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  
    c = 2 * asin(sqrt(a))  
     
    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371
       
    # calculate the result 

    return(c * r*1000)
      
      
# driver code  
# lat1 = 35.536917
# lat2 = 35.536907
# lon1 = 51.197899
# lon2 =  51.197899
# print(distance(lat1, lat2, lon1, lon2)*1000, "K.M")


distance(31.497324,31.497080,50.812733,50.812592)
