# MusicDSL 🎵
> **A Domain-Specific Language for Algorithmic Composition and Music Theory Manipulation.**

## 1. Introduction
**MusicDSL** is a domain-specific programming language designed to model, manipulate, and generate musical structures through symbolic logic. The project aims to provide a programmatic abstraction of music theory, treating composition not just as a creative process, but as a series of algebraic transformations on temporal sequences.

### 1.1 Core Philosophy and Goals
The primary objective of MusicDSL is to bridge the gap between formal logic and artistic expression. By providing an intuitive syntax for notes, durations, and accidentals, the language allows for deep **musical abstraction**. 

At its core, the system features a robust temporal engine designed to manage the complexities of time. It ensures perfect timing integrity by correctly handling the concatenation and overlapping of events, while treating silence (rests) as first-class citizens within the musical timeline. Furthermore, the integration of variables and procedural logic introduces **algorithmic flexibility**, empowering users to create generative compositions—such as automated scale generation or dynamic accompaniments—that would be difficult to achieve in traditional notation software.

### 1.2 Execution Pipeline: From Text to Music
The execution of a program written in **MusicDSL** follows a three-stage process managed entirely within a Python environment:

1.  **Syntactic Analysis (Parsing) with Lark**: The source code is analyzed by the `Lark` library. It uses a formal grammar (defined in EBNF format) to validate the syntax and transform text strings into an **Abstract Syntax Tree (AST)**.
2.  **Transformation and Evaluation (Transformer)**: A `Transformer` component traverses the AST and converts abstract nodes into real Python objects (e.g., instantiating a `Note` class or executing temporal logic for the `++` operator).
3.  **Output Generation**: The final result is a `MusicResult` structure (a list of events). This list is serialized into JSON and passed to a web back-end for sound reproduction and graphical visualization.



---

## 2. Semantic Domain

To represent music programmatically, the language maps source code expressions into a structured data model. This semantic domain is built upon three core entities, designed to handle both the hierarchical and temporal nature of sound.

### 2.1 The NoteValue: The Sonic Atom
At the most granular level, the `NoteValue` represents the fundamental unit of sound information. It encapsulates the **midi_pitch** (an integer following the MIDI standard, where Middle C is 60 and rests are conventionally flagged as -1) and the **duration** (a float representing the relative length of the note). By isolating these properties, the language treats the note as an abstract physical entity, independent of its position in time.

### 2.2 The MusicEvent: A Temporal Container
The `MusicEvent` serves as a "trigger point" on the musical timeline, bridging the gap between abstract notes and actual performance. It is defined by a **start_time**—the precise offset from the beginning of the composition—and a **set of NoteValues**. This design choice is pivotal: by using a set, the language provides native support for **polyphony**. Multiple notes starting at the same instant automatically form a chord, drastically simplifying the management of vertical harmonic structures.



### 2.3 The MusicResult: The Time Series
The final output of the evaluation process is the `MusicResult`, which is structurally defined as a **list of MusicEvents**. This ordered sequence represents the entire composition as a time series, ready to be serialized and rendered by the playback engine.

---

## 3. Syntax and Language Structure

In **MusicDSL**, every instruction is designed to be an expression that contributes to a `MusicResult`. The syntax balances musical readability with the rigorous requirements of a programming language, allowing for both simple compositions and complex algorithmic structures.

### 3.1 Musical Primitives and Temporal Logic
The basic units of composition are **Notes** and **Rests**. A note is defined by its pitch, accidental, and octave (e.g., `Cn4` for Middle C natural), optionally followed by its duration (e.g., `Cn4/1`). Rests follow a similar pattern, using the `R` symbol (e.g., `R/0.5`).



To combine these atoms into melodies and harmonies, the language provides three fundamental operators that manipulate the timeline:
* **Concatenation (`++`)**: Sequences two musical events chronologically, calculating the correct offset based on the duration of the first.
* **Union (`|`)**: Overlaps two sequences simultaneously, enabling native polyphony and chord construction.
* **Transposition (`!`)**: Dynamically shifts the pitch of an entire sequence by a given interval.

### 3.2 Computational Core: Data and Manipulation
Beyond music, the language supports **Integers** and **Booleans**, enabling the calculation of musical parameters through standard arithmetic (`+`, `-`, `*`, `/`, `%`) and logical comparisons (`==`, `<`, `and`, `not`). 

To manipulate musical sequences as data structures, MusicDSL offers powerful unary operations inspired by functional programming:
* `head` and `tail`: Used for recursive list processing, allowing the user to peel off the first event of a melody.
* `is_empty`: A boolean check essential for managing loop termination.
* `pitch` : Inspects the frequency of a `MusicEvent`.
* `initialize`: Resets the `start_time` of a `MusicEvent` to the origin (0.0).

### 3.3 State and Scoping
The language supports two distinct ways to manage data and names:
1. **Functional Scoping (`let`)**: Defines local, immutable variables with static scoping, ideal for temporary calculations within an expression.
2. **Imperative State (`var` and `<-`)**: Manages global, mutable variables that persist across the execution flow.

### 3.4 Commands, Functions and Procedures
Execution is controlled via **Command Sequences** separated by semicolons (`;`). These can be nested within `if-then-else` branches or `while` loops for generative music. Finally, MusicDSL distinguishes between **Functions** (`fundecl`), which are pure and side-effect-free, and **Procedures** (`procdecl`), which can execute commands and modify the global state.

---

### 3.5 Formal Grammar (EBNF)
The following is the formal definition of the language used by the **Lark** parser. It defines the hierarchy of commands, operator precedence, and the structure of musical tokens.



```lark
# The entry point is a program (sequence of commands)
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

# State Commands
vardecl: "var" IDENTIFIER "=" expr
assign: IDENTIFIER "<-" expr
print: "print" expr

# Control Structures
while: "while" expr "do" "{" command_seq "}"
ifelse: "if" expr "then" "{" command_seq "}" "else" "{" command_seq "}"

# Functions and Procedures
fundecl: "function" IDENTIFIER "(" [param_list] ")" "=" expr
param_list: IDENTIFIER ("," IDENTIFIER)*
procdecl: "procedure" IDENTIFIER "(" [param_list] ")" "=" "{" command_seq "return" expr "}"

# Expressions
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

# Musical Definitions
note: PITCH ACCIDENTAL OCTAVE ["/" DUR]
rest: REST_SYMBOL ["/" DUR]

# Terminals
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
```
 
---

## 4. Memory Management: Environment and State

The MusicDSL interpreter manages data through a decoupled architecture that separates identifiers from their actual values. Inspired by formal operational semantics, this design distinguishes between the **Environment** (naming) and the **State** (memory storage), ensuring robust scoping and clean variable management.

### 4.1 Functional Environment and Scoping
In MusicDSL, the environment is not a simple static map, but a **higher-order function** (`Callable[[str], DVal]`). This functional approach means that every time a variable is bound, the interpreter generates a new function that encapsulates the new name-value pair. If a requested identifier isn't found in the current layer, the system recursively searches through previous layers. The execution begins with a **Global Environment**, pre-loaded with essential operators for arithmetic, logic, and musical analysis (such as `head`, `tail`, and `pitch`).

### 4.2 The State and Store-passing Style
While the environment handles names, the **State** (or Store) manages the program's physical memory. By mapping unique locations (`Loc`) to values through a `Store` function, the language enables mutable variables and persistent data. 
* **Allocation**: The `allocate` function grants a unique memory address to every new value, incrementing an internal counter to prevent collisions.
* **Access and Update**: The system provides dedicated primitives to retrieve values from an address (`access`) or modify them (`update`) without altering the overall structure of the environment.



### 4.3 Type Hierarchy and Built-in Operators
To maintain data integrity, the interpreter enforces a rigorous type system. Values are categorized based on their role:
* **EVal (Expressible)**: Values that can be the result of an expression (Integers, Booleans, or Musical sequences).
* **MVal (Storable)**: Anything that can be saved within the State's memory.
* **DVal (Denotable)**: The broadest category, including memory locations, functional closures, and built-in operators.


---

## 5. From Text to Structure: Parsing and the AST

The journey of a MusicDSL program starts with a raw string of text and ends with a sophisticated **Abstract Syntax Tree (AST)**. This process is orchestrated by the `Lark` library, which first performs a syntactic analysis of the source code. During this initial phase, Lark generates an *Abstract Parse Tree*—a literal representation of the grammar rules. However, to make this data useful for our interpreter, we perform a second, more refined step: the **Transformation**.



### 5.1 Building the Abstract Syntax Tree (AST)
The AST is the "skeleton" of the program, stripped of any syntactic noise (like semicolons or parentheses used for grouping). Each node in this tree is a Python `dataclass` representing a specific semantic concept. We distinguish between two main categories of nodes:

* **Expressions**: These are the building blocks that return musical or logical values. They range from simple atoms like `Number`, `Bool`, and `Note` (which stores pitch, accidental, and duration) to more complex operations like `Apply` (for arithmetic or musical operators) and `FunctionApp`.
* **Commands**: These represent the active instructions of the language. Nodes like `Assign`, `VarDecl`, `While`, and `IfElse` do not return a value but instead modify the state of the program or control its execution flow. A specialized node, `CommandSequence`, acts as a recursive link that allows multiple commands to be executed in a specific order.

### 5.2 The Transformation Process
To convert the raw Lark parse tree into our typed AST, we use specialized transformer functions: `transform_expr_tree` and `transform_command_tree`. 

The process utilizes **Structural Pattern Matching** (Python's `match-case`) to navigate the tree nodes. For instance, when the transformer encounters a node labeled as a `note`, it extracts the pitch and duration tokens to instantiate a `Note` object. If it finds a `bin` (binary) node, it recursively transforms the left and right children and wraps them in an `Apply` node with the corresponding operator.

A key challenge in this phase is managing the sequence of execution. The `ensure_command_seq` utility ensures that every instruction—whether it's a single `print` or a complex `while` loop—is correctly wrapped into a `CommandSequence`. This recursive structure allows the interpreter to "consume" the program instruction by instruction, maintaining a clear path through the logic of the composition.



### 5.3 Procedural and Functional Abstractions
The AST also handles the complexity of declarations. When a function or procedure is defined via `FunctionDecl` or `ProcedureDecl`, the transformer captures the parameter names and the body (which could be an expression for functions or a sequence of commands for procedures). These nodes are later used by the evaluator to create **Closures**, which pair the code with the environment in which it was defined, ensuring that variables are correctly resolved during execution.

---

## 6. Evaluation and Execution

Once the source code has been transformed into an Abstract Syntax Tree (AST), the interpreter begins the process of giving semantic meaning to the nodes. This is achieved through two main mechanisms: **Expression Evaluation**, which calculates values (like notes or numbers), and **Command Execution**, which manages the program's logic and memory state.

### 7.1 Evaluating Expressions
The `evaluate_expr` function is a recursive engine that traverses the tree to produce a value (an `EVal`). When the interpreter encounters a `Note` node, it converts musical notation into a MIDI pitch and returns a `MusicEvent`—the fundamental unit of our musical time series. Similarly, a `Rest` is evaluated as a "silent note" with a conventional pitch of `-1`, ensuring that pauses occupy the correct space in the timeline.

A critical feature of our evaluator is **Dynamic Type Checking**. When an operator (like `++` for concatenation or `*` for multiplication) is applied via the `Apply` node, the interpreter doesn't just execute the function; it first verifies that the arguments match the expected types defined in the `Operator` structure. This ensures, for example, that a user cannot accidentally "multiply" a melody by a boolean, providing clear error messages when the logic fails.



The evaluator also handles the complexity of **Scoping**. For variables, it performs a `lookup` in the environment; if the identifier points to a memory location (`Loc`), it seamlessly reaches into the **State** to retrieve the current value. In the case of `Let` expressions, it creates a temporary, extended environment to support static scoping, ensuring that local variables do not "leak" into the global space.

### 6.2 Executing Commands and Managing State
While expressions calculate values, **Commands** are responsible for changing the world. The `execute_command` function manages the life cycle of variables and the flow of the program.

* **Variables and Assignment**: When a `VarDecl` is executed, the interpreter allocates a new spot in the memory store and binds the name to that location. The `Assign` command allows these values to be updated over time, enabling the incremental construction of complex musical pieces.
* **Control Flow**: The logic for `IfElse` and `While` constructs demonstrates how the interpreter handles conditional execution. In a `While` loop, the interpreter uses a recursive function to repeatedly evaluate the condition and execute the body. A key technical detail is the **local memory management**: after each iteration, the interpreter resets the memory allocation counter (`next_loc`) to prevent the store from bloating with temporary variables created inside the loop.
* **The Print Command**: This command serves as the bridge between the digital logic and the user. If the expression being printed is a musical sequence, the interpreter automatically triggers the `visualize_garageband_piano_roll` function, transforming the internal list of events into an interactive graphical interface.



### 6.3 Closures: Preserving Context
One of the most sophisticated aspects of the execution engine is the management of **Functions and Procedures**. When a `FunctionDecl` or `ProcedureDecl` is executed, the interpreter creates a **Closure**. 

A closure is more than just a block of code; it is a "snapshot" that captures the environment existing at the moment of declaration. This means that when a function is called later (via `funapp`), it remembers the variables that were visible when it was born, regardless of where it is being called from. The distinction between the two is strictly maintained: **Functions** evaluate their body as a pure expression, while **Procedures** execute a sequence of commands and return a final result, allowing for complex, state-altering musical algorithms.

### 6.4 Running the Program
The entire process is wrapped in the `execute_program` function. It acts as the orchestrator that takes the raw text, calls the **Parser** to build the command sequence, initializes the **Global Environment** with all built-in musical and mathematical operators, and finally kicks off the recursive chain of execution that results in the final musical output.

---

## 7. Visualization and Audio Playback

The final stage of the **MusicDSL** pipeline is the transformation of the logical `MusicResult` into an interactive, high-fidelity web interface. This is achieved by generating a standalone HTML5 file that combines dynamic SVG graphics with a professional-grade audio engine.

### 7.1 The "GarageBand Style" Piano Roll
The visualizer processes the list of musical events to create a classic **Piano Roll** interface. 
* **Dynamic Grid**: The system calculates the total duration of the piece and the pitch range (from the lowest to the highest note) to generate a proportional SVG grid. 
* **Musical Keyboard**: A responsive CSS-based keyboard is rendered on the left side, featuring a realistic layout of white and black keys. 
* **Note Rendering**: Each note is drawn as a green rounded rectangle (reminiscent of professional DAWs like GarageBand). The horizontal position and width are strictly determined by the `start_time` and `duration` calculated during the evaluation phase.



### 7.2 High-Fidelity Audio Synthesis
For sound reproduction, the project integrates the **Tone.js** library and uses **Sample-based Synthesis**:
* **Salamander Piano Samples**: Instead of using simple oscillators, the player downloads real high-quality piano samples for various pitches and octaves. This provides a realistic and pleasant listening experience.
* **Scheduling**: The Python interpreter exports the musical data as a JSON object. The JavaScript engine then schedules each note precisely in the future using the `piano.triggerAttackRelease` method, taking into account a `bpm_factor` to control the playback speed.
* **Audio Effects**: To add depth to the sound, a **Convolution Reverb** effect is applied to the master output, simulating the acoustics of a real concert hall.

### 7.3 Interaction and Web Integration
The visualization is triggered by the `print` command within the DSL. When the interpreter detects a musical sequence, it automatically:
1.  Generates a local `.html` file containing the SVG and the player logic.
2.  Opens the user's default web browser.
3.  Initializes the audio sampler, allowing the user to play the composition with a single click once the samples are loaded.

---


## 8. Practical Examples and Algorithmic Composition

To demonstrate the expressiveness and computational power of **MusicDSL**, the repository includes three examples that progress from basic musical structures to advanced algorithmic transformations.

### 8.1 Basic: Dynamic Scale Generation
The first example showcases how procedures can be used to automate repetitive musical tasks. Instead of manually writing every note, we defined a procedure that:
* Takes a **starting pitch** as input.
* Iteratively calculates the intervals of a **Major Scale**.
* Uses a `while` loop to concatenate the notes into a single `MusicResult`.
This illustrates the leap from a simple sequencer to a programmable musical environment.

### 8.2 Intermediate: Jazz Harmony and Chord Voicings
The second example focuses on **vertical structures (polyphony)** and compositional logic. We re-imagined the traditional melody of *Brother John* (Fra Martino) through a sophisticated Jazz arrangement:
* **Chord Construction**: Accords are built using the `|` (**Union**) operator to stack multiple `Note` values simultaneously at the same `start_time`.
* **Harmonic Progression**: These individual chords are then linked together using the `++` (**Concatenation**) operator to create a fluid harmonic accompaniment.
* **Layering**: The final result is obtained by merging the lead melody with the jazz harmony, demonstrating how the language handles high-density musical information without losing timing integrity.



### 8.3 Advanced: The Diatonic Canon and Functional Analysis
The final example is a masterpiece of **Algorithmic Music Theory**, consisting of a 4-voice canon built through functional transformations of a primary subject:

1.  **Voice 1 (The Subject)**: A simple original melody in C Major.
2.  **Voice 2 (Diatonic Transposition)**: This voice is transposed by a third, but not through a simple pitch shift. We implemented a function `is_in_scale` to verify that every new note belongs to the C Major scale. The `trasponi_melodia_diatonica` function uses this logic to ensure the transposition remains "musically correct" according to the rules of Western harmony.
3.  **Voice 3 (Retrograde Transformation)**: Created using a `reverse_melody` function, which processes the `MusicResult` list to play the subject backward, a classic technique in counterpoint.
4.  **Voice 4 (The Bass)**: A supportive line that highlights the tonics of the C and G chords, providing a solid harmonic foundation for the other three moving voices.



This example highlights the power of **MusicDSL** as a tool for analysis: functions can "inspect" a melody (via `head`, `tail`, and `pitch`), apply logic to it, and generate entirely new musical material based on theoretical constraints.

---

## 9. How to Run

To execute a **MusicDSL** script and experience the algorithmic compositions, follow these steps:

### 9.1 Prerequisites
Ensure you have **Python 3.10+** installed on your system. You will also need the `lark` library for parsing.

1. **Install Lark**:
   ```bash
   pip install lark
   ```
   
2. **Web Browser**:
A modern web browser (Chrome, Firefox, or Safari) is required for the interactive visualization and audio playback.

### 9.2 Running Examples
Navigate to the project root directory and run the main interpreter script. You can point the interpreter to one of the provided examples.

### 9.3 Using the Interactive Player
Once the execution is complete:

* **Auto-Open**: Your default browser will automatically open the generated `piano_roll_pro.html` file.
* **Wait for Samples**: Look at the status bar in the browser. It will say **"PIANO READY"** once the high-quality samples are downloaded from the Tone.js cloud.
* **Playback**: Click the **▶ PLAY** button to start the audio engine and visualize the green "GarageBand-style" notes on the grid.

---

## License
This project is licensed under the **MIT License** - see the `LICENSE` file for details.

