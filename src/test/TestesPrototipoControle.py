import os
import RPi.GPIO as gpio
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#***********************************************************#
def retornar_lista_gpio():  
  
   # Intervalo GPIO é 4 - 27
   return range(4, 27 + 1)

#***********************************************************#
def retornar_lista_gpio_I2C():  

   # 2 e 3 são reservados para conversor Analogico
   return [2, 3]

#***********************************************************#
def retornar_dicionario_gpio():

   dicionario_gpio = {}

   for pino in retornar_lista_gpio():
      dicionario_gpio[pino] = ''

   return dicionario_gpio

#***********************************************************#
def inicilizacao_gpio():

   gpio.setmode(gpio.BCM)

   for pino in retornar_lista_gpio():
      gpio.setup(pino, gpio.IN, pull_up_down = gpio.PUD_UP)

   return retornar_dicionario_gpio()

#***********************************************************#
def carregar_status_gpio(dicionario_gpio):

   for pino in retornar_lista_gpio():        
      status = ''
        
      if gpio.input(pino) == gpio.LOW:
         status = 'PRESSIONADO'  

      dicionario_gpio[pino] = status

#***********************************************************#
def inicializacao_I2C_analogico():

   # Iniciliaza a interface I2C
   i2c = busio.I2C(board.SCL, board.SDA)

   # Monta objeto conversor Digital para Analógico
   ads = ADS.ADS1115(i2c)

   # Istancia canais para leitura
   canalA0 = AnalogIn(ads, ADS.P0)
   canalA1 = AnalogIn(ads, ADS.P1)
   canalA2 = AnalogIn(ads, ADS.P2)
   canalA3 = AnalogIn(ads, ADS.P3)

   return [canalA0, canalA1, canalA2, canalA3]

#***********************************************************#
def limparTerminal():
   
   if os.name == "nt":
      os.system("cls") # Terminal Windows
   else:
      os.system("clear") # Terminal Linux

#***********************************************************#
def exibir_status_gpio(dicionario_gpio, lista_canais_I2C):

   limparTerminal()
   
   print('Input dos Pinos GPIO')
   print('[GPIO]:[   STATUS    ]  [GPIO]:[   STATUS    ]')
   print('----------------------------------------------')
   for pino in range(4, 27 + 1, 2):
      print('[ {:>2} ]:[ {:>11} ]'.format(pino, dicionario_gpio[pino]),
            '[ {:>2} ]:[ {:>11} ]'.format(pino + 1, dicionario_gpio[pino + 1]), sep='  ') 

   print('\n\nConversor Analógico I2C')
   print('[CANAL]:[VALOR]:[VOLTAGEM]')
   print('--------------------------')
   for canal in range(len(lista_canais_I2C)):
      print('[A{}]:[{:>5}]:[ {:>7,.2f}]'.format(canal,
                                                abs(lista_canais_I2C[canal].value), 
                                                abs(lista_canais_I2C[canal].voltage)))

#***********************************************************#
if __name__ == '__main__':

   dicionario_gpio = inicilizacao_gpio()
   lista_canais_I2C = inicializacao_I2C_analogico()   

   while True:
      carregar_status_gpio(dicionario_gpio)
         
      exibir_status_gpio(dicionario_gpio, lista_canais_I2C)
      
      time.sleep(0.08)
   
   gpio.cleanup()

   