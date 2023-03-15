
from MapGPIO_Model import MapGPIO_Model
import json 
import os
import RPi.GPIO as gpio
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

class MapGPIO_Controller:   

    #inicilizacao***********************************************# 
    def __init__(self):
        self.COMs                   = []
        self.todos_componentes_gpio = {}
        self.todos_componentes_I2C  = {}

        logging.basicConfig(filename = "MapGPIO.log", format='%(asctime)s:%(levelname)s:%(filename)s:%(message)s', level = logging.DEBUG)

    #***********************************************************#
    def retornar_lista_gpio(self): 
        return range(4, 27 + 1)

    #***********************************************************#
    def retornar_lista_gpio_I2C(self):    
        return [2, 3]

    def zerar_componentes_salvos(self):
        self.COMs                   = []
        self.todos_componentes_gpio = {}
        self.todos_componentes_I2C  = {}

    #***********************************************************#
    def adicionar_novo_COM(self):

        self.COMs.append(MapGPIO_Model())

    #***********************************************************#
    def gravar_COM(self, map_GPIO_COM, nome_arquivo):        

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
                json_file.close()             
            return True
        except:
            return False
        
    #***********************************************************#
    def gerar_mapeamentos_gravados(self, lista_arquivos):

        for COM in self.COMs:
            arquivo = self.retornar_nome_arquivo_livre()
            
            if not self.gravar_COM(COM, arquivo):
                return False 
            
            time.sleep(1) # Necessario pois gera erro no Raspberry gravar muitos arquivos instantaneamente
            
            lista_arquivos.append(arquivo)

        return True   


    #***********************************************************#
    def carregar_COM(self, nome_arquivo):

        if not (os.path.isfile(nome_arquivo)):
            return False
        
        try:
            with open( nome_arquivo, 'r') as openfile:      
                json_object = json.load(openfile) 
                openfile.close()
        except:
            return False

        COM = MapGPIO_Model()

        for gpio in json_object['botoes']:
            COM.set_botao(gpio)
        
        for gpios in json_object['joysticks']:
            COM.set_joystick(gpios)

        for porta in json_object['analogicos']:
            COM.set_analogico(porta)

        self.COMs.append(COM)

        return True    

    #***********************************************************#
    def retornar_nome_arquivo_livre(self):

        numero = 1

        while True:        
            nome_arquivo = 'COM' + str(numero).zfill(3) + '.json'
            if not (os.path.isfile(nome_arquivo)):
                return nome_arquivo

            numero += 1

    #***********************************************************#
    def retornar_lista_mapeamentos_pasta(self):

        lista_arquivos = []

        for arquivo in list(filter(os.path.isfile, os.listdir())):
            nome, extensao = os.path.splitext(arquivo) 

            if nome[0:3] == 'COM' and extensao == '.json' and len(nome) == 6:
                lista_arquivos.append(nome)

        lista_arquivos.sort()
        
        return lista_arquivos

    #***********************************************************#
    def inicializar_componentes_salvos(self):

        if len(self.COMs) == 0:
            return False
        
        gpio.setmode(gpio.BCM)
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        for COM in self.COMs:    
            self.inicializacao_gpio(COM)
            self.inicializacao_I2C_analogico(COM, ads)    

        return True

    #***********************************************************#
    def inicializacao_gpio(self, COM):

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
    def inicializacao_I2C_analogico(self, COM, ads):
    
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
    def carregar_status_componentes_salvos(self):

        if len(self.COMs) == 0:
            return False

        for COM in self.COMs: 

            # Botoes
            if len(COM.get_lista_botoes()) > 0:        
                for botao in COM.get_lista_botoes(): 
                    status = False
            
                    if gpio.input(botao['gpio']) == gpio.LOW:
                        logging.warning('INPUT DE BOTÃO EM GPIO:' + str(botao['gpio']).zfill(2))
                        status = True 

                    botao['status'] = status

            # Joysticks
            if len(COM.get_lista_joysticks()) > 0:        
                for joystick in COM.get_lista_joysticks():
                    for direcao in ['up', 'down', 'left', 'right']:
                        status = False

                        if gpio.input(joystick['gpio'][direcao]) == gpio.LOW:
                            logging.warning('INPUT DE JOYSTICK EM GPIO:' + str(joystick['gpio'][direcao]).zfill(2) + ' NA DIREÇÃO:' + direcao )
                            status = True 

                        joystick['status'][direcao] = status

            # Portas Analogicas
            if len(COM.get_lista_analogicos()) > 0:
                for analogico in COM.get_lista_analogicos():      
                    logging.warning('VALORES LIDOS DE POTENCIOMETRO NA PORTA:' + str(analogico['porta']).zfill(2) + ' Valor:' + str(analogico['conversor'].value) + ' Voltagem:' + str(analogico['conversor'].voltage) )              
                    analogico['status']['valor'   ] = analogico['conversor'].value
                    analogico['status']['corrente'] = analogico['conversor'].voltage

    #***********************************************************#
    def inicializar_todos_componentes(self):
        
        self.limpar_gpio()

        try:
            gpio.setmode(gpio.BCM)

            for pino in self.retornar_lista_gpio():
                gpio.setup(pino, gpio.IN, pull_up_down = gpio.PUD_UP)
                self.todos_componentes_gpio[pino] = False
            
            i2c = busio.I2C(board.SCL, board.SDA)   
            ads = ADS.ADS1115(i2c)

            self.todos_componentes_I2C[0] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P0) }
            self.todos_componentes_I2C[1] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P1) }
            self.todos_componentes_I2C[2] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P2) }
            self.todos_componentes_I2C[3] = { 'valor': 0, 'corrente': 0, 'conversor': AnalogIn(ads, ADS.P3) } 
            
        except:
            return False    
        
        return True    


    #***********************************************************#
    def carregar_status_todos_componentes(self):

        for pino in self.retornar_lista_gpio():        
            status = False
            
            if gpio.input(pino) == gpio.LOW:
                logging.warning('GERAL: INPUT GERAL DE GPIO:' + str(pino).zfill(2) )
                status = True 

            self.todos_componentes_gpio[pino] = status

        for porta in range(4):
            logging.warning('GERAL: POTENCIOMETRO NA PORTA:' + str(porta).zfill(2) + ' Valor:' + str(self.todos_componentes_I2C[porta]['conversor'].value) + ' Voltagem:' + str(self.todos_componentes_I2C[porta]['conversor'].voltage ) )
            self.todos_componentes_I2C[porta]['valor'   ] = self.todos_componentes_I2C[porta]['conversor'].value
            self.todos_componentes_I2C[porta]['corrente'] = self.todos_componentes_I2C[porta]['conversor'].voltage     

    #***********************************************************#
    def limpar_gpio(self):

        gpio.cleanup()              

    #***********************************************************#
    def retornar_GPIO_com_input_todos_componentes(self):
        
        self.carregar_status_todos_componentes()

        for chave in self.todos_componentes_gpio.keys():                
            if self.todos_componentes_gpio[chave]:
                return chave             
        
        return 0
    
    #***********************************************************#
    def retornar_porta_acionado_todos_componentes(self):
        
        for porta in range(4):            
            if self.todos_componentes_I2C[porta]['conversor'].voltage >= 3:
                return porta
                
        return None
    
    #***********************************************************#
    def porta_gpio_ja_utilizado_mapeamento(self, gpio=None, porta=None):

        if len(self.COMs) == 0:
            return False

        for COM in self.COMs: 

            if not gpio == None:            

                # Botoes
                if len(COM.get_lista_botoes()) > 0:        
                    for botao in COM.get_lista_botoes(): 

                        if botao['gpio'] == gpio:
                            return True                       

                # Joysticks
                if len(COM.get_lista_joysticks()) > 0:        
                    for joystick in COM.get_lista_joysticks():
                        for direcao in ['up', 'down', 'left', 'right']:
                            if joystick['gpio'][direcao] == gpio:
                                return True

            if not porta == None:           

                # Portas Analogicas
                if len(COM.get_lista_analogicos()) > 0:
                    for analogico in COM.get_lista_analogicos():
                        if analogico['porta'] == porta:
                            return True
    
        return False
    
    #***********************************************************#
    def remover_item_mapeamento(self, gpio=None, porta=None, com=0):

        if len(self.COMs) == 0 or len(self.COMs) < com:
            return 
        
        COM = self.COMs[ com ]  

        if not gpio == None:            

            # Botoes
            if len(COM.get_lista_botoes()) > 0:  
                for posicao in range(len(COM.get_lista_botoes())): 
                    if COM.get_lista_botoes()[posicao]['gpio'] == gpio:
                        COM.get_lista_botoes().pop(posicao)
                        return                        

                # Joysticks
                if len(COM.get_lista_joysticks()) > 0: 
                    for posicao in range(len(COM.get_lista_joysticks())):
                        for direcao in ['up', 'down', 'left', 'right']:
                            if COM.get_lista_joysticks()[posicao]['gpio'][direcao] == gpio:
                                COM.get_lista_joysticks().pop(posicao)
                                return
                            

        if not porta == None:           

            # Portas Analogicas
            if len(COM.get_lista_analogicos()) > 0:
                for posicao in range(len(COM.get_lista_analogicos())):                    
                    if COM.get_lista_analogicos()[posicao]['porta'] == porta:
                        COM.get_lista_analogicos().pop(posicao)
                        return         

