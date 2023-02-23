
from MapGPIO_Model import MapGPIO_Model
import json 
import os
import RPi.GPIO as gpio
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

COMs                   = []
todos_componentes_gpio = {}
todos_componentes_I2C  = {}

#***********************************************************#
def retornar_lista_gpio(): 
   return range(4, 27 + 1)

#***********************************************************#
def retornar_lista_gpio_I2C():    
   return [2, 3]

#***********************************************************#
def gravar_COM( map_GPIO_COM, nome_arquivo ):

    botoes = []
    for botao in map_GPIO_COM.get_lista_botoes():
        botoes.append( botao['gpio'] )

    joysticks = []
    for joystick in map_GPIO_COM.get_lista_joysticks():
       joysticks.append( joystick['gpio'] )   

    analogicos = []
    for analogico in map_GPIO_COM.get_lista_analogicos():
       analogicos.append( analogico['porta'] )  

    dicionario_JSON = { 'botoes':     botoes,
                        'joysticks':  joysticks,
                        'analogicos': analogicos }   

    try:
        with open(nome_arquivo, 'w') as json_file:
            json.dump(dicionario_JSON, json_file, indent=4)        
        return True
    except:
        return False
    

#***********************************************************#
def carregar_COM( nome_arquivo ):

    if not (os.path.isfile(nome_arquivo)):
        return False
    
    try:
        with open( nome_arquivo, 'r') as openfile:      
            json_object = json.load(openfile) 
    except:
        return False

    COM = MapGPIO_Model()

    for gpio in json_object['botoes']:
        COM.set_botao(gpio)
    
    for gpios in json_object['joysticks']:
        COM.set_joystick(gpios)

    for porta in json_object['analogicos']:
        COM.set_analogico(porta)

    COMs.append(COM)

    return True    

#***********************************************************#
def inicializar_componentes_salvos():

    if len(COMs) == 0:
        return False
    
    gpio.setmode(gpio.BCM)
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)

    for COM in COMs:    
        inicializacao_gpio(COM)
        inicializacao_I2C_analogico(COM, i2c, ads)    

    return True

#***********************************************************#
def inicializacao_gpio(COM):

    if len(COM.get_lista_botoes()) > 0:        
        for botao in COM.get_lista_botoes():
            gpio.setup(botao['gpio'], gpio.IN, pull_up_down = gpio.PUD_UP)

    if len(COM.get_lista_joysticks()) > 0:        
        for joystick in COM.get_lista_joysticks():
            gpio.setup(joystick['gpio']['up'   ], gpio.IN, pull_up_down = gpio.PUD_UP)
            gpio.setup(joystick['gpio']['down' ], gpio.IN, pull_up_down = gpio.PUD_UP)
            gpio.setup(joystick['gpio']['left' ], gpio.IN, pull_up_down = gpio.PUD_UP)
            gpio.setup(joystick['gpio']['right'], gpio.IN, pull_up_down = gpio.PUD_UP)

#***********************************************************#
def inicializacao_I2C_analogico(COM, i2c, ads):
  
    if len(COM.get_lista_analogicos()) > 0:
        for analogico in COM.get_lista_analogicos():
            
            if analogico['porta'] == 0:
                conversor = AnalogIn(ads, ADS.P0)
            elif analogico['porta'] == 1:
                conversor = AnalogIn(ads, ADS.P1)
            elif analogico['porta'] == 2:
                conversor = AnalogIn(ads, ADS.P2)
            else:
                conversor = AnalogIn(ads, ADS.P3)
            
            analogico['conversor'] = conversor

#***********************************************************#
def carregar_status_componentes_salvos():

    if len(COMs) == 0:
        return False

    for COM in COMs: 

        # Botoes
        if len(COM.get_lista_botoes()) > 0:        
            for botao in COM.get_lista_botoes(): 
                status = False
        
                if gpio.input(botao['gpio']) == gpio.LOW:
                    status = True 

                botao['status'] = status

        # Joysticks
        if len(COM.get_lista_joysticks()) > 0:        
            for joystick in COM.get_lista_joysticks():
                for direcao in ['up', 'down', 'left', 'right']:
                    status = False

                    if gpio.input(joystick['gpio'][direcao]) == gpio.LOW:
                        status = True 

                    joystick['status'][direcao] = status

        # Portas Analogicas
        if len(COM.get_lista_analogicos()) > 0:
            for analogico in COM.get_lista_analogicos():
                analogico['status']['valor'   ] = analogico['conversor'].value
                analogico['status']['corrente'] = analogico['conversor'].voltage

#***********************************************************#
def inicializar_todos_componentes():

    gpio.setmode(gpio.BCM)

    for pino in retornar_lista_gpio():
        gpio.setup(pino, gpio.IN, pull_up_down = gpio.PUD_UP)
        todos_componentes_gpio[pino] = False
    
    i2c = busio.I2C(board.SCL, board.SDA)   
    ads = ADS.ADS1115(i2c)

    todos_componentes_I2C[0] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P0) }
    todos_componentes_I2C[1] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P1) }
    todos_componentes_I2C[2] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P2) }
    todos_componentes_I2C[3] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P3) }     

#***********************************************************#
def carregar_status_todos_componentes():

    for pino in retornar_lista_gpio():        
        status = False
        
        if gpio.input(pino) == gpio.LOW:
            status = True 

        todos_componentes_gpio[pino] = status

    for porta in range(4):
        todos_componentes_I2C[porta]['valor'   ] = todos_componentes_I2C[porta]['conversor'].value
        todos_componentes_I2C[porta]['corrente'] = todos_componentes_I2C[porta]['conversor'].voltage        

    

#***********************************************************#
def finalizar_gpio():
    gpio.cleanup()
           

#***********************************************************#
def Teste():

    #model1 = MapGPIO_Model()    
    #model1.set_botao(16)   
    #model1.set_joystick({'up':20, 'down':9, 'left':10, 'right':11})  
    #model1.set_analogico(0)    
    #COMs.append(model1)   

    if not carregar_COM( 'teste.json' ):
        print('erro')
        return

    inicializar_componentes_salvos()

    while True:
        carregar_status_componentes_salvos()
        print(COMs[0].get_lista_botoes())  
        print(COMs[0].get_lista_joysticks())  
        print(COMs[0].get_lista_analogicos())        

        time.sleep(0.08)

    #print(COMs[0].get_lista_botoes())
    #print(COMs[0].get_lista_joysticks())
    #print(COMs[0].get_lista_analogicos())
    #print(gravar_COM( model1, 'teste.json' ))
    #print(carregar_COM( 'teste.json' ))
    #print(COMs[1].get_lista_botoes())
    #print(COMs[1].get_lista_joysticks())
    #print(COMs[1].get_lista_analogicos())

    finalizar_gpio()

