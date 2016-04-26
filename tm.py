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

  # creem clasa TuringMachine
    class TuringMachine(threading.Thread):
      
  # metoda constructor
    [program] = TuringProgram ce va fi folosit pentru aceasta masina
    [speed] = viteza cu care vom simula programul (in numar de pasi per secunda)/ in cazul in care vom avea o viteza de "-1", simularea va avea loc in timp real
    [listener] = o functie care va fi apelata dupa fiecare pas, folosita pentru a arata simularea. Va primi urmatoarele argumente:
                 [tm] = masina turing care va apela functia
                 [step] = un umar ce specifica ultimul tip de pas facut de (STEP_READ, STEP_WRITE, STEP_MOVE, sau STEP_STATE pentru schimbari de stare)
                 
    def __init__(self, program=None, speed=4, listener=None):
        threading.Thread.__init__(self)
        
        self.program = program
        self.speed = speed
        self.listener = listener
        
        self.should_continue = threading.Event() # permite sa punem pauza simularii
                                                 # folosim clear() pentru pauza si set() pentru continuare
                                                 
  # metoda principala a masinii, care manevreaza intreaga simulare
  
    def run(self):
        if self.program == None: raise RuntimeError("No program specified")

        #pregateste o lista pentru a putea stoca pozitiile curente ale fiecarei benzi
        #si apoi sa le umple cu pozitia initiala, 0
        self.tapes_pos = list()                   
        for i in range(len(self.program.tapes)):
            self.tapes_pos.append(0)

        # se asigura ca toate benzile au cel putin o valoare, pentru a preveni diverse probleme la citire/scriere
        for tape in self.program.tapes:
            if len(tape) == 0:
                tape.append(self.program.symbol_blank)

        self.current_state = self.program.state_initial
        self.current_action = None
        self.running = True
        self.should_continue.set() 
        
        # bucla principala. ruleaza un ciclu Turing standard (citeste, scrie, muta, schimba starea) pana cand intalneste starea finala a programului
        while self.running:
            self.should_continue.wait()  #daca punem pauza masinii (prin should_continue.clear()),
                                         #se va bloca pana cand se reia (should_continue.set())
            self.read_step()
            self.post_step(STEP_READ)

            self.should_continue.wait()
            self.write_step()
            self.post_step(STEP_WRITE)

            self.should_continue.wait()
            self.move_step()
            self.post_step(STEP_MOVE)

            self.should_continue.wait()
            self.state_change_step()
            self.post_step(STEP_STATE)
            
  # ruleaza dupa fiecare pas al simularii. apeleaza listener pentru a notifica schimbarile, ridica o eroare, 
    daca una va intalni ultimul pas, apoi va fi in repaus pentru o secunda, pentru ca utilizatorul sa poata urmari simularea
      
      def post_step(self, step_type):
        if self.listener != None:
            self.listener(self, step_type)
            
  # setam erorile folosind self.error in loc de a le creste direct numarandu-le in ordine pentru a permite ascultatorului
    de a trata eroarea in sine deoarece, de altfelnu ar sti despre o eroare aparuta intr-un alt 
    if hasattr(self, 'error'):
            raise RuntimeError(self.error)
    
        if self.speed != -1:
            time.sleep(1/float(self.speed))
 
 # În etapa de citire, aparatul citește valoarea curentă din fiecare bandă, iar apoi se utilizează aceste valori și starea
 curentă a mașinii pentru a căuta o acțiune corespunzătoare în lista programului
 
   def read_step(self):
        read_values = []
        for tape_nr, tape in enumerate(self.program.tapes): 
            read_values.append(tape[self.tapes_pos[tape_nr]]) 
            
        self.current_action = self.program.get_action(self.current_state, read_values)
        if self.current_action == None:
            self.error = "nici o actiune nu este definita pentru starea '%(state)s' si valorile (%(read)s)" \
                         % dict(state=self.current_state, read=','.join(read_values))
            self.running = False
            
  # scrie valori pe fiecare banda, dictate de catre actiunea curenta a programului
    def write_step(self):
        for tape_nr, tape in enumerate(self.program.tapes):
              tape[self.tapes_pos[tape_nr]] = self.current_action['write_values'][tape_nr]
              
# muta fiecare banda conform cu starea curenta a actiunii
   
   def move_step(self):
        for tape_nr, tape in enumerate(self.program.tapes):
            direction = self.current_action['directions'][tape_nr]
            if direction == self.program.dir_left:
                if self.tapes_pos[tape_nr] <= 0:
                    # daca atingem marginea stanga, introducem o noua valoare 
                    tape.insert(0, self.program.symbol_blank)
                    # si ne asiguram ca pozitia este la noua margine 0
                    self.tapes_pos[tape_nr] = 0                
                else: 
                    self.tapes_pos[tape_nr] -= 1
            elif direction == self.program.dir_right: 
                self.tapes_pos[tape_nr] += 1
                if self.tapes_pos[tape_nr] >= len(tape):
                    #daca atingem marginea corecta, introducem o noua valoare
                    tape.append(self.program.symbol_blank)
            #daca nu: directia este  [dir_none]
            
  # Modifică starea aparatului la cel specificat de acțiunile curente [next_state]
  
    def state_change_step(self):
        self.current_state = self.current_action['next_state']
        if self.current_state == self.program.state_final:
            self.running = False
            
 # cod test
    if __name__ == "__main__":
    tape = "0100101"
    print("Initial value: "+tape)
    
    inversion = TuringProgram("Inversion")
    inversion.set_tapes(list(tape))
    inversion.set_actions("""init 0 1 > init
                             init 1 0 > init
                             init _ _ - halt""")

    def print_tapes(tm, step_type):
        if step_type == STEP_READ:
            tcopy = list(tm.program.tapes[0])
            pos = tm.tapes_pos[0]
            tcopy.insert(pos, '[')
            tcopy.insert(pos+2, ']')
            print(''.join(tcopy))
        elif step_type == STEP_STATE and not tm.running:
            print("Final value (trimmed): " + (''.join(tm.program.tapes[0])).strip('_'))
            
    machine = TuringMachine(inversion, listener=print_tapes)
    machine.start()
    machine.join()
