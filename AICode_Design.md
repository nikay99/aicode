# AICode - KI-optimierte Programmiersprache

## 1. Vision & Kernziele

AICode ist eine Programmiersprache, die explizit für KI-Assistenten optimiert ist. Hauptziele:

- **50-70% weniger Token** im Vergleich zu Python/JavaScript
- **Explizite, vorhersagbare Strukturen** für bessere KI-Completion
- **Minimale Syntax-Überraschungen** - keine versteckten Magie
- **Funktional-first** mit klaren Datenflüssen
- **Type-Safety** ohne Boilerplate

## 2. Design-Philosophie

### 2.1 Token-Effizienz-Regeln

| Regel | Beispiel | Token-Ersparnis |
|-------|----------|-----------------|
| Whitespace-basierte Blöcke | Keine `{}` oder `;` | 20-30% |
| Kurze Keywords | `fn` statt `function` | 5-10% |
| Implizite Returns | Letzte Zeile = Return | 5-8% |
| Auto-Import | Standardlib immer da | 10-15% |
| String-Interpolation | `"H $name"` | 5% |

### 2.2 KI-Verständlichkeits-Prinzipien

1. **Immutable by Default** - Keine Seiteneffekte ohne explizites `mut`
2. **Explizite Error-Handling** - Keine Exceptions, nur `Result<T, E>`
3. **Komposition > Vererbung** - Kleine, wiederverwendbare Funktionen
4. **Klare Datenflüsse** - Pipe-Operator für Transformationen
5. **Pattern Matching** - Explizite Fallunterscheidungen

## 3. Syntax-Spezifikation

### 3.1 Variablen & Typen

```aic
# Variablen: let name[: typ] = wert
let x = 42                    # Type-Inference
let y: int = 42              # Expliziter Typ
let mut z = 0                # Mutable

# Konstanten
const PI = 3.14159

# Primitive Typen
bool, int, float, str, char

# Komplexe Typen
list<T>, dict<K, V>, option<T>, result<T, E>, tuple<T...>
```

### 3.2 Funktionen

```aic
# Funktionsdefinition
fn add(a: int, b: int) -> int
  a + b

# Mehrzeilig
fn factorial(n: int) -> int
  if n <= 1
    1
  else
    n * factorial(n - 1)

# Lambda/Closure
let double = fn(x: int) -> int: x * 2
let double = \x: x * 2           # Kurzform

# Higher-Order Functions
fn apply_twice(f: fn(int) -> int, x: int) -> int
  f(f(x))
```

### 3.3 Datenstrukturen

```aic
# Listen
let nums = [1, 2, 3, 4, 5]
let names: list<str> = ["Anna", "Ben"]

# Dictionaries
let user = {name: "Max", age: 30}
let scores: dict<str, int> = {"Max": 100, "Anna": 95}

# Tuples
let point = (x: 10, y: 20)
let (x, y) = point             # Destructuring

# Structs (Product Types)
struct Point
  x: float
  y: float

let p = Point(x: 10.0, y: 20.0)

# Enums (Sum Types)
enum Status
  Loading
  Success(data: str)
  Error(msg: str)

let s = Status.Success("Done")
```

### 3.4 Kontrollfluss

```aic
# If-Else (ist ein Ausdruck!)
let result = if x > 0
  "positive"
else if x < 0
  "negative"
else
  "zero"

# Pattern Matching
match status
  Status.Loading -> "Warte..."
  Status.Success(data) -> "Fertig: " + data
  Status.Error(msg) -> "Fehler: " + msg

# For-Schleifen
for i in 0..10
  print(i)

for user in users
  if user.active
    process(user)

# While
while condition
  do_something()
```

### 3.5 Pipe-Operator & Method Chaining

```aic
# Standard-Approach (Pipe-Operator |>)
users
  |> filter(fn(u): u.active)
  |> map(fn(u): u.name)
  |> sort
  |> take(10)
  |> join(", ")

# Oder: Method-Syntax
users
  .filter(fn(u): u.active)
  .map(fn(u): u.name)
  .sort()
  .take(10)
  .join(", ")

# Beide kombinierbar
users
  |> filter(.active)        # Field access shorthand
  |> map(.name.upper())
```

### 3.6 Error Handling

```aic
# Result<T, E> statt Exceptions
fn divide(a: int, b: int) -> result<int, str>
  if b == 0
    Err("Division by zero")
  else
    Ok(a / b)

# ?-Operator für Propagation
fn calculate() -> result<int, str>
  let x = divide(10, 2)?     # Early return bei Err
  let y = divide(x, 5)?
  Ok(y)

# unwrap_or für Defaults
let value = divide(10, 0).unwrap_or(0)

# match für explizite Handhabung
match divide(10, 0)
  Ok(val) -> print("Result: " + val)
  Err(e) -> print("Error: " + e)
```

### 3.7 String-Interpolation

```aic
let name = "Max"
let age = 30

# Kurzform
let msg = "Hallo $name, du bist $age Jahre alt"

# Ausdrücke
let info = "Summe: ${x + y}"

# Mehrzeilige Strings
let query = "
  SELECT *
  FROM users
  WHERE name = '$name'
"
```

### 3.8 Module & Imports

```aic
# Kein expliziter Import nötig für Standardlib!
# (math, io, string, list, dict, etc. sind immer verfügbar)

# Eigene Module
import utils
import utils as u           # Alias
from math import sqrt, pow  # Selektiver Import

# Modul-Definition
# file: utils.aic
export fn helper(x: int) -> int
  x * 2

export const VERSION = "1.0.0"
```

## 4. Implementierungs-Roadmap

### Phase 1: Core (Woche 1-2)
- [ ] Lexer implementieren
- [ ] Parser (Recursive Descent oder Pratt)
- [ ] AST-Definition
- [ ] Basis-Evaluator (Interpreter)

### Phase 2: Typesystem (Woche 3-4)
- [ ] Hindley-Milner Type Inference
- [ ] Type Checker
- [ ] Fehlermeldungen mit Vorschlägen
- [ ] Generics

### Phase 3: Standardlib (Woche 5-6)
- [ ] Listen-Operationen (map, filter, reduce, etc.)
- [ ] String-Manipulation
- [ ] I/O (Dateien, Konsole)
- [ ] Math-Modul
- [ ] Dict-Operationen

### Phase 4: Compiler (Woche 7-8)
- [ ] Bytecode-Compiler oder LLVM-Backend
- [ ] Optimierungen (Inlining, Dead Code Elimination)
- [ ] CLI-Tool

### Phase 5: Tooling (Woche 9-10)
- [ ] LSP (Language Server Protocol)
- [ ] Formatter
- [ ] Syntax-Highlighter (VSCode, etc.)
- [ ] REPL

### Phase 6: KI-Integration (Woche 11-12)
- [ ] Training-Corpus erstellen
- [ ] Fine-tuned Model für AICode
- [ ] Prompt-Templates
- [ ] Code-Completion-Optimierungen

## 5. Token-Effizienz-Vergleich

### Beispiel: Datenverarbeitung

**Python (127 Tokens):**
```python
def process_users(users):
    active = [u.name.upper() for u in users if u.active]
    return sorted(active)[:10]
```

**AICode (67 Tokens - 47% weniger):**
```aic
fn process_users(users: list<User>) -> list<str>
  users
    |> filter(.active)
    |> map(.name.upper)
    |> sort
    |> take(10)
```

### Beispiel: Error Handling

**Rust (89 Tokens):**
```rust
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

**AICode (52 Tokens - 42% weniger):**
```aic
fn divide(a: int, b: int) -> result<int, str>
  if b == 0
    Err("Division by zero")
  else
    Ok(a / b)
```

## 6. KI-Optimierungsstrategien

### 6.1 Vorhersagbare Patterns

```aic
# KI erkennt Pattern leicht:
# "Datenquelle -> Filter -> Transform -> Aggregieren"

data
  |> filter(condition)
  |> map(transformation)
  |> reduce(operation)

# Entspricht natürlicher KI-Denkweise:
# "Nimm Daten, behalte nur relevante, wandle um, fasse zusammen"
```

### 6.2 Explizite Intentions

```aic
# Schlecht (mehrdeutig):
let x = get_data()        # Was ist x? Kann null sein?

# Gut (explizit):
let result: result<Data, Error> = get_data()
match result
  Ok(data) -> process(data)
  Err(e) -> handle(e)
```

### 6.3 Kleine, komponierbare Funktionen

```aic
# Jede Funktion hat einen klaren, einzigen Zweck
fn is_even(n: int) -> bool: n % 2 == 0
fn square(n: int) -> int: n * n
fn sum(a: int, b: int) -> int: a + b

# Komposition
numbers
  |> filter(is_even)
  |> map(square)
  |> fold(0, sum)
```

## 7. Standardlibrary-Design

### 7.1 Listen-Modul

```aic
# Core-Operationen (immer verfügbar)
list.map<T, U>(self: list<T>, f: fn(T) -> U) -> list<U>
list.filter<T>(self: list<T>, f: fn(T) -> bool) -> list<T>
list.reduce<T, U>(self: list<T>, init: U, f: fn(U, T) -> U) -> U
list.find<T>(self: list<T>, f: fn(T) -> bool) -> option<T>
list.take<T>(self: list<T>, n: int) -> list<T>
list.drop<T>(self: list<T>, n: int) -> list<T>
list.sort<T>(self: list<T>) -> list<T>
list.join<T>(self: list<T>, sep: str) -> str
list.length<T>(self: list<T>) -> int
list.contains<T>(self: list<T>, item: T) -> bool
```

### 7.2 String-Modul

```aic
str.length(self: str) -> int
str.upper(self: str) -> str
str.lower(self: str) -> str
str.trim(self: str) -> str
str.split(self: str, delim: str) -> list<str>
str.replace(self: str, old: str, new: str) -> str
str.starts_with(self: str, prefix: str) -> bool
str.parse_int(self: str) -> result<int, str>
str.parse_float(self: str) -> result<float, str>
```

### 7.3 I/O-Modul

```aic
io.print(msg: str) -> void
io.println(msg: str) -> void
io.input(prompt: str) -> str
io.read_file(path: str) -> result<str, str>
io.write_file(path: str, content: str) -> result<void, str>
io.exists(path: str) -> bool
```

## 8. Beispiel-Programme

### 8.1 FizzBuzz

```aic
fn fizzbuzz(n: int) -> str
  match (n % 3 == 0, n % 5 == 0)
    (true, true) -> "FizzBuzz"
    (true, false) -> "Fizz"
    (false, true) -> "Buzz"
    (false, false) -> n.to_str()

# Ausführen
for i in 1..100
  io.println(fizzbuzz(i))
```

### 8.2 HTTP API Client

```aic
struct User
  id: int
  name: str
  email: str

fn fetch_users() -> result<list<User>, str>
  match http.get("https://api.example.com/users")
    Ok(response) -> parse_users(response.body)
    Err(e) -> Err("Request failed: " + e)

fn parse_users(json: str) -> result<list<User>, str>
  # JSON parsing...
  Ok(users)

fn main()
  match fetch_users()
    Ok(users) -> 
      users
        |> filter(fn(u): u.name.starts_with("A"))
        |> map(fn(u): u.email)
        |> io.println
    Err(e) -> io.println("Error: " + e)
```

### 8.3 Daten-Analyse

```aic
struct Sales
  product: str
  amount: int
  date: str

fn total_by_product(sales: list<Sales>) -> dict<str, int>
  sales
    |> fold({}, fn(acc, s):
      let current = acc.get(s.product).unwrap_or(0)
      acc.insert(s.product, current + s.amount)
    )

fn top_products(sales: list<Sales>, n: int) -> list<(str, int)>
  total_by_product(sales)
    |> dict.to_list
    |> sort_by(fn((_, amount)): -amount)  # Absteigend
    |> take(n)

# Nutzung
let data = [
  Sales(product: "Laptop", amount: 1200, date: "2024-01-01"),
  Sales(product: "Mouse", amount: 25, date: "2024-01-01"),
  Sales(product: "Laptop", amount: 1200, date: "2024-01-02"),
]

top_products(data, 5)
  |> map(fn((name, total)): "$name: $total")
  |> str.join("\n")
  |> io.println
```

## 9. Tooling & IDE-Support

### 9.1 CLI-Kommandos

```bash
# Ausführen
aic run main.aic

# Kompilieren
aic build main.aic -o output

# Type-Check
aic check main.aic

# REPL
aic repl

# Formatieren
aic fmt main.aic

# LSP starten
aic lsp
```

### 9.2 LSP-Features

- Autocomplete (Typ-basiert)
- Go to Definition
- Find References
- Type Hover
- Rename Refactoring
- Error Diagnostics
- Code Actions (Quick Fixes)

## 10. Zukunftsausblick

### 10.1 Erweiterte Features

- **Effekt-System**: Explizite Seiteneffekte (IO, Async, etc.)
- **Async/Await**: Native Unterstützung für Nebenläufigkeit
- **Macros**: Hygienische Makros für Metaprogrammierung
- **WASM-Target**: Kompilierung zu WebAssembly
- **Package Manager**: Einfache Dependency-Verwaltung

### 10.2 KI-Integration Level 2

- **Intentions-Recognizer**: KI versteht natürlichsprachige Beschreibungen
- **Auto-Refactoring**: Code automatisch optimieren/vereinfachen
- **Test-Generation**: Tests aus Code generieren
- **Dokumentation**: Auto-Doku aus Typen und Patterns

## 11. Technische Spezifikationen

### 11.1 Grammatik-Regeln (EBNF)

```ebnf
program         ::= statement*

statement       ::= let_stmt
                  | const_stmt
                  | fn_stmt
                  | struct_stmt
                  | enum_stmt
                  | expr_stmt
                  | return_stmt

let_stmt        ::= "let" identifier [":" type] "=" expr
const_stmt      ::= "const" identifier "=" expr
fn_stmt         ::= "fn" identifier "(" params ")" ["->" type] block
struct_stmt     ::= "struct" identifier struct_body
enum_stmt       ::= "enum" identifier enum_body

params          ::= [param ("," param)*]
param           ::= identifier ":" type

block           ::= NEWLINE INDENT statement+ DEDENT
                  | "{" statement* "}"

expr            ::= pipe_expr

pipe_expr       ::= logic_expr ("|>" logic_expr)*

logic_expr      ::= comp_expr (("&&" | "||") comp_expr)*
comp_expr       ::= add_expr (("==" | "!=" | "<" | ">" | "<=" | ">=") add_expr)*
add_expr        ::= mul_expr (("+" | "-") mul_expr)*
mul_expr        ::= unary_expr (("*" | "/" | "%") unary_expr)*
unary_expr      ::= ("!" | "-") unary_expr | postfix_expr
postfix_expr    ::= primary_expr ("." identifier | "(" args ")" | "[" expr "]")*
primary_expr    ::= identifier
                  | literal
                  | "(" expr ")"
                  | lambda
                  | match_expr
                  | if_expr

lambda          ::= "\\" [params] ":" expr
                  | "fn" "(" params ")" ["->" type] ":" expr

match_expr      ::= "match" expr NEWLINE INDENT match_arm+ DEDENT
match_arm       ::= pattern "->" expr NEWLINE

pattern         ::= identifier ["(" pattern* ")"]
                  | literal
                  | "_"

if_expr         ::= "if" expr block ["else" (if_expr | block)]

literal         ::= int | float | string | bool | "null"
                  | list_literal | dict_literal | tuple_literal

list_literal    ::= "[" [expr ("," expr)*] "]"
dict_literal    ::= "{" [dict_entry ("," dict_entry)*] "}"
dict_entry      ::= (identifier | string) ":" expr
tuple_literal   ::= "(" expr ("," expr)+ ")"

type            ::= identifier ["<" type ("," type)* ">"]
                  | "(" type ("," type)* ")" "->" type
                  | "fn" "(" [type ("," type)*] ")" "->" type
```

### 11.2 Speicher-Management

- **Garbage Collection**: Einfacher, deterministischer GC
- **Wert-Semantik**: Structs werden kopiert (COW-Optimierung)
- **Referenz-Semantik**: Listen/Dicts sind Referenzen

### 11.3 Performance-Ziele

- **Startup**: < 10ms für kleine Programme
- **Throughput**: ~50% von Go/Rust
- **Memory**: Minimaler Overhead durch GC
- **Compilation**: Schneller als TypeScript

## 12. Migrations-Guide

### Von Python

```python
# Python
def process(items):
    return [x * 2 for x in items if x > 0]
```

```aic
# AICode
fn process(items: list<int>) -> list<int>
  items |> filter(fn(x): x > 0) |> map(fn(x): x * 2)
```

### Von JavaScript

```javascript
// JavaScript
const users = await fetch('/api/users');
const names = users.filter(u => u.active).map(u => u.name);
```

```aic
# AICode
let users = http.get("/api/users")?
let names = users |> filter(.active) |> map(.name)
```

### Von Rust

```rust
// Rust
let result: Result<i32, String> = divide(10, 2)?;
```

```aic
# AICode
let result: result<int, str> = divide(10, 2)?
```

---

## Nächste Schritte

1. [ ] Prototyp-Interpreter in Python/OCaml erstellen
2. [ ] Test-Corpus mit 100+ Beispielprogrammen
3. [ ] Token-Effizienz-Tests mit verschiedenen KI-Modellen
4. [ ] Community-Feedback sammeln
5. [ ] Referenz-Implementierung in Rust

**Fokus**: Schneller Prototyp zur Validierung der Token-Effizienz!
