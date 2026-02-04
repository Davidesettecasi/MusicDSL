import webbrowser
import os
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class NoteValue:
    midi_pitch: int
    duration: int

@dataclass(frozen=True)
class MusicEvent:
    start_time: float
    notes: set[NoteValue]

def get_duration(sequence):
    if not sequence: return 0.0
    last_event = sequence[-1]
    max_note_dur = max(n.duration for n in last_event.notes) if last_event.notes else 0
    return last_event.start_time + max_note_dur

def visualize_garageband_piano_roll(music, filename="piano_roll_pro.html"):
    if not music: return

    all_events = sorted(music, key=lambda x: x.start_time)
    
    # PARAMETRI CHIAVE
    CELL_WIDTH = 50
    CELL_HEIGHT = 20 # Questa è l'altezza di una riga della griglia (semitono)
    KEYBOARD_WIDTH = 100 
    
    all_pitches = sorted(list({n.midi_pitch for e in all_events for n in e.notes}))
    min_p = max(0, min(all_pitches) - 4) if all_pitches else 60
    max_p = min(127, max(all_pitches) + 4) if all_pitches else 72

    total_duration = get_duration(all_events)
    svg_width = int(total_duration * CELL_WIDTH) + 100
    svg_height = (max_p - min_p + 1) * CELL_HEIGHT
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # --- GENERAZIONE TASTIERA ---
    keyboard_html = f'<div class="piano-keyboard" style="width: {KEYBOARD_WIDTH}px; height: {svg_height}px;">'
    
    for p in range(max_p, min_p - 1, -1):
        name = note_names[p % 12]
        is_black = "#" in name
        top_offset = (max_p - p) * CELL_HEIGHT
        
        if is_black:
            # TASTO NERO: Sta esattamente sulla sua riga della griglia
            keyboard_html += f'<div class="key black-key" style="top:{top_offset}px; height:{CELL_HEIGHT}px;"></div>'
        else:
            # TASTO BIANCO: Deve espandersi per coprire i bordi
            # Calcoliamo quanto deve essere alto per toccare il bianco successivo
            # coprendo le mezze righe dei tasti neri
            
            # Di base il tasto bianco copre la sua riga
            y_start = top_offset
            height = CELL_HEIGHT
            
            # Se la nota SOPRA (p+1) è nera, il bianco si allunga in su di metà riga
            if p + 1 <= max_p and "#" in note_names[(p + 1) % 12]:
                y_start -= (CELL_HEIGHT / 2)
                height += (CELL_HEIGHT / 2)
                
            # Se la nota SOTTO (p-1) è nera, il bianco si allunga in giù di metà riga
            if p - 1 >= min_p and "#" in note_names[(p - 1) % 12]:
                height += (CELL_HEIGHT / 2)
            
            label = f"{name}{(p // 12) - 1}" if name == "C" else ""
            
            keyboard_html += f'''
            <div class="key white-key" style="top:{y_start}px; height:{height}px; z-index:1;">
                <span>{label}</span>
            </div>'''
            
    keyboard_html += '</div>'

    # --- GENERAZIONE SVG (GRIGLIA CON RIGHE PER OGNI NOTA) ---
    svg_content = f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">'
    
    # Sfondo e Righe Orizzontali
    for p in range(min_p, max_p + 1):
        y = (max_p - p) * CELL_HEIGHT
        is_black_row = "#" in note_names[p % 12]
        # Colore riga: nero profondo per tasti neri, grigio scuro per bianchi
        fill = "#181818" if is_black_row else "#222"
        svg_content += f'<rect x="0" y="{y}" width="{svg_width}" height="{CELL_HEIGHT}" fill="{fill}" stroke="#111" stroke-width="0.5" />'

    # Linee Verticali (Battute)
    for t in range(int(total_duration) + 2):
        x = t * CELL_WIDTH
        svg_content += f'<line x1="{x}" y1="0" x2="{x}" y2="{svg_height}" stroke="#333" stroke-width="{"1.5" if t%4==0 else "0.5"}" />'

    # Note (Verdi stile GarageBand)
    for event in all_events:
        for note in event.notes:
            x, y = event.start_time * CELL_WIDTH, (max_p - note.midi_pitch) * CELL_HEIGHT
            svg_content += f'<rect x="{x}" y="{y+1}" width="{note.duration * CELL_WIDTH - 2}" height="{CELL_HEIGHT-2}" rx="2" fill="#63ad4d" stroke="#fff" stroke-width="0.5" />'
    
    svg_content += '</svg>'

    # --- PREPARAZIONE DATI PER IL PLAYER ---
    notes_data = []
    for event in all_events:
        for note in event.notes:
            notes_data.append({
                "time": float(event.start_time),
                "pitch": int(note.midi_pitch),
                "duration": float(note.duration)
            })
    
    # Trasformiamo la lista Python in una stringa JSON per JavaScript
    json_notes = json.dumps(notes_data)

    # --- CSS E JAVASCRIPT AGGIORNATI ---
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Piano Roll Pro Player</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
        <style>
            body {{ background: #121212; color: #eee; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 30px; }}
            .container {{ display: flex; border: 2px solid #444; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.8); border-radius: 8px; }}
            .piano-keyboard {{ position: relative; background: #000; border-right: 2px solid #333; }}
            .key {{ position: absolute; left: 0; box-sizing: border-box; width: 100%; }}
            .white-key {{ background: linear-gradient(to right, #eee 0%, #fff 100%); border-bottom: 1px solid #ccc; z-index: 1; }}
            .black-key {{ width: 65%; background: linear-gradient(to right, #333 0%, #000 100%); z-index: 2; border-radius: 0 3px 3px 0; border-bottom: 1px solid #000; }}
            .white-key span {{ position: absolute; bottom: 5px; left: 5px; color: #999; font-size: 10px; text-transform: uppercase; }}
            .scroll-area {{ overflow-x: auto; background: #1a1a1a; }}
            
            .controls {{ display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }}
            .play-button {{ 
                background: #63ad4d; color: white; border: none; padding: 15px 40px; 
                font-size: 18px; cursor: pointer; border-radius: 50px;
                font-weight: bold; transition: all 0.3s; box-shadow: 0 4px 15px rgba(99,173,77,0.3);
            }}
            .play-button:disabled {{ background: #444; cursor: not-allowed; opacity: 0.6; }}
            .play-button:hover:not(:disabled) {{ background: #76c05f; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(99,173,77,0.4); }}
            .status {{ font-size: 14px; color: #888; }}
        </style>
    </head>
    <body>
        <h1>Interactive Piano Roll</h1>
        
        <div class="controls">
            <button id="btn-play" class="play-button" onclick="startAudio()" disabled>CARICAMENTO PIANOFORTE...</button>
            <div id="status" class="status">Download campioni in corso...</div>
        </div>

        <div class="container">
            {keyboard_html}
            <div class="scroll-area">{svg_content}</div>
        </div>

        <script>
            const myNotes = {json_notes};
            let piano;

            // Inizializzazione immediata del campionatore
            const initSampler = () => {{
                // Creiamo un effetto riverbero per dare profondità
                const reverb = new Tone.Reverb({{
                    decay: 2.5,
                    wet: 0.3
                }}).toDestination();

                piano = new Tone.Sampler({{
                    urls: {{
                        A0: "A0.mp3", C1: "C1.mp3", "D#1": "Ds1.mp3", "F#1": "Fs1.mp3",
                        A1: "A1.mp3", C2: "C2.mp3", "D#2": "Ds2.mp3", "F#2": "Fs2.mp3",
                        A2: "A2.mp3", C3: "C3.mp3", "D#3": "Ds3.mp3", "F#3": "Fs3.mp3",
                        A3: "A3.mp3", C4: "C4.mp3", "D#4": "Ds4.mp3", "F#4": "Fs4.mp3",
                        A4: "A4.mp3", C5: "C5.mp3", "D#5": "Ds5.mp3", "F#5": "Fs5.mp3",
                        A5: "A5.mp3", C6: "C6.mp3", "D#6": "Ds6.mp3", "F#6": "Fs6.mp3",
                        A6: "A6.mp3", C7: "C7.mp3", "D#7": "Ds7.mp3", "F#7": "Fs7.mp3",
                        A7: "A7.mp3", C8: "C8.mp3"
                    }},
                    release: 1.2,
                    baseUrl: "https://tonejs.github.io/audio/salamander/",
                    onload: () => {{
                        document.getElementById('btn-play').disabled = false;
                        document.getElementById('btn-play').innerText = "▶ RIPRODUCI";
                        document.getElementById('status').innerText = "Pianoforte pronto.";
                    }}
                }}).connect(reverb);
            }};

            initSampler();

            async function startAudio() {{
                await Tone.start();
                const now = Tone.now() + 0.1;
                const bpm_factor = 0.5;

                myNotes.forEach(n => {{
                    if (n.pitch >= 0) {{
                        const freq = Tone.Frequency(n.pitch, "midi");
                        piano.triggerAttackRelease(
                            freq, 
                            n.duration * bpm_factor, 
                            now + n.time * bpm_factor
                        );
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f: f.write(html_template)
    webbrowser.open('file://' + os.path.realpath(filename))

