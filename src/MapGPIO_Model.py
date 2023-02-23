class MapGPIO_Model:   

    #inicilizacao***********************************************# 
    def __init__(self):
        self._lista_botoes     = []
        self._lista_joysticks  = []
        self._lista_analogicos = [] 

    #getters****************************************************# 
    def get_lista_botoes(self):
        return self._lista_botoes

    def get_lista_joysticks(self):
        return self._lista_joysticks

    def get_lista_analogicos(self):
        return self._lista_analogicos

    #setters****************************************************#    
    def set_lista_botoes(self, lista_botoes):
        self._lista_botoes = lista_botoes

    def set_lista_joysticks(self, lista_joysticks):
        self._lista_joysticks = lista_joysticks

    def set_lista_analogicos(self, lista_analogicos):
        self._lista_analogicos = lista_analogicos

    def set_botao(self, pino_gpio):
        self._lista_botoes.append( { 'gpio': pino_gpio, 'status': False} )

    def set_joystick(self, dicionario_joystick): 
        self._lista_joysticks.append( { 'gpio': dicionario_joystick , 'status': { 'up': False,
                                                                                  'down': False,
                                                                                  'left': False,
                                                                                  'right': False } } )

    def set_analogico(self, porta_analogica ):

        self._lista_analogicos.append( { 'porta': porta_analogica,
                                         'status': { 'valor': 0, 'corrente': 0}, 
                                         'conversor': None } )


    