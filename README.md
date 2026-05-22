# El Senyor dels Anells — Pràctica IA 2026

## Requisits previs

- **Python 3.9 – 3.12** (recomanat 3.10 o 3.11)  
  > Python 3.13 pot causar errors de compilació de pygame. Si tens problemes, instal·la Python 3.11.

Comprova la teva versió amb:
```bash
python --version
```

---

## Instal·lació

### Opció A — pip (entorn virtual recomanat)

```bash
# Clona el repositori
git clone https://github.com/maarcmarcuus/iaprac2_2026.git
cd iaprac2_2026

# Crea i activa un entorn virtual
python -m venv venv

# Linux / macOS:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\activate
```

**Instal·la pygame amb wheel pre-compilat** (evita errors de compilació a Windows):
```bash
pip install pygame --prefer-binary
```

O bé instal·la totes les dependències:
```bash
pip install -r requirements.txt --prefer-binary
```

### Opció B — Conda

```bash
conda create -n anells python=3.11
conda activate anells
pip install pygame --prefer-binary
```

### Solució d'errors comuns a Windows

| Error | Solució |
|-------|---------|
| `No module named 'distutils.msvccompiler'` | Usa `pip install pygame --prefer-binary` en lloc de `pip install -r requirements.txt` |
| `venv\Scripts\activate` no funciona | Executa `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` i torna a provar |

---

## Execució

### Part 1: El Laberint de l'Anell d'Or

```bash
python laberint.py
```

**Controls del teclat:**
- Fletxes + diagonals (Q/E/Z/C) o `WASD` — moure el jugador
- Botó **HINT** — mostra la millor casella següent (A*)
- Botó **GOD MODE** — mostra el camí mínim complet
- Botó **RESET** — nova partida aleatòria

### Part 2: Joc de Cartes (Humà vs Màquina)

```bash
python joc_cartes.py
```

**Accions disponibles per torn (botons a pantalla):**
1. Alliberar carta revelada
2. Reservar carta revelada
3. Alliberar carta reservada
4. Tornar carta al munt
5. Bloquejar torn de l'oponent

---

## Dependències

| Paquet  | Versió mínima | Ús |
|---------|---------------|-----|
| pygame  | 2.1.0         | Interfície gràfica d'ambdós jocs |

La resta d'imports (`sys`, `random`, `heapq`, `math`, `copy`, `itertools`) són de la **llibreria estàndard** de Python.

---

## Estructura del projecte

```
IAprac2_2026/
├── laberint.py       # Part 1: laberint 12×12, A*, HINT/GOD mode
├── joc_cartes.py     # Part 2: joc de cartes, Minimax + Alpha-Beta
├── memoria.md        # Document tècnic: heurística, algorismes, conclusions
├── requirements.txt  # Dependències pip
└── README.md         # Aquest fitxer
```
