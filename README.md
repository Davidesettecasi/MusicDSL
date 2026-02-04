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
 
---

## 4. Memory Management: Environment and State

The interpreter manages data through a decoupled architecture consisting of an **Environment** and a **State (Store)**. This design, inspired by formal operational semantics, allows for robust management of variables, memory locations, and scoping.

### 4.1 Environment as a Function
In MusicDSL, the **Environment** is implemented as a **higher-order function**.
- **Definition**: An `Environment` is a `Callable[[str], DVal]` that maps an identifier (string) to a value.
- **Binding**: When a new variable is defined using `bind`, the interpreter returns a new function. This function checks if the requested name matches the new binding; if not, it recursively searches the previous environment (`lookup`).
- **Initial Environment**: The interpreter starts with a **Global Environment** pre-loaded with primitive operators (arithmetic, logic, and musical).

### 4.2 State and the Store-passing Style
The **State** manages the program's memory, storing values in specific locations (`Loc`) to allow for mutable variables.
- **Store**: Implemented as a function `Callable[[int], MVal]`. Updating the store returns a new function representing the updated memory state.
- **Allocation**: The `allocate` function assigns a unique address to new values and increments the `next_loc` counter.
- **Access and Update**: `access` retrieves values from an address, while `update` modifies existing memory locations.



### 4.3 Type System
The interpreter uses a rigorous type hierarchy:
- `EVal`: Expressible Values (Integers, Booleans, and `MusicResult` lists).
- `MVal`: Storable Values (values that can be saved in the `Store`).
- `DVal`: Denotable Values (Values, Operators, Memory Locations, or Closures).

### 4.5 Built-in Operators
The initial environment is populated with several primitive operators:
- **Math**: `+`, `-`, `*`, `/`, `%`.
- **Logic**: `==`, `!=`, `<`, `>`, `and`, `or`, `not`.
- **Music Analysis**: Native support for list processing (`head`, `tail`) and event inspection (`pitch`).

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

### 9.2 Web Browser
A modern web browser (Chrome, Firefox, or Safari) is required for the interactive visualization and audio playback.

### 9.3 Running Examples
Navigate to the project root directory and run the main interpreter script. You can point the interpreter to one of the provided examples.

### 9.4 Using the Interactive Player
Once the execution is complete:

* **Auto-Open**: Your default browser will automatically open the generated `piano_roll_pro.html` file.
* **Wait for Samples**: Look at the status bar in the browser. It will say **"PIANO READY"** once the high-quality samples are downloaded from the Tone.js cloud.
* **Playback**: Click the **▶ PLAY** button to start the audio engine and visualize the green "GarageBand-style" notes on the grid.

---

## License
This project is licensed under the **MIT License** - see the `LICENSE` file for details.

