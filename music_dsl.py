from dataclasses import dataclass
from typing import List, Union, Optional, Type, Literal, Callable, Dict, Any, Tuple, cast
from lark import Lark, Transformer, Tree, Token
from visualization import visualize_garageband_piano_roll

#DOMINIO SEMANTICO MUSICALE
# Rappresentiamo una singola nota calcolata
@dataclass(frozen=True)
class NoteValue:
    midi_pitch: int  # C4 diventa 60, C#4 diventa 61, ecc.
    duration: float    # Durata in battiti (es. 1, 2, 4)

# Rappresentiamo un istante temporale che può contenere più note
@dataclass(frozen=True)
class MusicEvent:
    start_time: float
    notes: set[NoteValue]

# Il risultato finale della valutazione di un programma musicale è una lista di eventi ordinati nel tempo
type MusicResult = list[MusicEvent]

def note_to_midi(pitch: str, accidental: str, octave: int) -> int:
    # 1. Mappatura delle note base nell'ottava 0
    pitch_map = {
        "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11
    }
    
    # 2. Valore dell'alterazione
    accidental_map = {
        "bb": -2, "b": -1, "n": 0, "d": 1, "dd": 2
    }
    
    # 3. Calcolo del numero MIDI
    # Formula: (Ottava + 1) * 12 + ValoreNota + Alterazione
    # Usiamo (octave + 1) perché nel MIDI l'ottava 0 parte da 12, e C-1 è lo 0.
    
    base_note = pitch_map[pitch]
    modifier = accidental_map[accidental]
    
    midi_number = (octave + 1) * 12 + base_note + modifier
    
    return midi_number

def get_duration(sequence: MusicResult) -> float:
    """Calcola la durata totale di una sequenza."""
    if not sequence:
        return 0.0
    # La durata è il tempo d'inizio dell'ultimo evento + la durata della sua nota più lunga
    last_event = sequence[-1]
    max_note_duration = max((n.duration for n in last_event.notes), default=0)
    return last_event.start_time + max_note_duration

def concat_music(left: MusicResult, right: MusicResult) -> MusicResult:
    shift = get_duration(left)
    # Spostiamo tutti gli eventi della seconda sequenza in avanti
    shifted_right = [
        MusicEvent(e.start_time + shift, e.notes) 
        for e in right
    ]
    return left + shifted_right

def harmony_music(left: MusicResult, right: MusicResult) -> MusicResult:
    # Uniamo semplicemente le liste. 
    # Un vero motore musicale poi ordinerebbe per tempo, 
    # ma per ora tenerle insieme in una lista è corretto semanticamente.
    return sorted(left + right, key=lambda x: x.start_time)


#GRAMMATICA
grammar = r"""
    # Il punto di ingresso ora è un programma (sequenza di comandi)
    ?start: command_seq

    ?command_seq: command
               | command ";" command_seq

    ?command: vardecl
            | assign
            | print
            | ifelse 
            | while    
            | fundecl 
            | procdecl

    # Nuovi Comandi di Stato
    vardecl: "var" IDENTIFIER "=" expr
    assign: IDENTIFIER "<-" expr
    print: "print" expr

    # Strutture di controllo come comandi
    while: "while" expr "do" "{" command_seq "}"
    ifelse: "if" expr "then" "{" command_seq "}" "else" "{" command_seq "}"

    # Funzioni
    fundecl: "function" IDENTIFIER "(" [param_list] ")" "=" expr
    param_list: IDENTIFIER ("," IDENTIFIER)*

    # Procedure
    procdecl: "procedure" IDENTIFIER "(" [param_list] ")" "=" "{" command_seq "return" expr "}"

    # Espressioni (calcolano valori, non cambiano lo stato direttamente)
    ?ground: note | rest | NUMBER | BOOL

    ?expr: bin | mono | let | funapp | procapp
    
    ?bin: expr OP mono
    
    ?mono: ground | paren | var | unary
    


    unary: UNOP mono
    
    paren: "(" expr ")"
    var: IDENTIFIER
    let: "let" IDENTIFIER "=" expr "in" expr
    funapp: IDENTIFIER "(" [arg_list] ")"
    procapp: IDENTIFIER "(" [arg_list] ")"
    arg_list: expr ("," expr)*

    # Definizioni musicali
    note: PITCH ACCIDENTAL OCTAVE ["/" DUR]
    rest: REST_SYMBOL ["/" DUR]

    # Terminali
    PITCH.2: "C" | "D" | "E" | "F" | "G" | "A" | "B"
    ACCIDENTAL.2: "bb" | "b" | "n" | "d" | "dd"
    OCTAVE.2: /[0-9]/
    DUR.2: /[0-9]+(\.[0-9]+)?/
    REST_SYMBOL: "R"
    NUMBER: /[0-9]+/
    BOOL: "true" | "false"
    UNOP: "not" | "head" | "tail" | "is_empty" | "pitch" | "initialize"
    OP: "+" | "-" | "*" | "/" | "%" | "==" | "<" | ">" | "and" | "or" | "++" | "|" | "!"
    IDENTIFIER: /[a-z][a-zA-Z0-9_]*/

    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, start='start')

#OPERATORI
# Operatori Aritmetici (Standard)
def add(x: Any, y: Any) -> Any: return x + y
def sub(x: Any, y: Any) -> Any: return x - y

# Operatori Musicali (Specifici del dominio)
def concat(x: list[MusicEvent], y: list[MusicEvent]) -> list[MusicEvent]:
    # Qui usiamo la logica di concatenazione definita in precedenza
    return concat_music(x, y) 

def harmony(x: list[MusicEvent], y: list[MusicEvent]) -> list[MusicEvent]:
    return harmony_music(x, y)

def transpose_music(shift: int, sequence: list[MusicEvent]) -> list[MusicEvent]:
    # Shift è il numero di semitoni, sequence è la musica
    transposed = []
    for event in sequence:
        new_notes = {
            NoteValue(n.midi_pitch + shift, n.duration) 
            for n in event.notes
        }
        transposed.append(MusicEvent(event.start_time, new_notes))
    return transposed

#AST NODES
# 1. Definiamo i tipi degli operatori
type Op = Literal["+", "-", "*", "/", "%", "==", "<", ">", "++", "|"]

# 2. Definiamo i nodi dell'AST
@dataclass
class Number:
    value: int

@dataclass
class Bool:
    value: bool

@dataclass
class Var:
    name: str

@dataclass
class Note:
    pitch: str
    accidental: str
    octave: int
    duration: float

@dataclass
class Rest:
    duration: float

@dataclass
class Apply:
    op: str
    args: list[Expression]

@dataclass                # modo statico di trattare le variabili. Siamo passati a quello dinamico
class Let:
    identifier: str
    value: 'Expression'
    body: 'Expression'

#Funzioni
@dataclass
class FunctionDecl:
    name: str
    params: list[str]
    body: Expression

@dataclass
class FunctionApp:
    name: str
    args: list[Expression]

@dataclass
class Closure:
    function: FunctionDecl
    env: Environment

#Procedure
@dataclass
class ProcedureDecl:
    name: str
    params: list[str]
    body: CommandSequence
    return_expr: Expression

@dataclass
class ProcedureApp:
    name: str
    args: list[Expression]

@dataclass
class ProcedureClosure:
    procedure: ProcedureDecl
    env: Environment

type Expression = Number | Bool | Var | Note | Apply | Let | FunctionApp | ProcedureApp

#Nodi dell'AST per i comandi
@dataclass
class Assign:
    name: str
    expr: Expression

@dataclass
class Print:
    expr: Expression

@dataclass
class VarDecl:
    name: str
    expr: Expression

@dataclass
class CommandSequence:
    first: 'Command'
    rest: Optional['CommandSequence'] = None

@dataclass
class IfElse:
    condition: Expression
    then_branch: CommandSequence
    else_branch: CommandSequence

@dataclass
class While:
    cond: Expression
    body: CommandSequence

type Command = Assign | Print | VarDecl | CommandSequence | IfElse | While | FunctionDecl



#TRANSFORMER
#Transformer per espressioni
def transform_expr_tree(tree: Union[Tree, Token]) -> Expression:
    if isinstance(tree, Token):
        if tree.type == "NUMBER": return Number(int(tree.value))
        if tree.type == "BOOL": return Bool(tree.value == "true")
        if tree.type == "IDENTIFIER": return Var(str(tree.value))
        return Var(str(tree.value))

    # Ordiniamo i case per assicurarci che le note siano prese prima di var
    match tree:
        # 1. Gestione Note e pause
        case Tree(data="note", children=c):
            p, a, o = str(c[0]), str(c[1]), int(c[2])
            d = float(c[3]) if len(c) > 3 and c[3] is not None else 1 
            return Note(p, a, o, d)
        
        case Tree(data="rest", children=c):
            d = float(c[1]) if len(c) > 1 and c[1] is not None else 1
            return Rest(d)

        # 2. Ground (scende ricorsivamente verso note o token)
        case Tree(data="ground", children=[child]):
            return transform_expr_tree(child)

        # 3. Variabili (solo se non è una nota)
        case Tree(data="var", children=[Token(value=name)]):
            return Var(name=str(name))

        # ... resto dei case (bin, unary, mono, funapp, etc.) ...
        case Tree(data="mono", children=[subtree]):
            return transform_expr_tree(subtree)
        case Tree(data="unary", children=[Token(value=op), operand]):
            return Apply(op=str(op), args=[transform_expr_tree(operand)])
        case Tree(data="bin", children=[left, Token(value=op), right]):
            return Apply(op=str(op), args=[transform_expr_tree(left), transform_expr_tree(right)])
        case Tree(data="funapp", children=[Token(value=name), args_node]):
            args = [transform_expr_tree(c) for c in args_node.children] if isinstance(args_node, Tree) else ([transform_expr_tree(args_node)] if args_node else [])
            return FunctionApp(name=str(name), args=args)
        case Tree(data="procapp", children=[Token(value=name), args_node]):
            args = [transform_expr_tree(c) for c in args_node.children] if isinstance(args_node, Tree) else ([transform_expr_tree(args_node)] if args_node else [])
            return ProcedureApp(name=str(name), args=args)
        case Tree(data="paren", children=[subtree]):
            return transform_expr_tree(subtree)
        case _:
            raise ValueError(f"Struttura inattesa: {getattr(tree, 'data', tree)}")

#transformer per comandi
def transform_command_tree(tree: Tree) -> Command:
    match tree:
        case Tree(data="vardecl", children=[Token(value=name), expr_tree]):
            return VarDecl(name=str(name), expr=transform_expr_tree(expr_tree))

        case Tree(data="assign", children=[Token(value=name), expr_tree]):
            return Assign(name=str(name), expr=transform_expr_tree(expr_tree))

        case Tree(data="print", children=[expr_tree]):
            return Print(expr=transform_expr_tree(expr_tree))

        case Tree(data="ifelse", children=[cond, then_b, else_b]):
            return IfElse(
                condition=transform_expr_tree(cond),
                then_branch=ensure_command_seq(then_b),
                else_branch=ensure_command_seq(else_b)
            )

        case Tree(data="while", children=[cond, body]):
            return While(
                cond=transform_expr_tree(cond),
                body=ensure_command_seq(body)
            )
        
        case Tree(data="fundecl", children=[Token(value=name), param_list_tree, body_expr_tree]):
            # Estrazione parametri (IDENTIFIER)
            if isinstance(param_list_tree, Tree):
                params = [t.value for t in param_list_tree.children if isinstance(t, Token)]
            elif isinstance(param_list_tree, Token):
                params = [param_list_tree.value]
            else:
                params = []
            
            return FunctionDecl(
                name=str(name),
                params=params,
                body=transform_expr_tree(cast(Tree, body_expr_tree))
            )
        
        case Tree(data="procdecl", children=[Token(value=name), param_list_tree, body_tree, return_expr_tree]):
            if isinstance(param_list_tree, Tree):
                params = [t.value for t in param_list_tree.children if isinstance(t, Token)]
            elif isinstance(param_list_tree, Token):
                params = [param_list_tree.value]    
            else:
                params = []
            
            return ProcedureDecl(
                name=str(name),
                params=params,
                body=ensure_command_seq(body_tree),
                return_expr=transform_expr_tree(cast(Tree, return_expr_tree))
            )
        
        case x:
            raise ValueError(f"Comando inatteso: {x.data}")

# Funzione di utilità (trasforma in seq se necessario)
def ensure_command_seq(tree: Any) -> CommandSequence:
    # Se è già un Tree con data="command_seq", usiamo la funzione specifica
    if isinstance(tree, Tree) and tree.data == "command_seq":
        return transform_command_seq_tree(tree)
    
    # Se è un Tree di un comando (es. vardecl, assign), lo trasformiamo e lo impacchettiamo
    if isinstance(tree, Tree):
        return CommandSequence(first=transform_command_tree(tree))
    
    # Se per qualche motivo è già un oggetto Command (già trasformato)
    return CommandSequence(first=tree)

#Transformer per sequenze di comandi
def transform_command_seq_tree(tree: Tree) -> CommandSequence:

    # Sicurezza: se non è un Tree, non possiamo leggere tree.data
    if not isinstance(tree, Tree):
        raise ValueError(f"Atteso un nodo Tree, ricevuto {type(tree)}")

    match tree:
        # --- Caso ricorsivo per sequenze di comandi ---
        case Tree(data="command_seq", children=[first, rest]):
            return CommandSequence(
                first=transform_command_tree(first),
                rest=transform_command_seq_tree(rest)
            )
        
        # --- Caso base per singolo comando ---
        case Tree(data="command_seq", children=[single]):
            return CommandSequence(first=transform_command_tree(single))
        
        # --- Caso singolo comando ---
        case _ if hasattr(tree, "data") and tree.data in {
            "vardecl", "assign", "print", "ifelse", "while", "fundecl"
        }:
            return CommandSequence(first=transform_command_tree(tree))
            
        case x:
            raise ValueError(f"Sequenza comandi inattesa: {x.data}")


#PARSER
def parse_program(program_text: str) -> CommandSequence:
    """Trasforma una stringa di codice musicale in una sequenza di comandi (AST)"""
    # 1. Parsing del testo tramite Lark
    parse_tree = parser.parse(program_text)
    
    # 2. Trasformazione dell'albero Lark nel nostro AST (CommandSequence)
    return transform_command_seq_tree(parse_tree)


#COSTRUZIONE DELLO STATE
@dataclass
class State:
    # MVal è Union[int, list[MusicEvent]]
    store: Callable[[int], MVal] 
    next_loc: int

def empty_store() -> Callable[[int], MVal]:
    def store_fn(loc: int) -> MVal:
        raise ValueError(f"Location {loc} non allocata nello store")
    return store_fn

def empty_state() -> State:
    return State(store=empty_store(), next_loc=0)

def allocate(state: State, value: MVal) -> tuple[Loc, State]:
    # 1. Creiamo la locazione usando il counter attuale
    loc = Loc(state.next_loc)
    prev_store = state.store

    # 2. Creiamo una nuova funzione store (scoping funzionale)
    def new_store(l: int) -> MVal:
        if l == loc.address:
            return value
        return prev_store(l)

    # 3. Restituiamo la locazione e il NUOVO stato con counter incrementato
    return loc, State(store=new_store, next_loc=loc.address + 1)

def update(state: State, addr: int, value: MVal) -> State:
    prev_store = state.store

    def new_store(l: int) -> MVal:
        if l == addr:
            return value
        return prev_store(l)

    # Qui next_loc NON aumenta perché stiamo sovrascrivendo
    return State(store=new_store, next_loc=state.next_loc)

def access(state: State, addr: int) -> MVal:
    return state.store(addr)


#LOCAZIONI E TIPI DI VALORE
@dataclass #Dataclass per rappresentare l'indirizzo di una variabile nello stato
class Loc:
    address: int

type EVal = int | bool | list[MusicEvent] #Valori che le espressioni possono "esprimere" (musica o numeri)
type MVal = EVal  # Valori che possono essere salvati nello Store
type DVal = EVal | Operator | Loc | Closure #Tutto ciò che può essere associato a un nome nell'Environment

# Definizione della struttura di un operatore
@dataclass
class Operator:
    type: tuple[list[type], type]  # (tipi_input, tipi_output)
    fn: Callable[[list[EVal]], EVal]

# --- Operatori aritmetici --- 
def add(args):
    return args[0] + args[1]

def subtract(args):
    return args[0] - args[1]

def multiply(args):
    return args[0] * args[1]

def divide(args):
    if args[1] == 0:
        raise ValueError("Division by zero")
    return args[0] // args[1]

def modulo(args):
    if args[1] == 0:
        raise ValueError("Division by zero")
    return args[0] % args[1]

# --- Operatori di confronto e logici ---
def eq(args):
    return args[0] == args[1]

def ne(args):
    return args[0] != args[1]

def lt(args):
    return args[0] < args[1]

def gt(args):
    return args[0] > args[1]

def le(args):
    return args[0] <= args[1]

def ge(args):
    return args[0] >= args[1]

def land(args):
    if not (isinstance(args[0], bool) and isinstance(args[1], bool)):
        raise ValueError("and expects booleans")
    return args[0] and args[1]

def lor(args):
    if not (isinstance(args[0], bool) and isinstance(args[1], bool)):
        raise ValueError("or expects booleans")
    return args[0] or args[1]

def lnot(args):
    if not isinstance(args[0], bool):
        raise ValueError("not expects a boolean")
    return not args[0]

# --- Operatori Musicali ---
def concat_op(args):
    # Verifichiamo che entrambi gli argomenti siano effettivamente musica (liste)
    if not (isinstance(args[0], list) and isinstance(args[1], list)):
        raise ValueError("L'operatore ++ può essere usato solo tra due sequenze musicali.")
    return concat_music(args[0], args[1])

def harmony_op(args):
    if not (isinstance(args[0], list) and isinstance(args[1], list)):
        raise ValueError("L'operatore | può essere usato solo tra due sequenze musicali.")
    return harmony_music(args[0], args[1])

def transpose_op(args):
    # args[0] sarà il numero, args[1] sarà la musica
    if not isinstance(args[0], int):
        raise ValueError(f"La trasposizione richiede un numero, ricevuto {type(args[0]).__name__}")
    if not isinstance(args[1], list):
        raise ValueError(f"La trasposizione richiede musica, ricevuto {type(args[1]).__name__}")
    return transpose_music(args[0], args[1])

def pitch_op(args):
    melodia = args[0]
    if not isinstance(melodia, list) or len(melodia) ==0:
        raise ValueError(f"pitch operator expects a musical sequence, received {type(melodia).__name__}")
    primo_evento = melodia[0]

    if not primo_evento.notes:
        raise ValueError("Il primo evento musicale non contiene note, impossibile estrarre il pitch")
    nota_valore = list(primo_evento.notes)[0] 
    return nota_valore.midi_pitch

def initialize_music_event_op(args):
    melodia = args[0]
    if not isinstance(melodia, list) or len(melodia) ==0:
        raise ValueError(f"pitch operator expects a musical sequence, received {type(melodia).__name__}")
    
    nuova_melodia = [MusicEvent(0.0, ev.notes) for ev in melodia]
    return nuova_melodia


# --- Operatori per manipolare la lista di note ---
def op_head(args):  #Funzione per ottenere il primo elemento
    lista = args[0]
    if not lista:
        raise ValueError("head: lista vuota")
    # Restituiamo una lista contenente solo il primo MusicEvent
    return [lista[0]]

def op_tail(args):  #Funzione per otterere la coda della lista (tutti tranne il primo elemento)
    lista = args[0]
    if not lista:
        raise ValueError("tail: lista vuota")
    # Restituiamo la sottolista dal secondo elemento in poi
    return lista[1:]

def op_is_empty(args): #Funzione per controllare se la lista è finita
    lista = args[0]
    return len(lista) == 0


#COSTRUZIONE DELL'ENVIRONMENT
type Environment = Callable[[str], DVal] # Environment come Funzione

def empty_environment() -> Environment:
    def env(name: str) -> DVal:
        raise ValueError(f"Undefined identifier: {name}")
    return env

def lookup(env: Environment, name: str) -> DVal:
    return env(name)

def bind(env: Environment, name: str, value: DVal) -> Environment:
    def new_env(n: str) -> DVal:
        if n == name:
            return value
        return env(n) # Cerca ricorsivamente nell'ambiente precedente
    return new_env

def create_initial_env_state() -> tuple[Environment, State]:
    """Crea l'ambiente con operatori logici, matematici e musicali, e uno stato vuoto"""
    env = empty_environment()
    state = empty_state()

    # --- Operatori aritmetici ---
    env = bind(env, "+", Operator(([int, int], int), add))
    env = bind(env, "-", Operator(([int, int], int), subtract))
    env = bind(env, "*", Operator(([int, int], int), multiply))
    env = bind(env, "/", Operator(([int, int], int), divide))
    env = bind(env, "%", Operator(([int, int], int), modulo))

    # --- Operatori di confronto e logici ---
    env = bind(env, "==", Operator(([object, object], bool), eq))
    env = bind(env, "!=", Operator(([object, object], bool), ne))
    env = bind(env, "<", Operator(([int, int], bool), lt))
    env = bind(env, ">", Operator(([int, int], bool), gt))
    env = bind(env, "and", Operator(([bool, bool], bool), land))
    env = bind(env, "or", Operator(([bool, bool], bool), lor))
    env = bind(env, "not", Operator(([bool], bool), lnot))

    # --- Operatori Musicali ---
    env = bind(env, "++", Operator(([list, list], list), concat_op))     # Usiamo list perché le melodie sono list[MusicEvent]
    env = bind(env, "|", Operator(([list, list], list), harmony_op))
    env = bind(env, "!", Operator(([int, list], list), transpose_op))
    env = bind(env, "pitch", Operator(([list], int), pitch_op))
    env = bind(env, "initialize", Operator(([list], list), initialize_music_event_op))

    #--- Operatori per manipolare liste di note ---
    env = bind(env, "head", Operator(type=([list], list), fn=op_head))
    env = bind(env, "tail", Operator(type=([list], list), fn=op_tail))
    env = bind(env, "is_empty", Operator(type=([list], bool), fn=op_is_empty))
    return env, state


#VALUTAZIONE DELLE ESPRESSIONI
def evaluate_expr(expr: Expression, env: Environment, state: State) -> EVal:
    match expr:
        # --- Ground Musicali ---
        case Note(p, a, o, d):
            midi = note_to_midi(p, a, o)
            return [MusicEvent(0.0, {NoteValue(midi, d)})]
        
        case Rest(d):
            nv = NoteValue(midi_pitch=-1, duration=d)  # Usando -1 per rappresentare una pausa
            return [MusicEvent(0.0, {nv})]
        

        # --- Ground Aritmetici, Logici e Liste ---
        case Number(value):
            return value
        
        case Bool(value):
            return value
        
        case list(value):
            return value

        # --- Applicazione di Operatori (con Type Checking) ---
        case Apply(op, args):
            # 1. Valutazione ricorsiva degli argomenti
            arg_vals = [evaluate_expr(a, env, state) for a in args]
            
            # 2. Lookup dell'operatore
            op_val = lookup(env, op)
            if isinstance(op_val, Operator):
                expected_types, _ = op_val.type
                
                # Controllo numero argomenti
                if len(expected_types) != len(arg_vals):
                    raise ValueError(f"L'operatore '{op}' aspetta {len(expected_types)} argomenti, ricevuti {len(arg_vals)}")
                
                # Controllo dei tipi (Type Checking)
                for i, (expected, actual) in enumerate(zip(expected_types, arg_vals)):
                    # NOTA: usiamo isinstance invece di 'type is' per gestire meglio le liste musicali
                    if not isinstance(actual, expected):
                        raise ValueError(
                            f"L'operatore '{op}' (arg {i+1}) aspetta {expected.__name__}, ricevuto {type(actual).__name__}"
                        )
                
                # 3. Esecuzione della funzione dell'operatore
                return op_val.fn(arg_vals)
            
            raise ValueError(f"'{op}' non è un operatore definito")

        # --- Lookup delle Variabili ---
        case Var(name):
            try:
                dval = lookup(env, name)
                match dval:
                    # Se è un valore diretto (es. una costante o un booleano nell'env)
                    case int() | bool() | list():
                        return dval
                    # Se è una locazione, andiamo nello Stato (Store)
                    case Loc(address=addr):
                        return access(state, addr)
                    case _:
                        raise ValueError(f"La variabile '{name}' non contiene un valore accessibile")
            except ValueError as e:
                raise ValueError(f"Errore variabile '{name}': {e}")

        # --- Let (Scoping statico temporaneo) ---
        case Let(name, expr_val, body):
            val = evaluate_expr(expr_val, env, state)
            extended_env = bind(env, name, val)
            return evaluate_expr(body, extended_env, state)

        # --- Chiamata di Funzione o Procedura ---
        case FunctionApp(name, args) | ProcedureApp(name, args):
            dval = lookup(env, name)
            
            # Caso 1: È una FUNZIONE pura
            if isinstance(dval, Closure):
                closure = dval
                params = closure.function.params
                if len(args) != len(params):
                    raise ValueError(f"Funzione {name} aspetta {len(params)} argomenti, ricevuti {len(args)}")
                
                args_vals = [evaluate_expr(a, env, state) for a in args]
                new_env = closure.env
                for p, v in zip(params, args_vals):
                    new_env = bind(new_env, p, v)
                
                return evaluate_expr(closure.function.body, new_env, state)

            # Caso 2: È una PROCEDURA (con comandi e return)
            elif isinstance(dval, ProcedureClosure):
                closure = dval
                params = closure.procedure.params
                if len(args) != len(params):
                    raise ValueError(f"Procedura {name} aspetta {len(params)} argomenti, ricevuti {len(args)}")

                args_vals = [evaluate_expr(a, env, state) for a in args]
                new_env = closure.env
                for p, v in zip(params, args_vals):
                    new_env = bind(new_env, p, v)

                # Eseguiamo i comandi che modificano lo stato
                updated_env, updated_state = execute_command_seq(closure.procedure.body, new_env, state)
                
                # Valutiamo il return col nuovo stato
                return evaluate_expr(closure.procedure.return_expr, updated_env, updated_state)
            
            else:
                raise ValueError(f"'{name}' non è né una funzione né una procedura")
        case _:
            raise ValueError(f"Tipo di espressione inatteso: {expr}")
        
        
#ESECUZIONE DEI COMANDI
def execute_command(
    cmd: Command, env: Environment, state: State
) -> tuple[Environment, State]:
    match cmd:
        case VarDecl(name, expr):
            value = evaluate_expr(expr, env, state)
            loc, state1 = allocate(state, value)
            new_env = bind(env, name, loc)
            return new_env, state1

        case Assign(name, expr):
            try:
                dval = lookup(env, name)
                match dval:
                    case Loc(address=addr):
                        value = evaluate_expr(expr, env, state)
                        state1 = update(state, addr, value)
                        return env, state1
                    case _:
                        raise ValueError(f"'{name}' non è una variabile assegnabile")
            except ValueError:
                raise ValueError(f"Variabile non dichiarata: '{name}'")

        case Print(expr):
            value = evaluate_expr(expr, env, state)
            # Personalizzazione per la musica
            if isinstance(value, list):
                print(f"🎨 Generazione Piano Roll per {len(value)} eventi...")
                # Chiamiamo la funzione dal file visualizer.py
                visualize_garageband_piano_roll(value)
            else:
                print(value)
            return env, state

        case IfElse(cond, then_branch, else_branch):
            cond_val = evaluate_expr(cond, env, state)
            if not isinstance(cond_val, bool):
                raise ValueError("La condizione dell'If deve essere un booleano")
            
            saved_next_loc = state.next_loc
            if cond_val:
                _, state1 = execute_command_seq(then_branch, env, state)
            else:
                _, state1 = execute_command_seq(else_branch, env, state)
            
            # Ripristino next_loc (scoping locale del blocco)
            return env, State(store=state1.store, next_loc=saved_next_loc)

        case While(cond, body):
            def rec_fn(env_curr: Environment, state_curr: State) -> tuple[Environment, State]:
                cond_val = evaluate_expr(cond, env_curr, state_curr)
                if not isinstance(cond_val, bool):
                    raise ValueError("La condizione del While deve essere un booleano")
                
                saved_next_loc = state_curr.next_loc
                if cond_val:
                    # Eseguiamo il corpo
                    _, state1 = execute_command_seq(body, env_curr, state_curr)
                    # Puliamo la memoria locale del corpo e ripetiamo
                    state2 = State(store=state1.store, next_loc=saved_next_loc)
                    return rec_fn(env_curr, state2)
                else:
                    return env_curr, state_curr
            
            return rec_fn(env, state)
        
        case FunctionDecl(name, _, _):
            closure = Closure(function=cmd, env=env)
            new_env = bind(env, name, closure)
            return new_env, state
        
        case ProcedureDecl(name, _, _, _):
            closure = ProcedureClosure(procedure=cmd, env=env)
            new_env = bind(env, name, closure)
            return new_env, state
        
        case _:
            raise ValueError(f"Comando sconosciuto: {cmd}")

def execute_command_seq(
    seq: CommandSequence, env: Environment, state: State
) -> tuple[Environment, State]:
    # Eseguiamo il primo comando
    env1, state1 = execute_command(seq.first, env, state)

    # Se ci sono altri comandi nella sequenza, procediamo ricorsivamente
    if seq.rest:
        return execute_command_seq(seq.rest, env1, state1)

    return env1, state1

def execute_program(program_text: str) -> tuple[Environment, State]:
    """
    Legge il codice sorgente, crea l'AST e lo esegue partendo
    da un ambiente e uno stato iniziali.
    """
    # 1. Parsing: Trasforma il testo in un AST di comandi (CommandSequence)
    command_seq = parse_program(program_text) 
    
    # 2. Setup: Crea l'ambiente con gli operatori e lo store vuoto
    env, state = create_initial_env_state()
    
    # 3. Execution: Avvia la catena di esecuzione
    # Restituisce la coppia (Ambiente Finale, Stato Finale)
    return execute_command_seq(command_seq, env, state)

