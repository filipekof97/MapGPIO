from MapGPIO_Controller import MapGPIO_Controller
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo, askquestion
import datetime
import time
import os

#***********************************************************#

def inicializar_modulo_tkinter():
    
    root = tk.Tk()
    root.title('MapGPIO')

    # Tamanho da Tela
    window_width  = 820
    window_height = 560

    # Pegando resolução do monitor
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Encontrando o ponto central
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)

    # Posicionando o janela principal no centro do monitor
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Desabilitante resizing
    root.resizable(False, False)

    # Nivel de transparencia da tela de 0 (tranparente) a 1 (nitido)
    # root.attributes('-alpha', 0.5) Não funciona no Linux

    # Deixa sempre visivel a tela sobre as outras
    # root.attributes('-topmost', 1)

    return root

#***********************************************************#
def apertou_novo_editar(janela_anterior, nome_arquivo=None):
     
    if not janela_anterior == None:
        janela_anterior.destroy()

    janela = inicializar_modulo_tkinter()  

    if nome_arquivo == None:
        titulo_tela = "Novo Mapeamento"
    else:
        titulo_tela = "Alteração de Mapeamento"

    ttk.Label(janela, text=titulo_tela, font=( "Helvetica", 20 )).place(x=40, y= 25) # [X e width=Horizontal] [y e height=Vertical]   

    # Selecao de Tipo
    ttk.Label(janela, text="Tipo:"          , font=( "Helvetica", 16 )).place(x=60, y=100)
    tipo_selecionado = tk.StringVar()
    tipo_combobox = ttk.Combobox(janela, textvariable=tipo_selecionado )
    tipo_combobox['values'] = ('Botão', 'Joystick', 'Potenciômetro')
    tipo_combobox['state' ] = 'readonly'
    tipo_combobox.place(x=120, y=100, width=150, height=30)  
    tipo_combobox.current(0)

    controller_map_gpio = MapGPIO_Controller()

    if nome_arquivo != None:
        controller_map_gpio.zerar_componentes_salvos()
        controller_map_gpio.carregar_COM(nome_arquivo + '.json')
    
    # Lista de Itens
    ttk.Label(janela, text="Lista de Itens" , font=( "Helvetica", 12 )).place(x=60, y=170) 
    lista_itens = tk.StringVar() 
    scrollbar = ttk.Scrollbar( janela, orient=tk.VERTICAL)
    scrollbar.place(x=410, y=200, height=300)
    listbox = tk.Listbox( janela, listvariable=lista_itens, yscrollcommand=scrollbar.set, font=( "Helvetica", 14 ), selectmode=tk.SINGLE)          
    listbox.place(x=60, y=200, width=350, height=300 )         
    scrollbar.config(command=listbox.yview)   

    if nome_arquivo != None:
        for item in retornar_lista_componentes_com(controller_map_gpio) :
            listbox.insert(tk.END, item) 

    # Console de LOGs
    ttk.Label(janela, text="Console de LOGs" , font=( "Helvetica", 10 )).place(x=430, y=35)     
    scrollbar2 = ttk.Scrollbar( janela, orient=tk.VERTICAL)
    scrollbar2.place(x=750, y=60, height=100)
    console_logs = tk.Text(janela, state=tk.DISABLED, font=('Arial', 8), yscrollcommand=scrollbar2.set, bg='Gray95', fg='red' )
    console_logs.place(x=430, y=60, width=320, height=100 )
    scrollbar2.config(command=console_logs.yview)   
    
    if nome_arquivo == None:
        controller_map_gpio.zerar_componentes_salvos()
        controller_map_gpio.adicionar_novo_COM()

    if not Inicializar_mapgpio_controller(controller_map_gpio, console_logs):        
        janela.destroy()
        return       

    # Botão Adicionar
    button_adicionar = ttk.Button(janela, text="Adicionar",  command=lambda: botao_adicionar_item(listbox, tipo_combobox, console_logs, controller_map_gpio, janela, button_adicionar))
    button_adicionar.place(x=280, y=100, width=100, height=30 )

    # Botão Retirar
    button_retirar = ttk.Button(janela, text="Retirar",    command=lambda: botao_retirar_item(listbox, console_logs, button_retirar, controller_map_gpio), )
    button_retirar.place(x=470, y=200, width=300, height=60 )
    button_retirar.state(['disabled'])
    listbox.bind("<<ListboxSelect>>", lambda _: controle_selecao_lista_itens(listbox, { button_retirar}))
    
    # Botão Calcelar/Voltar
    ttk.Button(janela, text="Cancelar",   command=lambda: janela_principal(janela)).place(x=470, y=350, width=300, height=60 )
    
    # Botão Gravar
    ttk.Button(janela, text="Gravar",     command=lambda: botao_gravar(janela, controller_map_gpio, nome_arquivo)).place(x=470, y=440, width=300, height=60 )

    janela.mainloop()

#***********************************************************#
def botao_gravar(janela, controller_map_gpio, nome_arquivo):

    alteracao = nome_arquivo != None

    if alteracao:

        nome_arquivo += '.json'

        try:
            os.remove(nome_arquivo)
        except:
            showerror('Erro', 'Não foi possivel alterar mapeamento, tente mais tarde!' )
            return       
        

    else:
        nome_arquivo = controller_map_gpio.retornar_nome_arquivo_livre()    
    
    if not controller_map_gpio.gravar_COM(controller_map_gpio.COMs[0], nome_arquivo):
        showerror('Erro', 'Não foi possível gravar o Mapeamento!' )
    else:
        if alteracao:
            showinfo('Sucesso', 'Mapeamento alterado em: ' + nome_arquivo)
        else:   
            showinfo('Sucesso', 'Mapeamento gerado em: ' + nome_arquivo)

    janela_principal(janela)


#***********************************************************#
def Inicializar_mapgpio_controller(controller_map_gpio, console_logs):

    if not controller_map_gpio.inicializar_todos_componentes(): 
        showerror( 'ERRO', 'Falha na inicialização do MapGPIO_Controller!')     
        return False

    escrever_console_log(console_logs, 'Modulo MapGPIO_Controller: Inicializado')    

    return True


#***********************************************************#
def controle_selecao_lista_itens(listbox, lista_button):
    
    selection = listbox.curselection()

    for button in lista_button:
        if selection:
            button.state(['!disabled'])
        else:
            button.state(['disabled'])

#***********************************************************#
def botao_adicionar_item(listbox, combobox, console_logs, controller_map_gpio, janela, button_adicionar):     

    button_adicionar.state(['disabled'])
    escrever_console_log(console_logs, 'Inicializando leitura das GPIOs...')    

    porta_gpio_log = ''

    if combobox.get() == 'Botão':
        escrever_console_log(console_logs, 'Aperte o botão...')

        gpio = retornar_leitura_GPIO_com_atualizacao_tela(janela, controller_map_gpio)

        if gpio == 0:
            escrever_console_log(console_logs, 'Leitura de GPIO falhou!')  
            button_adicionar.state(['!disabled'])
            return  

        if controller_map_gpio.porta_gpio_ja_utilizado_mapeamento(gpio=gpio):
            escrever_console_log(console_logs, 'Leitura falhou: GPIO já utilizada!')
            button_adicionar.state(['!disabled'])
            return  
        
        controller_map_gpio.COMs[0].set_botao(gpio)   
        porta_gpio_log = ' [GPIO:' + str(gpio).zfill(2) + ']'      
        
        

    elif combobox.get() == 'Joystick':        

        direcoes = { 'CIMA':0, 'BAIXO':0, 'ESQUERDA':0, 'DIREITA':0}

        for chave in direcoes.keys():

            escrever_console_log(console_logs, 'Pressione para ' + chave + '...')

            gpio = retornar_leitura_GPIO_com_atualizacao_tela(janela, controller_map_gpio)  

            if gpio == 0:            
                escrever_console_log(console_logs, 'Leitura de GPIO falhou!')
                button_adicionar.state(['!disabled'])
                return 
            
            if controller_map_gpio.porta_gpio_ja_utilizado_mapeamento(gpio=gpio):
                escrever_console_log(console_logs, 'Leitura falhou: GPIO já utilizada!')
                button_adicionar.state(['!disabled'])
                return 


            direcoes[chave] = gpio  
            porta_gpio_log += str(gpio).zfill(2) + ','

        
        porta_gpio_log = ' [GPIO:' + porta_gpio_log[0:len(porta_gpio_log)-1] + ']'

        controller_map_gpio.COMs[0].set_joystick({'up':    direcoes['CIMA'    ],
                                                  'down':  direcoes['BAIXO'   ], 
                                                  'left':  direcoes['ESQUERDA'], 
                                                  'right': direcoes['DIREITA' ]})   

    else: # potenciometro
        escrever_console_log(console_logs, 'Mova o potenciometro para o final...')
        janela.update()
        time.sleep(6)

        porta = controller_map_gpio.retornar_porta_acionado_todos_componentes()

        if porta == None:
            escrever_console_log(console_logs, 'Leitura de PORTA falhou!')
            button_adicionar.state(['!disabled'])
            return 
        
        if controller_map_gpio.porta_gpio_ja_utilizado_mapeamento(porta=porta):
            escrever_console_log(console_logs, 'Leitura falhou: PORTA já utilizada!')
            button_adicionar.state(['!disabled'])
            return  
        
        controller_map_gpio.COMs[0].set_analogico(porta)
        porta_gpio_log = ' [PORTA: ' + str(porta).zfill(2) + ']'
    

    listbox.insert( tk.END, combobox.get() + porta_gpio_log )
    escrever_console_log(console_logs, 'Adicionou ' + combobox.get() + porta_gpio_log)
    button_adicionar.state(['!disabled'])

#***********************************************************#
def retornar_leitura_GPIO_com_atualizacao_tela(janela, controller_map_gpio):
    
    limite_tentativas = 10
    total_tentaviva   = 0
    gpio              = 0
    
    while total_tentaviva < limite_tentativas and gpio == 0:
        janela.update()
        time.sleep(1)
        gpio = controller_map_gpio.retornar_GPIO_com_input_todos_componentes()
        total_tentaviva += 1        

    return gpio

#***********************************************************#
def botao_retirar_item(listbox, console_logs, button_retirar, controller_map_gpio): 

    if len(listbox.curselection()) > 0:

        componente = listbox.get( listbox.curselection()[0] ) 

        if askquestion("Atenção", "Efetuar a retirada do " + componente + '?', icon ='warning') == 'no':
            return
        
        if componente.find("Botão") != -1 or componente.find("Joystick") != -1:
            posicao_TAG = componente.find("GPIO:")
            gpio = int(componente[posicao_TAG+5:posicao_TAG+5+2])
            controller_map_gpio.remover_item_mapeamento(gpio=gpio)
        else:
            posicao_TAG = componente.find("PORTA:")
            porta = int(componente[posicao_TAG+6:posicao_TAG+6+2])
            controller_map_gpio.remover_item_mapeamento(porta=porta)                
        
        escrever_console_log(console_logs, 'Retirou ' + listbox.get( listbox.curselection()[0] ) )
        listbox.delete(listbox.curselection()[0]) 
        button_retirar.state(['disabled'])
        
#***********************************************************#
def escrever_console_log(console_logs, log):    
    console_logs.configure(state=tk.NORMAL)
    console_logs.insert(tk.END, str(datetime.datetime.now())[0:16] + '  ' + log + '\n')
    console_logs.configure(state=tk.DISABLED)
    console_logs.see(tk.END)

#***********************************************************#
def apertou_carregar(janela_anterior):
    
    if not janela_anterior == None:
        janela_anterior.destroy()

    janela              = inicializar_modulo_tkinter()
    controller_map_gpio = MapGPIO_Controller()

    lista_arquivos = controller_map_gpio.retornar_lista_mapeamentos_pasta()    

    if len(lista_arquivos) == 0:
        showwarning('Atenção', 'Não foi encontrado nenhum mapeamento na pasta!' )
        janela_principal(janela)
        return
    
    ttk.Label(janela, text="Carregar Mapeamentos", font=( "Helvetica", 20 )).place(x=40, y= 25)

    # Lista de Itens
    ttk.Label(janela, text="Lista de Mapeamentos" , font=( "Helvetica", 12 )).place(x=60, y=160) 
    lista_itens = tk.StringVar() 
    lista_itens.set(lista_arquivos)
    scrollbar = ttk.Scrollbar( janela, orient=tk.VERTICAL)
    scrollbar.place(x=410, y=190, height=300)
    listbox = tk.Listbox( janela, listvariable=lista_itens, yscrollcommand=scrollbar.set, font=( "Helvetica", 14 ), selectmode=tk.SINGLE)          
    listbox.place(x=60, y=190, width=350, height=300 )         
    scrollbar.config(command=listbox.yview)   

    
    botao_exibir = ttk.Button(janela, text="Exibir",  command=lambda: executa_botao_exibir(listbox, lista_botoes, janela))
    botao_exibir.place(x=470, y=190, width=300, height=60 )
    botao_deletar = ttk.Button(janela, text="Deletar", command=lambda: executa_botao_delete(listbox, lista_botoes))
    botao_deletar.place(x=470, y=270, width=300, height=60 )
    botao_alterar = ttk.Button(janela, text="Alterar", command=lambda: apertou_novo_editar(janela, listbox.get( listbox.curselection()[0] )))
    botao_alterar.place(x=470, y=350, width=300, height=60 )
    ttk.Button(janela, text="Voltar",  command=lambda: janela_principal(janela)).place(x=470, y=430, width=300, height=60 )

    lista_botoes = { botao_exibir, botao_deletar, botao_alterar}

    controle_selecao_lista_itens(listbox, lista_botoes )
    listbox.bind("<<ListboxSelect>>", lambda _: controle_selecao_lista_itens(listbox, lista_botoes))


    janela.mainloop() 

#***********************************************************# 
def executa_botao_delete(listbox, lista_botoes):

    if len(listbox.curselection()) > 0:

        componente = listbox.get( listbox.curselection()[0] ) 

        if askquestion("Atenção", 'Deseja deletar o mapeamento selecionado?', icon ='warning') == 'no':
            return
        
        try:
            os.remove(componente + '.json')
        except:
            showerror('Erro', 'Não foi possivel deletar mapeamento, tente mais tarde!' )
            return
        
        listbox.delete(listbox.curselection()[0]) 

    controle_selecao_lista_itens(listbox, lista_botoes )

#***********************************************************# 
def executa_botao_exibir(listbox_anterior, lista_botoes, janela_anterior):

    controle_selecao_lista_itens(listbox_anterior, lista_botoes )
    janela_anterior.update()

    janela = inicializar_modulo_tkinter()     

    ttk.Label(janela, text="Exibir Mapeamento: " + listbox_anterior.get(listbox_anterior.curselection()[0])[0:6] , font=( "Helvetica", 20 )).place(x=40, y= 25) # [X e width=Horizontal] [y e height=Vertical]

    controller_map_gpio = MapGPIO_Controller()
    controller_map_gpio.carregar_COM(listbox_anterior.get(listbox_anterior.curselection()[0])[0:6] + '.json')      

    # Lista de Itens
    ttk.Label(janela, text="Lista de Itens" , font=( "Helvetica", 12 )).place(x=60, y=170) 
    lista_itens2 = tk.StringVar()     
    scrollbar = ttk.Scrollbar( janela, orient=tk.VERTICAL)
    scrollbar.place(x=410, y=200, height=300)
    listbox2 = tk.Listbox( janela, listvariable=lista_itens2, yscrollcommand=scrollbar.set, font=( "Helvetica", 14 ), selectmode=tk.SINGLE)          
    listbox2.place(x=60, y=200, width=350, height=300 )         
    scrollbar.config(command=listbox2.yview)  

    for item in retornar_lista_componentes_com(controller_map_gpio) :
        listbox2.insert(tk.END, item)    

    ttk.Button(janela, text="Voltar",  command= janela.destroy).place(x=470, y=430, width=300, height=60 )

    janela.mainloop() 

#***********************************************************#
def retornar_lista_componentes_com(controller_map_gpio):

    COM = controller_map_gpio.COMs[0]
    lista_componentes = []
   
    # Botoes
    if len(COM.get_lista_botoes()) > 0:        
        for botao in COM.get_lista_botoes(): 
            lista_componentes.append( 'Botão [GPIO:' + str(botao['gpio']).zfill(2) + ']')          

    # Joysticks
    if len(COM.get_lista_joysticks()) > 0:        
        for joystick in COM.get_lista_joysticks():
            lista_componentes.append( 'Joystick [GPIO:' + str(joystick['gpio']['up'   ]).zfill(2) + ',' +
                                                          str(joystick['gpio']['down' ]).zfill(2) + ',' +
                                                          str(joystick['gpio']['left' ]).zfill(2) + ',' +
                                                          str(joystick['gpio']['right']).zfill(2) + ']')         
    
    # Portas Analogicas
    if len(COM.get_lista_analogicos()) > 0:
        for analogico in COM.get_lista_analogicos():
            lista_componentes.append( 'Potenciômetro [PORTA:' + str(analogico['porta']).zfill(2) + ']')           

    return lista_componentes

#***********************************************************#
def janela_principal(janela_anterior):

    if not janela_anterior == None:
        janela_anterior.destroy()

    janela = inicializar_modulo_tkinter()    

    frame1 = ttk.Frame(janela, borderwidth=5, relief='groove' ) 
    frame1.place(x=250, y=140, width=300, height=310 )

    ttk.Label(frame1, text="Mapeamentos de GPIO", font=( "Helvetica", 14 ), ).place(x=50, y=0, width=240, height=50 )
    ttk.Button(frame1, text="Novo", command=lambda: apertou_novo_editar(janela)).place(x=25, y=60, width=240, height=50 )
    ttk.Button(frame1, text="Carregar", command=lambda: apertou_carregar(janela) ).place(x=25, y=120, width=240, height=50 )  
    ttk.Button(frame1, text="Testar GPIOs", command=lambda: apertou_carregar(janela), state=tk.DISABLED ).place(x=25, y=180, width=240, height=50 ) 
    ttk.Button(frame1, text="Sair", command=janela.destroy ).place(x=25, y=240, width=240, height=50 )
    

    janela.mainloop()


#***********************************************************#
if __name__ == "__main__":
    janela_principal(None)
    
