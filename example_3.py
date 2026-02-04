from music_dsl import execute_program


# --- ESEMPIO 3: Canone musicale ---
# Il seguente programma genera un canone a quattro voci. La prima voce è una melodia semplice,
# la seconda voce è la voce1 traslata di una terza. Per traslare di una terza in maniera diatonica,
# dobbiamo controllare che ogni nota traslata appartenga alla scala maggiore di Do (la tonalità della voce1).
# Per questo motivo è stata definita la funzione is_in_scale ed è stata utilizzata all'interno della funzione
# trasponi_melodia_diatonica. La terza voce è la voce1 suonata al contrario, ottenuta grazie alla funzione reverse_melody.
# Infine, il basso accompagna le tre voci evidenziando le toniche degli accordi di Do e di Sol, su cui la voce1 si muove.

prog_canone = """
procedure genera_voce() = {
    var b1 = Cn4/2 ++ En4/1 ++ Gn4/1;
    var b2 = Dn4/1 ++ Fn4/2 ++ Gn4/1;
    var b3 = En4/1 ++ Gn4/1 ++ Cn5/1 ++ Gn4/1;
    var b4 = Dn4/1 ++ Bn3/1 ++ Gn4/2
    return b1 ++ b2 ++ b3 ++ b4
};

procedure is_in_scale(nota, scala) = {
    var b = is_empty scala;
    var corrente = scala;
    var trovato = false;

    while (not b) do {
        var nota_scala = head corrente;
        if (pitch nota == pitch nota_scala) or (pitch nota == (pitch nota_scala + 12)) then { trovato <- true } else {
        trovato <- trovato };
        corrente <- tail corrente;
        b <- is_empty corrente
    }

    return trovato
};


procedure major_scale(start_note) = {
    var n = start_note;
    var scale = n;
    var i = 0;

    while (i < 7) do {
        if (i == 2) or (i == 6) then { n <- 1 ! n} else { n <- 2 ! n};
        scale <- scale ++ n;
        i <- i + 1
    }

    return scale
};

procedure trasponi_melodia_diatonica(melodia, semitoni, scala) = {
    var x = head melodia;
    var risultato = semitoni ! x;
    if (is_in_scale(risultato, scala)) then {
        risultato <- risultato} else {
        risultato <- (0 - 1) ! risultato
    };
    var corrente = tail melodia;
    var b = is_empty corrente;

    while (not b) do {
        var nota = head corrente;
        var nota_trasposta = semitoni ! nota;
        if (is_in_scale(nota_trasposta, scala)) then {
            nota_trasposta <- nota_trasposta} else {
            nota_trasposta <- (0 - 1) ! nota_trasposta
        };
        risultato <- risultato | nota_trasposta;
        corrente <- tail corrente;
        b <- is_empty corrente
    }

    return risultato
};

procedure reverse_melody(melodia) = {
    var risultato = head melodia;
    var corrente = tail melodia;
    var b = is_empty corrente;

    while (not b) do {
        var nota = head corrente;
        nota <- initialize nota;
        risultato <- nota ++ risultato;
        corrente <- tail corrente;
        b <- is_empty corrente
    }

    return risultato
};

var voce1 = genera_voce();
var scala = major_scale(Cn4/1);

var basso = Cn2/4 ++ Gn2/4 ++ Cn2/4 ++ Gn2/4;

var voce2 = trasponi_melodia_diatonica(voce1, 4, scala);


var voce3 = reverse_melody(voce1);

voce1 <- voce1 ++ voce1 ++ voce1;
voce2 <- R/24 ++ voce2;
voce3 <- R/16 ++ voce3 ++ voce3;
basso <- basso ++ basso ++ basso;

var canone = voce1 | voce2 | voce3 | basso;
print canone
"""

def run_test(name, code):
    print(f"\n{'='*20}")
    print(f"ESECUZIONE: {name}")
    print(f"{'='*20}")
    try:
        execute_program(code)
    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")

if __name__ == "__main__":
    run_test("CANONE MUSICALE", prog_canone)