import csv
import sys
import statistics
import codecs
import xlsxwriter
from tkinter.filedialog import askopenfilename

# Nombre de cada uno de los campos
# Checkpoint:Source-Destination-Service
# ArcSight-sourceAddress, destinationAddress,destinationPort
nombreOrigen = ['Source','source','origen','sourceAddress']
nombreDestino = ['Destination','destination','origen','destinationAddress']
nombreServicio = ['Service','Servicio','destinationPort']
nombreTiempo = ['time','Time','Event Time']

def nombreArchivo():
    archivoLog=askopenfilename()
    print("Parseando Archivo...")
    return archivoLog
    # Parsear CSV

def parsearArchivo(archivoLog):
    huntingFile=codecs.open(archivoLog,'r',encoding='utf-8',errors='ignore')
    huntingReader=csv.reader(huntingFile)
    huntingData=list(huntingReader)
    return huntingData

def obtenerTiempo(huntingData):
    global nombreTiempo
    for i in range(len(nombreTiempo)):
        for j in range(len(huntingData[0])):
            if str(nombreTiempo[i]) == str(huntingData[0][j]):
                indiceTiempo = j
    return indiceTiempo

def indiceTiempos(huntingData,indiceTiempo):
    longitud = len(huntingData) - 1
    tiempoInicial = huntingData[2][indiceTiempo]
    tiempoFinal = huntingData[longitud][indiceTiempo]
    return tiempoInicial,tiempoFinal

def obtenerIndices(huntingData):
    # Indice Origen
    indiceOrigen = ''
    for i in range(len(nombreOrigen)):
        for j in range(len(huntingData[0])):
            if str(nombreOrigen[i]) == str(huntingData[0][j]):
                indiceOrigen = j

    # Indice Destino
    for i in range(len(nombreDestino)):
        for j in range(len(huntingData[0])):
            if str(nombreDestino[i]) == str(huntingData[0][j]):
                indiceDestino = j

    # Indice Servicio
    for i in range(len(nombreServicio)):
        for j in range(len(huntingData[0])):
            if str(nombreServicio[i]) == str(huntingData[0][j]):
                indiceServicio = j

    return indiceOrigen,indiceDestino,indiceServicio

def obtenerListas(huntingData,indiceOrigen,indiceDestino):
    print("...obteniendo Listas...")
    # Llenar lista de orígenes y destinos
    listaOrigenesCompleta= [None] * len(huntingData)
    for i in range (len(huntingData)):
        listaOrigenesCompleta[i]=huntingData[i][indiceOrigen]

    listaDestinosCompleta= [None] * len(huntingData)
    for i in range (len(huntingData)):
        listaDestinosCompleta[i]=huntingData[i][indiceDestino]

    # Remover Duplicados Origen
    listaOrigenes = []

    seen = set()
    for value in listaOrigenesCompleta:
        if value not in seen:
            listaOrigenes.append(value)
            seen.add(value)

    #Remover Duplicados Destino
    listaDestinos = []
    seen = set()
    for value in listaDestinosCompleta:
        if value not in seen:
            listaDestinos.append(value)
            seen.add(value)

    return listaOrigenes,listaDestinos

def conversionEnteros(huntingData,indiceServicio):
    huntingData[0][indiceServicio]=''
    for i in range(len(huntingData)):
        if (huntingData[i][indiceServicio]!=''):
            huntingData[i][indiceServicio]=int(huntingData[i][indiceServicio])
        else:
            huntingData[i][indiceServicio]=0
    return huntingData

#Función de progreso
def ProgressBar (value,endvalue,bar_length=50):
    percent=float(value/endvalue)
    arrow='-' * int(round(percent * bar_length)-1)+'>'
    spaces= ' ' * (bar_length - len(arrow))
    sys.stdout.write('\rCompletado : [{0}] {1}%'.format(arrow+spaces,int(round(percent*100))))
    sys.stdout.flush()

#Funcion de duplicados
def Remove_Duplicates(values):
    output=[]
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

#############################################################
#                Hunting Puertos                            #
#############################################################
def PeerHunting(port,opcion,huntingData,indiceServicio,listaOrigenes,indiceOrigen,listaDestinos,indiceDestino):
    listaSMB=[]
    medianArray=[]
    listaPuertosRep=[]
    contador=0
    contador2=0
    contador3=0
    median=0
    listaPeersPuertos=[]

    if (opcion==0):
        print('\r')
        print ('REVISIÓN DE PEERS DE PUERTO '+str(port))
        print ('')
#Hacer una lista para el puerto enviado
    for i in range(len(huntingData)):
        if huntingData[i][indiceServicio]==port:
            listaSMB.append(huntingData[i])
        
#Inicializa Matriz de Resultados
    w,h=len(listaSMB),2
    listaSMB2=[[0 for x in range(h)] for y in range(w)]
    
#Buscar puertos
    print ('...ejecutando algoritmo de puerto ' + str(port))
    print ('')
    for i in range(len(listaOrigenes)):
        for j in range(len(listaDestinos)):
            for k in range(len(listaSMB)):
                if listaOrigenes[i]==listaSMB[k][indiceOrigen] and listaDestinos[j]==listaSMB[k][indiceDestino] and listaSMB[k][indiceServicio]==port:
                    contador+=1
            if (contador!=0):
                contador2+=1
                contador=0
            
        if (contador2!=0):
            listaSMB2[contador3][0]=listaOrigenes[i]
            listaSMB2[contador3][1]=contador2
            contador3 += 1

        ProgressBar(i,len(listaOrigenes))
        contador2=0

#Sacar Media
    for i in range(len(listaSMB2)):
        if (listaSMB2[i][1]!=0):
            medianArray.append(listaSMB2[i][1])

    if (len(medianArray)!=0):
        median=statistics.median(medianArray)
        if (opcion==0):
            print('')
            print('...la media de Peers del puerto '+ str(port) + ' es ' + str(median) + '...')
            print('')
    else:
        if (opcion==0):
            print('')
            print ('NO HAY HALLAZGOS REELEVANTES PARA EL PUERTO '+ str(port) )
            print('')
            
#Ordenar el Arreglo
    listaPA2 = sorted(listaSMB2,key=lambda x: x[1],reverse=True)

# Llena lista global
    for i in range(len(listaPA2)):
        listaPeersPuertos.append(listaPA2[i][0])

#Imprimir
    print('\r')
    if (opcion==0):
        for i in range(len(listaPA2)):
            if (int(listaPA2[i][1])>=int(median)):
                print ('LA IP ' + str(listaPA2[i][0]) + ' TIENE CONEXIÓN A ' + str(listaPA2[i][1]) + ' PEER(S) DIFERENTES POR EL PUERTO '+ str(port))
    print(" ")
	
#Otras conexiones
    for i in range(len(listaPA2)):
        if listaPA2[i][1]>=int(median):
            for j in range (len(huntingData)):
                if listaPA2[i][0]==huntingData[j][indiceOrigen] and huntingData[j][indiceServicio]!=0:
                    listaPuertosRep.append(huntingData[j][indiceServicio])
            listaPuertosAdd=Remove_Duplicates(listaPuertosRep)
            listaPuertosAdd.remove(port)
            if listaPA2[i][0]!=0:
                print ("La dirección IP " + str(listaPA2[i][0]) + " se conecta tambien a los puertos: ")
                print (listaPuertosAdd)
                print ("")

            listaPuertosRep=[]

    return listaPeersPuertos
#############################################################
#                Puertos Altos                              #
#############################################################

def puertosAltos(port, opcion,huntingData,indiceServicio,listaOrigenes,listaDestinos,indiceOrigen,indiceDestino):
    listaPA = []
    medianArray = []
    contador = 0
    contador2 = 0
    contador3 = 0
    listaPeersPuertosAltos=[]
    print('\r')
    if (opcion == 0):
        print('REVISIÓN DE PEERS DE PUERTOS ALTOS A PARTIR DEL ' + str(port))
    huntingData[0][indiceServicio] = ''

    # print ('...haciendo una lista para los puertos enviados...')

    for i in range(len(huntingData)):
        if (huntingData[i][indiceServicio] != ''):
            huntingData[i][indiceServicio] = int(huntingData[i][indiceServicio])
        else:
            huntingData[i][indiceServicio] = 0

    # Hacer lista de puertos altos
    for i in range(len(huntingData)):
        if int(huntingData[i][indiceServicio]) > port:
            listaPA.append(huntingData[i])

    # Inicializa Matriz de Resultados
    w, h = len(listaPA), 2
    listaPA2 = [[0 for x in range(h)] for y in range(w)]

    # Buscar puertos
    #    #print ('...ejecutando algoritmo de puertos...')
    #    #print ('...' + time.asctime() + '...')
    for i in range(len(listaOrigenes)):
        for j in range(len(listaDestinos)):
            for k in range(len(listaPA)):
                if listaOrigenes[i] == listaPA[k][indiceOrigen] and listaDestinos[j] == listaPA[k][indiceDestino] and \
                        listaPA[k][indiceServicio] > port:
                    contador += 1
            if (contador != 0):
                contador2 += 1
                contador = 0

        if (contador2 != 0):
            contador3 += 1
            listaPA2[contador3][0] = listaOrigenes[i]
            listaPA2[contador3][1] = contador2
        ProgressBar(i, len(listaOrigenes))
        contador2 = 0

    # Sacar Mediana
    if len(listaPA2) != 0:
        for i in range(len(listaPA2)):
            if (listaPA2[i][1] != 0):
                medianArray.append(listaPA2[i][1])
        median = statistics.median(medianArray)
        if (opcion == 0):
            print(
                '...La media de Peers de puertos altos a partir del puerto ' + str(port) + ' es ' + str(median) + '...')
            print('')
    else:
        print('')
        print("NO SE ENCONTRARON RESULTADOS DE PUERTOS ALTOS")
        print('')

    # Ordenar el Arreglo
    listaPA2 = sorted(listaPA2, key=lambda x: x[1], reverse=True)

    # Llena lista global
    for i in range(len(listaPA2)):
        listaPeersPuertosAltos.append(listaPA2[i][0])

    # Imprimir
    if (opcion == 0) and len(listaPA2) != 0:
        for i in range(len(listaPA2)):
            if (int(listaPA2[i][1]) > int(median)):
                print('LA IP ' + str(listaPA2[i][0]) + ' TIENE CONEXIÓN A ' + str(
                    listaPA2[i][1]) + ' DIFERENTES PEER(S) EN PUERTOS ALTOS')

    return listaPeersPuertosAltos

#########################################################
#                Listas Negras                          #
#########################################################
def listasNegras(opcion,huntingData,indiceDestino,indiceOrigen,indiceServicio):
    contador = 0
    contador2 = 0
    contador3 = 0

    listaPeersBlacklist=[]
    ip = ''
    w, h = len(huntingData), 3
    listaBL = [[0 for x in range(h)] for y in range(w)]
    global listaPeersGlobBlacklist
    print('...parseando blacklist...')
    print('')
    nameblacklist = askopenfilename()
    blacklist = open(nameblacklist, 'r')
    dataList = blacklist.readlines()
    for i in range(len(dataList)):
        dataList[i] = dataList[i].rstrip()
    print('...Blacklist parseada!...')
    for j in range(len(dataList)):
        for k in range(len(huntingData)):
            if huntingData[k][indiceDestino] == dataList[j]:
                contador += 1
                ip = huntingData[k][indiceOrigen]
                puerto = huntingData[k][indiceServicio]
        if (contador != 0):
            if (opcion == 0):
                listaBL[contador2][0] = ip
                listaBL[contador2][1] = dataList[j]
                listaBL[contador2][2] = puerto
                contador2 += 1
            listaPeersBlacklist.append(str(ip))
            contador = 0
            ip = ''
            puerto = ''
        ProgressBar(j, len(dataList))

    # Imprimir
    print('')
    while True:
        if listaBL[contador3][0] != 0:
            print('LA DIRECCON IP ' + listaBL[contador3][0] + ' TIENE COMUNICACIÓN CON LA DIRECCIÓN IP DE BLACKLIST: ' +
                  listaBL[contador3][1] + ' POR EL PUERTO ' + str(listaBL[contador3][2]))
            contador3 += 1
        else:
            break

    return listaPeersBlacklist
#######################################################################
#                            Auto-Hunting                             #
#######################################################################
def autohunting():
    listaPeersPuertos = []
    listaPeersPuertos2 = []
    listaPeersPuertos3 = []
    listaPeersPuertosAltos = []
    listaPeersPuertosAltos2=[]
    listaGlobalCompleta=[]
    listaGlobalCompleta2 = []
    listaPeersBlacklist =[]
    listaMyports = [21, 22, 23, 53, 137, 139, 445, 3389, 4444, 5900]
    for i in range(len(listaMyports)):
        listaPeersPuertos=PeerHunting(listaMyports[i], 1,huntingDataEnteroGlob,indiceServicioGlob,listaOrigenesGlob,indiceOrigenGlob,listaDestinosGlob,indiceDestinoGlob)
        for j in range (len(listaPeersPuertos)):
            listaPeersPuertos3.append(listaPeersPuertos[j])
    #print(listaPeersPuertos3)
    print("...calculando puertos altos a partir del 1024...")
    listaPeersPuertosAltos=(puertosAltos(1024, 0,huntingDataEnteroGlob,indiceServicioGlob,listaOrigenesGlob,listaDestinosGlob,indiceOrigenGlob,indiceDestinoGlob))
    #print(listaPeersPuertosAltos)
    print('\r')
    print("...comparando vs listas negras...")
    listaPeersBlacklist=(listasNegras(0,huntingDataEnteroGlob,indiceDestinoGlob,indiceOrigenGlob,indiceServicioGlob))
    #print(listaPeersBlacklist)
    print("...imprimiendo...")
    print('')

    # Quitar ceros al arreglo
    for i in range(len(listaPeersPuertos3)):
        if listaPeersPuertos3[i] != 0:
            listaPeersPuertos2.append(listaPeersPuertos3[i])

    for i in range(len(listaPeersPuertosAltos)):
        if (listaPeersPuertosAltos[i] != 0):
            listaPeersPuertosAltos2.append(listaPeersPuertosAltos[i])

    # Juntarlos todo en una sola lista

    for i in range(len(listaPeersPuertos2)):
        listaGlobalCompleta.append(listaPeersPuertos2[i])

    for i in range(len(listaPeersPuertosAltos2)):
        listaGlobalCompleta.append(listaPeersPuertosAltos2[i])

    for i in range(len(listaPeersBlacklist)):
        listaGlobalCompleta.append(listaPeersBlacklist[i])

    # Remover duplicados
    seen = set()
    for value in listaGlobalCompleta:
        if value not in seen:
            listaGlobalCompleta2.append(value)
            seen.add(value)

    # Comparación
    contador1 = 0
    contador2 = 0
    contador3 = 0
    for i in range(len(listaGlobalCompleta2)):
        for j in range(len(listaPeersPuertos2)):
            if listaGlobalCompleta2[i] == listaPeersPuertos2[j]:
                contador1 += 1
        for k in range(len(listaPeersPuertosAltos2)):
            if listaGlobalCompleta2[i] == listaPeersPuertosAltos2[k]:
                contador2 += 1
        for l in range(len(listaPeersBlacklist)):
            if listaGlobalCompleta2[i] == listaPeersBlacklist[l]:
                contador3 += 1
        if contador1 >= 1 and contador2 >= 1 and contador3 >= 1:
            print('LA DIRECCION IP ' + str(listaGlobalCompleta2[i]) + " TIENE COMPORTAMIENTO ANOMALO PORQUE:")
            if contador1 >= 1:
                print('    TIENE COMUNICACION CON PEERS EN PUERTOS SOSPECHOSOS')
            if contador2 >= 1:
                print('    TIENE COMUNICACION CON PEERS EN PUERTOS ALTOS')
            if contador3 >= 1:
                print('    TIENE COMUNICACION CON DIRECCIONES IP EN BLACKLIST')
        contador1 = 0
        contador2 = 0
        contador3 = 0
#######################################################################
#                            Main                                     #
#######################################################################
loop = True

def principal():
    #Nombre de Log
    archivoLog = nombreArchivo()
    #Parsear Logs
    huntingData = parsearArchivo(archivoLog)
    #Obtener el indice del tiempo en el csv
    indiceTiempo = obtenerTiempo(huntingData)
    #Obtener tiempo inicial y final del log
    tiempoInicial,tiempoFinal=indiceTiempos(huntingData,indiceTiempo)
    #Obtener indices (localización) de origen, destino y puerto
    indiceOrigen,indiceDestino,indiceServicio=obtenerIndices(huntingData)
    #Obtener listas de origen y destion, quitar duplicados
    listaOrigenes,listaDestinos = obtenerListas(huntingData,indiceOrigen,indiceDestino)
    #Convertir a enteros los puertos de la lista principal
    huntingDataEntero=conversionEnteros(huntingData,indiceServicio)

    return archivoLog,tiempoInicial,tiempoFinal,indiceOrigen,indiceDestino,indiceServicio,listaOrigenes,listaDestinos,huntingDataEntero

archivoLogGlob,tiempoInicialGlob,tiempoFinalGlob,indiceOrigenGlob,indiceDestinoGlob,indiceServicioGlob,listaOrigenesGlob,listaDestinosGlob,huntingDataEnteroGlob = principal()

while loop:

    listaMyportsGlob=[]

    print ('******************************************')
    print ('AUTO-HUNTING V 1.0')
    print('')
    print ('1.- Hunting Puertos específicos')
    print ('2.- Hunting Puertos Altos')
    print ('3.- Comparación de Destinos vs listas Negras')
    print ('4.- Autohunting')
    print ('5.- Hunting Puertos Sospechosos')
    print ('9.- Salir')
    print ('******************************************')
    print ('El log que se analizará es: ' + archivoLogGlob)
    print('Se analizan logs entre ' + tiempoInicialGlob + " y " + tiempoFinalGlob)
    print ("*********************************************")
    opcion=input("Selecciona la Opcion Deseada:")
    print ('')

    if (opcion=='1'):
        print ('Especifica los puertos de Hunting, separados por comas')
        listaMyportsGlob=input().split(",")
        for i in range (len(listaMyportsGlob)):
            PeerHunting(int(listaMyportsGlob[i]),0,huntingDataEnteroGlob,indiceServicioGlob,listaOrigenesGlob,indiceOrigenGlob,listaDestinosGlob,indiceDestinoGlob)
    elif (opcion=='2'):
        print('A partir de qué puerto hacer la revisión de puertos altos?')
        puertoGlob=input()
        puertosAltos(int(puertoGlob),0,huntingDataEnteroGlob,indiceServicioGlob,listaOrigenesGlob,listaDestinosGlob,indiceOrigenGlob,indiceDestinoGlob)
    elif (opcion=='3'):
        print ('')
        print ('EVALUACIÓN DE HOSTS VS LISTAS NEGRAS')
        print ('')
        listasNegras(0,huntingDataEnteroGlob,indiceDestinoGlob,indiceOrigenGlob,indiceServicioGlob)
    elif (opcion=='4'):
        print("...Ejecutando Autohunting...")
        print ('\r')
        autohunting()
    elif (opcion == '5'):
        print("...calculando Peers de puertos 21,22,23,53,137,139,445,3389,4444,5900...")
        print('\r')
        listaMyports = [21, 22, 23, 53, 137, 445, 389, 3389, 4444, 5900]
        for i in range(len(listaMyports)):
            PeerHunting(int(listaMyports[i]),0,huntingDataEnteroGlob,indiceServicioGlob,listaOrigenesGlob,indiceOrigenGlob,listaDestinosGlob,indiceDestinoGlob)
    elif (opcion == '9'):
        loop = False
    else:
        print('Selecciona una opción valida')