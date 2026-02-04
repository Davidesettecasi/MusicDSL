from music_dsl import execute_program

# --- ESEMPIO 2: Armonizzazione con accordi di Fra Martino ---

prog_fra_martino = """
procedure fra_martino() = {
    var f1 = Cn4/1 ++ Dn4/1 ++ En4/1 ++ Cn4/1;
    var frase1 = f1 ++ f1;

    var f2 = En4/1 ++ Fn4/1 ++ Gn4/2;
    var frase2 = f2 ++ f2;

    var f3 = Gn4/0.5 ++ An4/0.5 ++ Gn4/0.5 ++ Fn4/0.5 ++ En4/1 ++ Cn4/1;
    var frase3 = f3 ++ f3;

    var f4 = Dn4/1 ++ Gn3/1 ++ Cn4/2;
    var frase4 = f4 ++ f4

    return frase1 ++ frase2 ++ frase3 ++ frase4
};

var melodia = fra_martino();
var cmaj9 = Cn2/4 | En3/4 | Gn3/4 | Bn3/4 | Dn4/4;
var a7b13 = Cd2/4 | An2/4 | Gn3/4 | Fn4/4;
var dm9 = Dn2/4 | Fn3/4 | An3/4 | Cn4/4 | En4/4;
var g13b9 = Gn2/4 | Bn2/4 | Fn3/4 | Ab3/4 | En4/4;
var em7 = En2/2 | Gn3/2 | Bn3/2 | Dn4/2;
var ebdim7 = Eb2/2 | Gb3/2 | Ab3/2 | Cn4/2;
var db7d11 = Db2/2 | Fn3/2 | Ab3/2 | Cb4/2 | Gn4/2;
var fastdm9 = Dn2/2 | Fn3/2 | An3/2 | Cn4/2 | En4/2;
var fmaj7d11 = Fn2/4 | An2/4 | Cn3/4 | En3/4 | Bn3/4;
var g13sus4 = Gn2/2 | Cn3/2 | Fn3/2 | An3/2 | En4/2;
var c69 = Cn2/2 | Gn2/2 | En3/2 | An3/2 | Dn4/2;


melodia <- 12 ! melodia;
var chord_progression = cmaj9 ++ a7b13 ++ dm9 ++ g13b9 ++ em7 ++ ebdim7 ++ fastdm9 ++ db7d11 
    ++ fmaj7d11 ++ g13sus4 ++ c69;

var music = melodia | chord_progression;

print music
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
    run_test("FRA MARTINO JAZZ", prog_fra_martino)