# MusicDSL
MusicDSL: A domain-specific language built with Python and Lark for algorithmic musical composition, featuring a custom temporal engine and interactive web-based rendering.

# MusicDSL 🎵
> **A Domain-Specific Language for Algorithmic Composition and Music Theory Manipulation.**

## 1. Introduction
**MusicDSL** is a domain-specific programming language designed to model, manipulate, and generate musical structures through symbolic logic. The project aims to provide a programmatic abstraction of music theory, treating composition not just as a creative process, but as a series of algebraic transformations on temporal sequences.

### 1.1 Project Goals
- **Musical Abstraction**: Providing an intuitive syntax for defining notes, durations, and accidentals.
- **Temporal Manipulation**: Implementing an engine capable of correctly managing the concatenation and overlapping of events, ensuring timing integrity even in the presence of rests (silences).
- **Algorithmic Flexibility**: Supporting procedures and variables to enable generative composition (e.g., automatic scale calculation or accompaniment generation).

### 1.2 Execution Pipeline: From Text to Music
The execution of a program written in **MusicDSL** follows a three-stage process managed entirely within a Python environment:

1.  **Syntactic Analysis (Parsing) with Lark**: The source code is analyzed by the `Lark` library. It uses a formal grammar (defined in EBNF format) to validate the syntax and transform text strings into an **Abstract Syntax Tree (AST)**.
2.  **Transformation and Evaluation (Transformer)**: A `Transformer` component traverses the AST and converts abstract nodes into real Python objects (e.g., instantiating a `Note` class or executing temporal logic for the `++` operator).
3.  **Output Generation**: The final result is a `MusicResult` structure (a list of events). This list is serialized into JSON and passed to a web back-end for sound reproduction and graphical visualization.



---

## 2. Semantic Domain
The language translates source code expressions into a structured data model defined by three main entities:

### 2.1 NoteValue (The Sonic Atom)
The `NoteValue` is the minimum unit of sound information.
- `midi_pitch (int)`: The note frequency in MIDI standard (e.g., 60 for Middle C). Rests are conventionally modeled with a value of `-1`.
- `duration (float)`: The relative duration of the note (e.g., 1.0 for a whole note, 0.25 for a quarter note).

### 2.2 MusicEvent (The Temporal Container)
The `MusicEvent` represents a specific "trigger point" on the timeline.
- `start_time (float)`: The exact moment the event begins relative to the start of the composition.
- `notes (set[NoteValue])`: A set of notes starting simultaneously. Using a `set` allows for native **polyphony** (chords).

### 2.3 MusicResult (The Time Series)
The `MusicResult` (defined as `list[MusicEvent]`) is the final output representing the entire composition.

---

## 3. Syntax and Language Structure
Every instruction in **MusicDSL** is an expression that produces a `MusicResult`.

### 3.1 Musical Primitives (Atoms)
- **Notes**: Defined by the triad `Note-Accidental-Octave` followed by duration.
  - *Syntax*: `[PITCH][ACCIDENTAL][OCTAVE]/[DUR]` (e.g., `Cn4/1`)
- **Rests**: Represented by the symbol `R` followed by duration.
  - *Syntax*: `R/[DUR]` (e.g., `R/0.5`)

### 3.2 Temporal and Algebraic Operators
- `++` (**Concatenation**): Joins two sequences in chronological order.
- `|` (**Union**): Overlaps two sequences simultaneously.
- `!` (**Transposition**): Raises or lowers the pitch of a sequence.

### 3.3 Unary Operations and Sequence Manipulation
- `head(list)`: Returns the first `MusicEvent` of a sequence.
- `tail(list)`: Returns the sequence excluding the first element.
- `is_empty(list)`: Returns `true` if the sequence contains no events.
- `pitch(event)`: Extracts the MIDI value of the first note in an event.
- `initialize(event)`: Resets the `start_time` of an event to `0.0`.

### 3.4 Arithmetic and Boolean Constructs
The language supports standard types like **integers** and **booleans**.
- **Arithmetic**: `+`, `-`, `*`, `/`, `%` are used to manipulate pitches or durations.
- **Logic**: Comparison operators (`==`, `!=`, `<`, `>`, etc.) and boolean operators (`and`, `or`, `not`) handle conditions for `while` loops and `if` constructs.

### 3.5 Variable Management and Scoping
- **A. `let` Expressions (Static Scoping)**: Used for local variables that exist only within the defined block.
  - *Syntax*: `let var_name = expression in block_expression`
- **B. Declaration and Assignment (Commands)**: Global variables that persist in the environment.
  - *Declaration*: `var melodia = Cn4/1;`
  - *Assignment*: `melodia = melodia ++ En4/1;`

### 3.6 Commands and Execution Flow
- `var`: Introduces a new identifier.
- `assignment`: Updates an existing variable.
- `print`: Displays the result in the Python console (essential for debugging).
- `if-then-else`: Conditional execution based on a boolean value.
- `while`: Repeatedly executes a block of commands as long as the condition is `true`.
- `;` (**Sequencing**): Used to group and execute multiple commands in order.

### 3.7 Functions and Procedures
The language distinguishes between functional and imperative paradigms:
- **Functions**: Bodies contain only **expressions**. They return values without side effects.
  - *Keywords*: `fundecl` (declaration) and `funapp` (application).
- **Procedures**: Bodies contain **commands**. They can modify the global state or perform iterations.
  - *Keywords*: `procdecl` (declaration) and `procapp` (application).
