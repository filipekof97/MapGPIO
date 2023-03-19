from MapGPIO_Controller import MapGPIO_Controller
import pygame
import time
import random

#***********************************************************#
# Valores Constantes
PRETO   = (0, 0, 0)
BRANCO  = (255, 255, 255)
VERDE   = (0, 255, 0)

LARGURA_MAX = 900
ALTURA_MAX  = 600

ESPESSURA_BARRA_INFERIOR = 20
ESPESSURA_BARRA_CENTRAL  = 5

CORRENTE_MAX = 3.3

VELOCIDADE_BOLA_MIN = 2
VELOCIDADE_BOLA_MAX = 30

FPS = 30

BOLA_SAIU_DIREITA  = -1
BOLA_SAIU_ESQUERDA = 1
BOLA_DENTRO_MAPA   = 0

BOLA_INVERTER_DIRECAO = -1

BOLA_DIRECAO_X_DIREITA  = 1
BOLA_DIRECAO_X_ESQUERDA = -1
BOLA_DIRECAO_Y_CIMA     = -1
BOLA_DIRECAO_Y_BAIXO    = 1

DIRECAO_RETANGULO_CIMA   = -1
DIRECAO_RETANGULO_PARADO = 0
DIRECAO_RETANGULO_BAIXO  = 1

PONTUACAO_MAXIMA = 12

lista_direcoes = [-1,1]


#***********************************************************#
# Inicilizacao das instancias
pygame.init()

fonte_pontuacao = pygame.font.SysFont('arial', 50)
fonte_normal = pygame.font.SysFont('arial', 30)

screen = pygame.display.set_mode((LARGURA_MAX, ALTURA_MAX))
pygame.display.set_caption(' JOGO PONG ')

clock = pygame.time.Clock()

controller_map_gpio = MapGPIO_Controller()
controller_map_gpio.carregar_COM('COM001' + '.json')
controller_map_gpio.carregar_COM('COM002' + '.json')
controller_map_gpio.inicializar_componentes_salvos()

#***********************************************************#
class Jogador:
   def __init__(self, posicao_x, posicao_y, joystick):
      self.posicao_x     = posicao_x
      self.posicao_y     = posicao_y
      self.joystick = joystick

      self.largura    = 10
      self.altura     = 100
      self.velocidade = 20
      self.pontuacao  = 0

      self.posicao_retangulo = pygame.Rect(posicao_x, posicao_y, self.largura, self.altura)
      self.retangulo         = pygame.draw.rect(screen, BRANCO, self.posicao_retangulo)


   def desenhar_objeto(self):
      self.retangulo = pygame.draw.rect(screen, BRANCO, self.posicao_retangulo)


   def atualizar_posicao(self, direcao_y):
      self.posicao_y = self.posicao_y + self.velocidade * direcao_y

      if self.posicao_y <= 0:
         self.posicao_y = 0

      elif self.posicao_y + self.altura >= ALTURA_MAX - ESPESSURA_BARRA_INFERIOR:
         self.posicao_y = ALTURA_MAX - ESPESSURA_BARRA_INFERIOR - self.altura

      self.posicao_retangulo = (self.posicao_x, self.posicao_y, self.largura, self.altura)


   def get_posicao(self):
      return self.posicao_retangulo


#***********************************************************#
class Bola:
   def __init__(self):
      self.posicao_x   = LARGURA_MAX//2
      self.posicao_y   = ALTURA_MAX//2
      self.radius      = 7
      self.direcao_x   = sorteio_direcao()
      self.direcao_y   = sorteio_direcao()
      self.velocidade  = 7
      self.bola        = pygame.draw.circle(screen, VERDE, (self.posicao_x, self.posicao_y), self.radius)

   def desenhar_objeto(self):
      self.bola = pygame.draw.circle(screen, VERDE, (self.posicao_x, self.posicao_y), self.radius)

   def atualizar_posicao(self):
      self.posicao_x += self.velocidade * self.direcao_x
      self.posicao_y += self.velocidade * self.direcao_y

      if self.posicao_y <= 0 or self.posicao_y >= ALTURA_MAX - ESPESSURA_BARRA_INFERIOR:
         self.direcao_y *= BOLA_INVERTER_DIRECAO

      if self.posicao_x <= 0:
         return BOLA_SAIU_ESQUERDA
      elif self.posicao_x >= LARGURA_MAX:
         return BOLA_SAIU_DIREITA
      else:
         return BOLA_DENTRO_MAPA

   def reiniciar(self):
      self.posicao_x = LARGURA_MAX//2
      self.posicao_y = sorteio_altura()
      self.direcao_x *= BOLA_INVERTER_DIRECAO
      self.direcao_y = sorteio_direcao()

   def rebateu(self):
      self.direcao_x *= BOLA_INVERTER_DIRECAO

   def get_posicao(self):
      return self.bola

   def setar_velocidade_potenciometro(self, corrente):
      velocidade = int(corrente * ( VELOCIDADE_BOLA_MAX / CORRENTE_MAX ) )

      if velocidade < VELOCIDADE_BOLA_MIN:
         velocidade = VELOCIDADE_BOLA_MIN

      self.velocidade = velocidade

      return


#***********************************************************#
class Mapa():

   def __init__(self, jogador1, jogador2, bola):
      self.jogador1      = jogador1
      self.jogador2      = jogador2
      self.bola          = bola

   def desenhar_mapa(self):
      self.escreve_pontuacao(self.jogador1.pontuacao, 100, 60 )
      self.escreve_pontuacao(self.jogador2.pontuacao, LARGURA_MAX-100, 60 )
      pygame.draw.line(screen, BRANCO, (0, ALTURA_MAX - ESPESSURA_BARRA_INFERIOR//2 ), (LARGURA_MAX, ALTURA_MAX - ESPESSURA_BARRA_INFERIOR//2), ESPESSURA_BARRA_INFERIOR )
      pygame.draw.line(screen, BRANCO, (LARGURA_MAX//2, 0 ), (LARGURA_MAX//2, ALTURA_MAX), ESPESSURA_BARRA_CENTRAL)

      self.jogador1.desenhar_objeto()
      self.jogador2.desenhar_objeto()
      self.bola.desenhar_objeto()

   def escreve_pontuacao(self, pontuacao, posicao_x, posicao_y ):
      escreve_na_tela(str(pontuacao), fonte_pontuacao, posicao_x, posicao_y)

   def verificar_fim_jogo(self):
      ganhador = 0

      if self.jogador1.pontuacao == PONTUACAO_MAXIMA:
         ganhador = 1

      elif self.jogador2.pontuacao == PONTUACAO_MAXIMA:
         ganhador = 2

      if ganhador == 0:
         return False

      escreve_na_tela('Jogador ' + str(ganhador) + ' ganhou!', fonte_normal, LARGURA_MAX//2, ALTURA_MAX//2)
      escreve_na_tela('Fim de Jogo', fonte_normal, LARGURA_MAX//2, ALTURA_MAX//2 + 200)
      pygame.display.update()
      time.sleep(6)

      return True

#***********************************************************#
def sorteio_direcao():
   return lista_direcoes[random.randint(0,1)]

#***********************************************************#
def sorteio_altura():
   return random.randint(1, ALTURA_MAX - ESPESSURA_BARRA_INFERIOR)

#***********************************************************#
def escreve_na_tela(texto, fonte, posicao_x, posicao_y):
   texto = fonte.render( texto, True, BRANCO)
   posicao_texto = texto.get_rect()
   posicao_texto.center = (posicao_x, posicao_y)
   screen.blit(texto, posicao_texto)

#***********************************************************#
def iniciar_jogo():

   joystick1 = controller_map_gpio.COMs[0].get_lista_joysticks()[0]
   joystick2 = controller_map_gpio.COMs[1].get_lista_joysticks()[0]

   potenciometro = controller_map_gpio.COMs[0].get_lista_analogicos()[0]

   jogador1 = Jogador(20, 0, joystick1)
   jogador2 = Jogador(LARGURA_MAX-30, 0, joystick2)
   bola     = Bola()

   mapa = Mapa(jogador1, jogador2, bola)

   continua_loop = True

   while continua_loop:
      screen.fill(PRETO)

      if mapa.verificar_fim_jogo():
         break

      controller_map_gpio.carregar_status_componentes_salvos()


      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            continua_loop = False

      if joystick1['status']['up']:
         direcao_retangulo_1 = DIRECAO_RETANGULO_CIMA
      elif joystick1['status']['down']:
         direcao_retangulo_1 = DIRECAO_RETANGULO_BAIXO
      else:
         direcao_retangulo_1 = DIRECAO_RETANGULO_PARADO

      if joystick2['status']['up']:
         direcao_retangulo_2 = DIRECAO_RETANGULO_CIMA
      elif joystick2['status']['down']:
         direcao_retangulo_2 = DIRECAO_RETANGULO_BAIXO
      else:
         direcao_retangulo_2 = DIRECAO_RETANGULO_PARADO


      bola.setar_velocidade_potenciometro(potenciometro['status']['corrente'])

      if pygame.Rect.colliderect(bola.get_posicao(), jogador1.get_posicao()) or pygame.Rect.colliderect(bola.get_posicao(), jogador2.get_posicao()):
         bola.rebateu()

      jogador1.atualizar_posicao(direcao_retangulo_1)
      jogador2.atualizar_posicao(direcao_retangulo_2)

      localizacao_bola = bola.atualizar_posicao()

      if localizacao_bola == BOLA_SAIU_DIREITA:
         jogador1.pontuacao += 1
      elif localizacao_bola == BOLA_SAIU_ESQUERDA:
         jogador2.pontuacao += 1

      if localizacao_bola != BOLA_DENTRO_MAPA:
         bola.reiniciar()

      mapa.desenhar_mapa()

      pygame.display.update()
      clock.tick(FPS)


#***********************************************************#
def apertar_start():

   botao1 = controller_map_gpio.COMs[0].get_lista_botoes()[0]
   botao2 = controller_map_gpio.COMs[1].get_lista_botoes()[0]

   pressionou_start_1 = False
   pressionou_start_2 = False

   while not pressionou_start_1 or not pressionou_start_2:
      screen.fill(PRETO)
      pygame.draw.line(screen, BRANCO, (0, ALTURA_MAX - ESPESSURA_BARRA_INFERIOR//2 ), (LARGURA_MAX, ALTURA_MAX - ESPESSURA_BARRA_INFERIOR//2), ESPESSURA_BARRA_INFERIOR )
      pygame.draw.line(screen, BRANCO, (LARGURA_MAX//2, 0 ), (LARGURA_MAX//2, ALTURA_MAX), ESPESSURA_BARRA_CENTRAL)

      controller_map_gpio.carregar_status_componentes_salvos()

      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            return False

      if not pressionou_start_1:
         escreve_na_tela('Pressione o botão!', fonte_normal, 220, ALTURA_MAX//2)

         if botao1['status']:
            pressionou_start_1 = True

      else:
         escreve_na_tela('Pronto', fonte_normal, 220, ALTURA_MAX//2)

      if not pressionou_start_2:
         escreve_na_tela('Pressione o botão!', fonte_normal, LARGURA_MAX//2 + 220, ALTURA_MAX//2)

         if botao2['status']:
            pressionou_start_2 = True
      else:
         escreve_na_tela('Pronto', fonte_normal, LARGURA_MAX//2 + 220, ALTURA_MAX//2)

      pygame.display.update()
      clock.tick(FPS)

   return True


#***********************************************************#
if __name__ == "__main__":

   while apertar_start():
      iniciar_jogo()

   pygame.quit()
   controller_map_gpio.limpar_gpio()
