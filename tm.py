import threading
import time

# STEP_ este utilizat pentru a specifica pasul curent in simularea masinii Turing
STEP_READ = 0
STEP_WRITE = 1
STEP_MOVE = 2
STEP_STATE = 3

# clasa ne ajuta la definirea programului masinii Turing (aflabet, stari speciale, simboluri)
class TuringProgram:

  # metoda constructor(defineste programul)
  
   def __init__(self, name):
        self.name = name

        # valori initiale
        self.input_values = "01"     # un string pentru care fiecare caracter reprezinta o valoare
        self.symbol_blank = '_'      # caracter/simbol 
        self.dir_left = '<'          # mutare pointer la stanga
        self.dir_right = '>'         # mutare pointer la dreapta
        self.dir_none = '-'          # nu schimbam pozitia
        self.state_initial = 'init'  # starea in care masina porneste
        self.state_final = 'halt'    # starea in care masina s-a oprit din rulat

        self.tapes = list()          # lista benzilor folosite in program. fiecare banda este o lista de caractere
                                    
        self.actions = list()        # programul in sine,denumit ca o lista de actiuni
        
  # definim alfabetul utilizat de catre programul nostru, cu alte cuvinte, lista de valori acceptate de catre benzile folosite.
   
    def set_alphabet(self, input_values, blank):
        self.input_values = input_values
        self.symbol_blank = blank
        
  #  definim simbolurile folosite la mutarea instructiunilor (left, right, none)
    
    def set_directions(self, left, right, none):
        self.dir_left = left
        self.dir_right = right
        self.dir_none = none
        
  # scurtatura pentru setarea starii finale si initiale
  
    def set_limit_states(self, initial, final):
        self.state_initial = initial
        self.state_final = final
        
  # scurtatura pentru adaugare de benzi (folosim *arg  deoarece nu suntem siguri prin cate argumente poate trece functia noastra)
  
    def set_tapes(self, *arg):
        self.tapes = list(arg)
        
  # adăugam o singură acțiune la program. in cazul în care starea curentă a mașinii este cea specificată de [state], iar valoarea 
  pe care o citește din fiecare bandă corespunde cu valoarea din [read_values], se vor înlocui aceste valori cu cele 
  din [write_values], apoi vom muta benzile conform [direction] și în cele din urmă vom schimba starea aparatului in [next_state].
  
    def add_action(self, state, read_values, write_values, directions, next_state):
        self.actions.append(dict(id=len(self.actions),
                                 state=state,
                                 read_values=read_values,
                                 write_values=write_values,
                                 directions=directions,
                                 next_state=next_state))
                                 
  # setam toate actiunile ce le vom utiliza, folosind o lista de tip string
     
    def set_actions(self, table):
        self.actions = list()
        for line in table.split('\n'):
            columns = line.split()
            
            state = columns[0]
            
            #avand mai multe benzi, coloanele vor avea valori multiple, separate prin virgule
            read_values = columns[1].split(',')
            write_values = columns[2].split(',')
            directions = columns[3].split(',')
            
            next_state = columns[4]
            
            self.add_action(state, read_values, write_values, directions, next_state)
            
  # cautam actiuni in lista, bazate pe [state] si [read_values]
  
    def get_action(self, state, read_values):
        for action_id, action in enumerate(self.actions):
            if action['state'] == state and action['read_values'] == read_values:
                return action
        return None
