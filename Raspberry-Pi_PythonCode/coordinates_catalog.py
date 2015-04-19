#-------------------------------------------------------------#
#Coordinates insertion and transformation for Aq'anoq Observatory
#SpaceApps Challenge 2015, Guatemala Edition.
#-------------------------------------------------------------#

finalData = [] #finalData is a variable used to deliver coordinates from readTxt function into the main program
backupString = [] #backupString is used for conversions in some function
import math
import ephem
import time

#--------------------------------------------------------------------------------------------------#
#radian: it is a function used to convert a given right ascention coordinate in hours and converts it to radians

def radian(hourTemp): #hourTemp is the variable to convert
    radianOut = 15*math.pi*hourTemp/180
    return radianOut


#--------------------------------------------------------------------------------------------------#
#coorSubstract: steps difference, this function creates a vector that points in the direction movement of the telescope, it is used if the software accepts vectors instead of coordinates

def coorSubstract(ascF,ascI,decF,decI,sign): #ascF is the final right ascention, ascI is the current right ascention, decF is the final declination, decI is the current declination and sign is the sign of the declination
    if sign == "+": #movimiento en sentido positivo, positive movement
        finalStep = [(ascF-ascI),(decF-decI)]
    elif sign == "-": #movimiento en sentido negativo, negative movement
        finalStep = [(ascF-ascI),(decF-decI)]
    if finalStep[0] <= 0: #insertar signo, insert sign
        finalStep.append("-")
        finalStep[0] = finalStep[0]*-1
    else:
        finalStep.append("+") #insertar signo, insert sign
    if finalStep[1] <= 0:
        finalStep.append("-")
        finalStep[1] = finalStep[1]*-1
    else:
        finalStep.append("+")
    return finalStep
    

#--------------------------------------------------------------------------------------------------#
#fillZeros: Zero filling on the final string, this routine makes all numbers to have the same digits, 
#filling with zeroes to the left until the digits are needed.

def fillZeros(number,length): #number is the number to convert, length is the number of digits of the final number
    counter = len(str(number)) #gets the length of the number
    x = 0
    backupString = ""
    while x < (length - counter): #fills with all zeroes neded
        backupString = backupString + "0"
        x = x+1
    backupString = backupString + str(number)
    return backupString
    
    
#--------------------------------------------------------------------------------------------------#
#rectaConver: this function converts right ascention into degrees or hours
def rectaConver(hora,minut,segundos,selec): #selec = 1 pasa a grados, selec = 2 pasa a horas, 1 converts to degrees, 2 converts to hours
    minutTemp = float(minut) + float(segundos)/60
    horaTemp = float(hora) + float(minutTemp)/60
    if selec == 1:
        degFinal = float(horaTemp)*15
    elif selec == 2:
        degFinal = float(horaTemp)
    return degFinal
    
    
#--------------------------------------------------------------------------------------------------#
#sidereal: sidereal function returns the sidereal time for the given latitude and longitude, change the constant values to your location 

def sidereal():
    currentTime = time.strftime("%Y/%m/%d") + ' ' + time.strftime("%H:%M:%S") 
    test = ephem.Observer()
    test.lon = '+90:32:48' #longitude for Guatemala City
    test.lat = '+14:36:48' #latitude for Guatemala City
    test.elevation = 1690 #elevation for Guatemala City
    test.date = currentTime #gets time from the PC
    var = test.sidereal_time()
    cad = var.__str__()
    if cad[1] == ":":
        cad = "0" + cad
    hora = int(cad[0] + cad[1])-6
    if hora < 0:
        hora = 24 + hora
    minute = int(cad[3]+cad[4])
    second = int(cad[6]+cad[7])
    finalTime = str(hora) + ":" + str(minute) + ":" + str(second)
    if finalTime[1] == ":":
        finalTime = "0" + finalTime
    if finalTime[4] == ":":
        finalTime = finalTime[:3] + "0" + finalTime[3:]
    if len(finalTime) != 8:
        finalTime = finalTime[:6] + "0" + finalTime[6:]
    #print finalTime
    return finalTime
    
#--------------------------------------------------------------------------------------------------#
# decliConver: converts declination in deg,min,seg into degrees.

def decliConver(deg,minutes,second):
    minutesTemp = float(minutes) + float(second)/60
    degFinal = float(deg) + float(minutesTemp)/60
    return degFinal

#--------------------------------------------------------------------------------------------------#
# pasos: converts to steps for a stepper motor, if required, option 3 is for DC motors
def pasos(grados,motor): #1 es ascensiÃ³n recta, 2 es declinaciÃ³n, 3 es el DC con encoder
    if motor == 1:
        finalSteps = grados*96/0.8
    elif motor == 2:
        finalSteps = grados*20/0.8
    elif motor == 3:
        finalSteps = grados*2000
    finalSteps = int(finalSteps)
    return finalSteps
  

#--------------------------------------------------------------------------------------------------#
#horizontal: converting equatorial to horizontal coordinates, have faith on this one

def horizontal(latitude,rightAsc,dec,decSign): #latitude is the region's latitude, rightAsc is the right Ascention from the catalog minus the sidereal time, dec is declination and decSign is the sign of the declination
    if decSign == "-":
        dec = dec*-1
    param1 = math.sin(dec)*math.sin(latitude)+math.cos(dec)*math.cos(latitude)*math.cos(rightAsc)
    altitude = math.asin(param1)
    param2 = (math.sin(dec)-math.sin(latitude)*math.sin(altitude))/(math.cos(latitude)*math.cos(altitude))
    azimut = math.acos(param2)
    #param2 = -1*math.sin(rightAsc)*math.cos(dec)/math.cos(altitude)
    #azimut = math.asin(param2)
    altitudeDeg = altitude*180/math.pi
    #print decSign
    if rightAsc <= 0:
        azimutDeg = azimut*180/math.pi
    elif rightAsc > 0:
        azimutDeg = 360 - azimut*180/math.pi
    #print azimutDeg
    coordinates = [altitudeDeg,azimutDeg]
    #print coordinates
    return coordinates
    
#--------------------------------------------------------------------------------------------------#
# readTxt: acquires coordinates from planets, moon or sun.

def readTxt(nameStar):
    '''fileRead=open('Lista Estrellas.txt','r') #opens the database file
    lineRead = fileRead.readline() #reads lines
    ban = 0
    while lineRead !="": #this method looks for the star in the catalog, if it finds it, returns its equatorial coordinates, if don't, checks for planets
            lineRead = lineRead.rstrip("\n")
            #print lineRead
            dataTemp = lineRead.split(',')
            #print dataTemp
            if nameStar.lower() == dataTemp[0].lower():
                ban = 1
                for x in range(1,8):
                    finalData.append(dataTemp[x])
                lineRead = ""
            else:
                lineRead = fileRead.readline()
            
    fileRead.close()'''
    
    #looks for planets, sun or moon
    if nameStar.lower() == "marte":
        planet = ephem.Mars()
        ban = 2
    elif nameStar.lower() == "mercurio":
        planet = ephem.Mercury()
        ban = 2
    elif nameStar.lower() == "venus":
        planet = ephem.Venus()
        ban = 2
    elif nameStar.lower() == "jupiter":
        planet = ephem.Jupiter()
        ban = 2
    elif nameStar.lower() == "saturno":
        planet = ephem.Saturn()
        ban = 2
    elif nameStar.lower() == "urano":
        planet = ephem.Uranus()
        ban = 2
    elif nameStar.lower() == "neptuno":
        planet = ephem.Neptune()
        ban = 2
    elif nameStar.lower() == "luna":
        planet = ephem.Moon()
        ban = 2
    elif nameStar.lower() == "sol":
        planet = ephem.Sun()
        ban = 2
    else:
        try:
            planet = ephem.star(nameStar.title())
            ban = 2
        except:
            ban = 0
    if ban == 2: #fills with data from the desired planet, sun or moon
        planet.compute()
        #print planet.ra, planet.dec
        if planet.dec > 0:
            finalDataTemp = str(planet.ra) + ":" + "+:" + str(planet.dec)
        elif planet.dec < 0:
            decTemp = str(planet.dec).replace("-","")
            finalDataTemp = str(planet.ra) + ":" + "-:" + decTemp
            #print finalDataTemp
        ban = 1
        temporal = finalDataTemp.split(":")
        for x in range(0,7):
            finalData.append(temporal[x])
            
        
        #print finalData
    if ban == 0: #returns nothing if the object is not found
        finalData.append("nada")
    #print finalData
    return finalData
    #starts the program
    #polaris coordinates
    
#--------------------------------------------------------------------------------------------------#
ascHome = pasos(42.625,1)
decHome = pasos(89.328,2)
prevAsc = ascHome
prevDec = decHome
latitude = 14.613333*math.pi/180
while True: #program cycle
    nombreEstrella = raw_input("Ingrese el nombre de la estrella a ubicar\n") #insert star name
    coorEstrella = readTxt(nombreEstrella) 
    #print coorEstrella
    if coorEstrella[0] == "nada":
        print("No se encuentra dentro de la base de datos") #if the object is not found
    else:
        sideralDate = sidereal() #get sidereal time
        siderHoras = int(sideralDate[0] + sideralDate[1]) #sidereal time hours
        siderMinutos = int(sideralDate[3] + sideralDate[4])#sidereal time minutes
        siderSegundos = int(sideralDate[6] + sideralDate[7])#sidereal time seconds
        tiempoSideral = rectaConver(siderHoras,siderMinutos,siderSegundos,2) #conversion for degrees of sidereal time
        absoluteAscention = rectaConver(coorEstrella[0],coorEstrella[1],coorEstrella[2],2) #converts to degrees the body's right ascention
        horaSideral = tiempoSideral - absoluteAscention #position in the right ascention axis of the body
        radianSideral = radian(horaSideral) #converts to radians
        radianDecli = radian(decliConver(coorEstrella[4],coorEstrella[5],coorEstrella[6])/15) #declination to radians
        #coordenadas horizontales, horizontal coordinates
        horizontales = horizontal(latitude,radianSideral,radianDecli,coorEstrella[3])
        print "Coordenadas horizontales (Alt,Az): \n" + str(horizontales[0]) + "," + str(horizontales[1])
        
        #trama en ecuatoriales, equatorial coordinates
        declination = decliConver(coorEstrella[4],coorEstrella[5],coorEstrella[6])
        rightAscention = rectaConver(coorEstrella[0],coorEstrella[1],coorEstrella[2],2)
        
        print "Coordenadas Ecuatoriales (RA,Dec): \n" + "%.2f" %rightAscention + "," + str(coorEstrella[3])+ "%.2f" %declination
        #steps routine
        currentDec = pasos(decliConver(coorEstrella[4],coorEstrella[5],coorEstrella[6]),2)
        currentAsc = pasos(rectaConver(coorEstrella[0],coorEstrella[1],coorEstrella[2],1),1)
        finalSteps = coorSubstract(currentAsc,prevAsc,currentDec,prevDec,coorEstrella[3])
        #Stream for an equatorial mount with stepper motors
        tramaFinalEcu = "a"+"," "+" + "," + fillZeros(currentAsc,5)+","+"b"+","+str(coorEstrella[3])+","+fillZeros(currentDec,5)
        print "trama si se enviaran los valores al stepper en ecuatorial: \n" + tramaFinalEcu
        #steps final stream
        tramaFinal = "a"+"," + (finalSteps[2]) + "," + fillZeros(finalSteps[0],5)+","+"b"+","+str(finalSteps[3])+","+fillZeros(finalSteps[1],5)
        #gets the current coordinates in order to move again, if the difference is needed
        prevAsc = currentAsc
        prevDec = currentDec
        print "Trama si se envía la diferencia entre la posición actual y la final en montura ecuatorial: \n" + tramaFinal
        #steps for horizontal coordinates
        if horizontales[0] >= 0:
            tramaFinalHor = "+" + str(fillZeros(pasos(horizontales[0],3),6)) + "+" + str(fillZeros(pasos(horizontales[1],3),6)) + "+" + "0000"
            print "Trama si se enviaran los valores al telescopio alt-acimutal: \n" + tramaFinalHor
        else:
            tramaFinalHor = "-" + str(fillZeros(pasos(-1*horizontales[0],3),6)) + "+" + str(fillZeros(pasos(horizontales[1],3),6)) + "+" + "0000"
            print "el objetivo esta debajo del horizonte, no puede apuntarse."
            #print "Trama si se enviaran los valores al telescopio alt-acimutal: \n" + tramaFinalHor
    del coorEstrella[:]
