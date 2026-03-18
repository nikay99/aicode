# AICode Todo App

Eine voll funktionsfähige Kommandozeilen-Todo-App geschrieben in AICode.

## Features

- ✅ Todos erstellen mit Priorität (low/medium/high)
- ✅ Todos als erledigt markieren
- ✅ Todos filtern (nach Status oder Priorität)
- ✅ Persistente Speicherung in JSON
- ✅ Statistiken anzeigen
- ✅ Interaktive CLI

## Dateien

- `models.aic` - Datenstrukturen und Operationen
- `storage.aic` - Datei-I/O (JSON)
- `commands.aic` - CLI Kommandos
- `main.aic` - Hauptprogramm mit Event Loop

## Verwendung

```bash
# App starten
python3 main.py run examples/todo-app/main.aic

# Befehle:
# 1. list     - Alle Todos anzeigen
# 2. add      - Neues Todo hinzufügen
# 3. done     - Todo als erledigt markieren
# 4. undo     - Todo als nicht erledigt markieren
# 5. delete   - Todo löschen
# 6. filter   - Todos filtern
# 7. clear    - Alle Todos löschen
# 8. stats    - Statistiken anzeigen
# 9. help     - Hilfe anzeigen
# 0. quit     - Beenden
```

## Beispiel-Session

```
================================
        TODO APP v1.0          
================================

Loaded 0 existing todos

Commands:
  1. list     - List all todos
  2. add      - Add a new todo
  ...

> add
Title: Einkaufen gehen
Priority (1=low, 2=medium, 3=high): 2
+ Added todo #1: Einkaufen gehen

> add
Title: Sport machen
Priority (1=low, 2=medium, 3=high): 3
+ Added todo #2: Sport machen

> list
Your Todos:
-----------
[ ] 2: Sport machen (HIGH)
[ ] 1: Einkaufen gehen (MEDIUM)

Active: 2 / Total: 2

> done
Todo ID: 2
+ Marked todo #2 as completed

> stats
Statistics
----------
Total todos:     2
Active:          1
Completed:       1
...
```

## Was diese App demonstriert

- **Modulares Design** mit `import`
- **File I/O** mit `read_file`/`write_file`
- **JSON** mit `json_parse`/`json_stringify`
- **Dictionaries** für Datenstrukturen
- **Higher-Order Functions** (filter, map)
- **Interactive Input** mit `input()`
- **While-Loops** für Event Loop

## Bekannte Einschränkungen

- ASCII-Syntax (Unicode-Symbole werden vom ASCII Lexer nicht unterstützt)
- Keine Datum-/Zeit-Funktionen (Datum als Strings gespeichert)
- Einfache Fehlerbehandlung

## Nächste Schritte

Mögliche Erweiterungen:
- [ ] Datums-Validierung
- [ ] Kategorien/Tags
- [ ] Suchfunktion
- [ ] Export nach CSV
- [ ] Mehrere Todo-Listen
