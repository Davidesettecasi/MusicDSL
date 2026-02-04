from music_dsl import execute_program

# --- ESEMPIO 1: Funzione per generare la scala maggiore con pause ---
prog_scale = """
procedure major_scale(start_note) = {
    var n = start_note;
    var scale = n ++ R/0.5;
    var i = 0;

    while (i < 7) do {
        if (i == 2) or (i == 6) then { n <- 1 ! n} else { n <- 2 ! n};
        scale <- scale ++ n ++ R/0.5;
        i <- i + 1
    }

    return scale
};

var my_scale = major_scale(Cn4/1);
print my_scale
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
    run_test("GENERATORE DI SCALE", prog_scale)