# AICode v0.4 Implementations-Strategie

**Technical Lead Strategic Plan**  
**Datum:** 19. März 2026  
**Version:** 0.4.0 Roadmap

---

## Executive Summary

**Kernproblem:** 2.020 Zeilen duplizierter Code (lexer.py/parser.py vs lexer_ai.py/parser_ai.py)

**Strategie-Empfehlung:** Option A (Refactoring zuerst, dann Features)  
**Risiko-Level:** Mittel  
**Zeitrahmen:** 8 Wochen

---

## 1. Implementations-Reihenfolge

### Empfohlene Option: A - Refactoring zuerst

| Kriterium | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| **Risiko** | Niedrig | Hoch | Sehr Hoch |
| **Code-Qualität** | Hoch | Niedrig | Mittel |
| **Wartbarkeit** | Exzellent | Schlecht | Mittel |
| **Zeit bis v0.4** | 8 Wochen | 6 Wochen | 10 Wochen |
| **Tech Debt** | Eliminiert | Verdoppelt | Unklar |

### Warum Option A?

```
Aktueller State:
┌─────────────────────────────────────────┐
│  lexer.py (423) ───┐                    │
│                     ├── 90% Duplikation │
│  lexer_ai.py (383)─┘                    │
│                                         │
│  parser.py (665) ───┐                   │
│                      ├── 85% Duplikation│
│  parser_ai.py (549)─┘                   │
└─────────────────────────────────────────┘
                   ↓
Nach Refactoring:
┌─────────────────────────────────────────┐
│  lexer.py (500) mit TokenMode Strategy │
│  (ASCII + Unicode in einer Datei)       │
│                                         │
│  parser.py (700) mit ParseMode         │
│  (Eine Grammatik, zwei Modi)           │
└─────────────────────────────────────────┘
```

**Vorteile:**
- Package Manager braucht eine API, nicht zwei
- LSP muss nur einen Parser unterstützen
- Bugfixes werden automatisch für beide Modi gelten
- Neue Features werden nur einmal implementiert

---

## 2. Team-Einteilung (4 Entwickler)

### Team-Struktur

```
Tech Lead (Du)
├── Senior Dev A (Refactoring Lead)
├── Senior Dev B (Features Lead)  
├── Mid-Level Dev C (Testing/Integration)
└── Junior Dev D (Tooling/Docs)
```

### Aufgaben-Verteilung

| Dev | Primäre Aufgabe | Sekundäre Aufgabe | Abhängigkeiten |
|-----|-----------------|-------------------|----------------|
| **Senior A** | Lexer/Parser Merge | Architecture Design | - |
| **Senior B** | Package Manager Core | Module Resolution | Week 2: Merge fertig |
| **Mid C** | LSP Server | Integration Tests | Week 3: APIs stabil |
| **Junior D** | CLI Tooling | Documentation | Week 1: Arch-Docs |

### Zeitplan mit Abhängigkeiten

```
Woche 1:    [A: Lexer Merge]----------->
            [D: Docs]----------------->
            
Woche 2:    [A: Parser Merge]--------->
            [B: Package Manager]------>
            
Woche 3:    [A: Testing Merge]-------->
            [B: Registry API]--------->
            [C: LSP Start]------------>
            
Woche 4:    [A: Code Review]---------->
            [B: Dependency Resolution]->
            [C: LSP Features]--------->
            [D: CLI Polish]----------->
            
Woche 5-6:  [B+C: Integration]-------->
            [A: Performance]---------->
            [D: Examples]------------->
            
Woche 7-8:  [All: Bugfixes + Polish]->
```

### Synchronisations-Strategie

**Daily Standups:** 15 Min via Discord/Slack  
**Wöchentliche Reviews:** Freitag 14:00 Uhr  
**Sprint Planning:** Montag 09:00 Uhr  

**Branching-Strategie:**
```
main (geschützt)
├── release/v0.4.0
│   ├── feature/lexer-unification    [Dev A]
│   ├── feature/parser-unification   [Dev A]
│   ├── feature/package-manager      [Dev B]
│   ├── feature/lsp-server          [Dev C]
│   └── feature/cli-tooling         [Dev D]
```

---

## 3. Risk Assessment

### Risiko-Matrix

| Risiko | Wahrscheinlichkeit | Impact | Score | Mitigation |
|--------|-------------------|--------|-------|------------|
| Merge-Konflikte im Lexer | Hoch | Hoch | 🔴 9 | Feature-Flags verwenden |
| Tests brechen bei Merge | Mittel | Hoch | 🟡 6 | Parallel-Test-Suite |
| Package Manager zu komplex | Mittel | Hoch | 🟡 6 | MVP-Scope definieren |
| LSP Performance-Probleme | Niedrig | Mittel | 🟢 3 | Caching implementieren |
| Zeitplan-Verzug | Hoch | Mittel | 🟡 6 | Wöchentliche Checkpoints |
| Breaking Changes für Nutzer | Mittel | Mittel | 🟡 4 | Deprecation Warnings |

### Fallback-Strategien

**Szenario 1: Merge zu komplex**
- Fallback: Keep both lexers, extract common base class
- Zeitverlust: 2-3 Tage statt 5 Tage

**Szenario 2: Package Manager zu groß**
- Fallback: Minimaler PM (nur install from git)
- Zeitersparnis: 1 Woche

**Szenario 3: LSP zu langsam**
- Fallback: VS Code Extension ohne LSP (Syntax only)
- Zeitverlust: Minimal

**Szenario 4: Zeitplan-Verzug**
- Option A: Alpha verzögern um 1 Woche
- Option B: LSP auf v0.4.1 verschieben
- Option C: Package Manager auf v0.4.1 verschieben

### Testing-Strategie

```python
# Test-Pyramide für v0.4

         /\
        /  \     E2E Tests (10%)
       /----\      - Full IDE workflow
      /      \     - Package install cycle
     /--------\  
    /          \  Integration Tests (30%)
   /------------\   - Lexer+Parser Kombos
  /              \  - Compiler+VM Pipeline
 /----------------\
/                  \ Unit Tests (60%)
/--------------------\  - Lexer (all modes)
                        - Parser (all modes)
                        - Type Checker
```

**Test-Abdeckungsziele:**
- Lexer: 100% (beide Modi)
- Parser: 100% (beide Modi)
- Type Checker: 90%
- Compiler: 85%
- Package Manager: 80%
- LSP: 75%

---

## 4. Migrations-Strategie

### Breaking Changes

| Änderung | Impact | Lösung |
|----------|--------|--------|
| `lexer_ai.py` entfernt | 🔴 Hoch | Import-Redirect in `__init__.py` |
| `parser_ai.py` entfernt | 🔴 Hoch | Import-Redirect + Deprecation |
| Neuer Package-Manager | 🟡 Mittel | Dokumentation + Beispiele |
| CLI Commands renamed | 🟢 Niedrig | Alias + Deprecation Warning |

### Backwards Compatibility

```python
# src/__init__.py - Kompatibilitäts-Layer

import warnings

# Deprecated: Redirect für alte Imports
def lexer_ai():
    warnings.warn(
        "lexer_ai is deprecated. Use lexer with mode='unicode'",
        DeprecationWarning,
        stacklevel=2
    )
    from .lexer import Lexer, TokenMode
    return Lexer(TokenMode.UNICODE)

def parser_ai():
    warnings.warn(
        "parser_ai is deprecated. Use parser with mode='unicode'",
        DeprecationWarning,
        stacklevel=2
    )
    from .parser import Parser, ParseMode
    return Parser(ParseMode.UNICODE)
```

### Migration Guide (für Nutzer)

**Alt (v0.3.x):**
```python
from src.lexer_ai import tokenize
from src.parser_ai import parse
```

**Neu (v0.4.0):**
```python
from src.lexer import tokenize
from src.parser import parse

# Beide unterstützen jetzt beide Modi automatisch
# Oder explizit:
tokens = tokenize(source, mode='unicode')  # oder 'ascii'
```

**Timeline:**
- v0.4.0: Alte Imports funktionieren mit Deprecation Warning
- v0.4.5: Alte Imports funktionieren mit Error (nicht nur Warning)
- v0.5.0: Alte Imports entfernt

---

## 5. Konkrete Milestones

### Woche 1: Foundation
**Ziele:**
- [ ] Architecture Decision Records (ADRs) geschrieben
- [ ] Branch-Struktur eingerichtet
- [ ] CI/CD Pipeline für v0.4 aktiviert
- [ ] Lexer-Unification Design fertig
- [ ] Package Manager API Design fertig

**Deliverables:**
- `docs/adr/001-lexer-unification.md`
- `docs/adr/002-package-manager.md`
- `docs/adr/003-lsp-architecture.md`

### Woche 2: Core Refactoring
**Ziele:**
- [ ] Lexer merge abgeschlossen
- [ ] Alle Lexer-Tests passing
- [ ] Parser merge gestartet
- [ ] Package Manager Grundgerüst

**Deliverables:**
- `src/lexer.py` (unified)
- `src/pm/` package initialized

### Woche 3: Parser & Integration
**Ziele:**
- [ ] Parser merge abgeschlossen
- [ ] Alle Parser-Tests passing
- [ ] Integration: Lexer+Parser+Compiler+VM
- [ ] LSP Server gestartet

**Deliverables:**
- `src/parser.py` (unified)
- `src/lsp/server.py` (basic)

### Woche 4: v0.4.0-alpha Release
**Ziele:**
- [ ] Alpha-Version released
- [ ] Package Manager: install from git
- [ ] LSP: Syntax highlighting
- [ ] Alle 50+ Tests passing

**Deliverables:**
- Tag: `v0.4.0-alpha.1`
- `aic install <git-url>` funktioniert
- VS Code Extension: Syntax Highlighting

### Woche 5: Feature Completion
**Ziele:**
- [ ] Package Manager: Registry support
- [ ] LSP: Auto-completion
- [ ] CLI: Alle Subcommands
- [ ] Performance Benchmarks

**Deliverables:**
- `aic install <package>` from registry
- LSP: Basic completions
- `aic fmt`, `aic check`, `aic test`

### Woche 6: v0.4.0-rc Release
**Ziele:**
- [ ] Release Candidate
- [ ] Integration Tests passing
- [ ] Dokumentation vollständig
- [ ] Breaking Changes dokumentiert

**Deliverables:**
- Tag: `v0.4.0-rc.1`
- Complete Migration Guide
- 100% API Documentation

### Woche 7: Stabilization
**Ziele:**
- [ ] Bugfix-Sprint
- [ ] Performance-Optimierung
- [ ] Community Feedback einarbeiten
- [ ] Release Notes finalisieren

**Deliverables:**
- Bugtracker: 0 kritische Bugs
- Performance Report
- RELEASE_v0.4.md

### Woche 8: v0.4.0-final Release
**Ziele:**
- [ ] Final Release
- [ ] Release Party 🎉
- [ ] Blog Post
- [ ] v0.4.1 Planning

**Deliverables:**
- Tag: `v0.4.0`
- Blog Post auf aicode-lang.org
- Next: v0.4.1 Roadmap

---

## 6. Nächste Konkrete Schritte

### Heute (Tag 1)

1. **Repository Setup**
   ```bash
   git checkout -b release/v0.4.0
   git push -u origin release/v0.4.0
   ```

2. **ADR für Lexer-Unification**
   ```bash
   mkdir -p docs/adr
   cat > docs/adr/001-lexer-unification.md << 'EOF'
   # ADR 001: Lexer Unification
   
   ## Status
   Proposed
   
   ## Context
   Currently we have lexer.py (ASCII) and lexer_ai.py (Unicode) with 90% code duplication.
   
   ## Decision
   Merge into single lexer.py with TokenMode enum.
   
   ## Consequences
   - Positive: Single source of truth, easier maintenance
   - Negative: Breaking change for imports (mitigated by compatibility layer)
   EOF
   ```

3. **Issue Tracker Setup**
   - Erstelle GitHub Milestones für v0.4.0
   - Erstelle Labels: `v0.4`, `refactoring`, `package-manager`, `lsp`
   - Erstelle initial Issues für Week 1 Tasks

### Diese Woche (Woche 1)

**Tag 1-2:**
- [ ] ADRs reviewen & finalisieren
- [ ] Team-Meeting: Architektur-Review
- [ ] Beginn: Lexer-Unification Implementierung

**Tag 3-5:**
- [ ] Lexer-Unification fertigstellen
- [ ] Unit-Tests für unified Lexer
- [ ] Beginn: Parser-Unification Design

---

## 7. Success Metrics

### Technische Metriken

| Metrik | v0.3 | v0.4 Ziel | Wie messen |
|--------|------|-----------|------------|
| Code-Duplikation | 40% | < 5% | `pip install jscpd && jscpd src/` |
| Testabdeckung | 45% | > 85% | `pytest --cov=src` |
| Lines of Code | 3,500 | < 3,000 | `cloc src/` |
| Import-Zeit | 120ms | < 50ms | `time python -c "from src import *"` |
| CLI Startup | 200ms | < 100ms | `time aic --help` |

### Nutzer-Metriken

| Metrik | Ziel | Messung |
|--------|------|---------|
| Migration Rate | > 80% | GitHub Issues/Polls |
| Bug Reports | < 5/Woche | Issue Tracker |
| Package Downloads | > 100 | Registry Analytics |
| LSP Adoption | > 50% | VS Code Extension Stats |

---

## 8. Zusammenfassung

### Empfohlene Strategie

**Option A: Refactoring zuerst, dann Features**

1. **Woche 1-2:** Lexer/Parser vereinheitlichen
2. **Woche 3-4:** Package Manager MVP
3. **Woche 5-6:** LSP Server
4. **Woche 7-8:** Testing & Polish

### Hauptvorteile

- 🎯 **Fokus:** Eine Sache nach der anderen
- 🧹 **Qualität:** Saubere Basis für neue Features
- 🚀 **Wartung:** Zukünftige Features nur 1x implementieren
- 🛡️ **Risiko:** Niedrig durch stabile Test-Basis

### Nächster Schritt

```bash
# Starte jetzt:
git checkout -b release/v0.4.0
echo "# AICode v0.4.0 Roadmap" > ROADMAP_v0.4.md
```

---

**Geplant von:** Technical Lead  
**Review benötigt von:** Team  
**Entscheidungsdeadline:** 20. März 2026
