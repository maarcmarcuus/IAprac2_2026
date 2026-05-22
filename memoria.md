# Memòria - El Senyor dels Anells (Pràctica IA 2026)

## Part 1: El Laberint de l'Anell d'Or (`laberint.py`)

### Algorisme de cerca: A*

S'utilitza l'algorisme **A*** per trobar el camí de cost mínim des de la posició actual del jugador fins a recollir tots els anells en ordre jeràrquic (bronze → plata → or).

**Estat de l'A***: `(posició_jugador, frozenset_d'anells_recollits)`

**Funció de cost**: cada moviment (8 direccions, incloses diagonals) té cost 1.

### Heurística (h(n))

La heurística calcula una **cota inferior admissible** del cost restant:

1. Identifica quins anells queden per recollir en cada nivell (bronze, plata, or).
2. Per al nivell actual (el primer no completat), calcula la distància mínima per visitar tots els objectius restants d'aquell nivell des de la posició actual, usant:
   - Per a ≤5 objectius: **permutació exhaustiva** per trobar l'ordre òptim (exacte).
   - Per a >5 objectius: **arbre d'expansió mínim (MST) de Prim** sobre els punts (admissible, és una cota inferior del camí).
3. Encadena els nivells: estima la posició final de cada nivell amb "nearest-neighbour" per calcular el cost cap al nivell següent.

**Admissibilitat**: la distància de Manhattan mai sobreestima el cost real perquè el moviment és 8-direccional (cost 1 per pas, Manhattan ≤ cost real).

### Mode Pista (HINT MODE)

Executa A* des de la posició actual i ressalta només la **primera cel·la** del camí òptim.

### Mode Déu (GOD MODE)

Executa A* des de la posició actual i ressalta **totes les cel·les** del camí òptim fins a l'anell d'or.

### Condició de derrota

El jugador perd si `cost_actual > cost_mínim_inicial + 5`. El cost mínim es calcula una sola vegada en iniciar la partida amb A* des de la posició de sortida.

---

## Part 2: Joc de Cartes (`joc_cartes.py`)

### Algorisme de decisió: Minimax amb poda Alfa-Beta

La màquina usa **Minimax** amb **poda Alfa-Beta** per decidir la millor acció cada torn.

**Profunditat**: 4 nivells (configurable amb `MINIMAX_DEPTH`).

**Funció d'utilitat**:
```
U = punts_maquina - punts_humà
```
On els punts es calculen amb pesos jeràrquics:
- Bronze: 1 punt
- Plata: 3 punts
- Or: 10 punts

Els casos terminals (guanyar/perdre) retornen ±10000.

### Accions disponibles cada torn

1. **Alliberar carta revelada** (si la jerarquia ho permet).
2. **Reservar carta revelada** (guardar-la per un torn posterior).
3. **Alliberar carta reservada** (si la jerarquia ho permet).
4. **Tornar carta al munt** (i barrejar).
5. **Bloquejar el torn de l'oponent** (usa la carta revelada).

### Poda Alfa-Beta

Redueix significativament l'espai de cerca eliminant branques que no poden influir en la decisió final. Amb profunditat 4 i 5 accions possibles, la poda redueix de ~5^4=625 a ~√625≈25 nodes en el millor cas.

---

## Conclusions

### Part 1
- L'A* amb la heurística MST/permutació és eficient per a taulers 12×12 amb 10 anells.
- La jerarquia bronze→plata→or fa que l'espai d'estats sigui manejable (2^10 = 1024 subconjunts d'anells).
- El mode déu proporciona una guia visual útil però pot ser lent si el laberint és molt complex.

### Part 2
- Minimax amb poda alfa-beta a profunditat 4 ofereix un joc desafiant sense temps de càlcul excessiu.
- La funció d'utilitat ponderada reflecteix bé la jerarquia del joc: aconseguir l'anell d'or (valor 10) és molt més important que els anells de bronze (valor 1).
- L'acció de "bloquejar" afegeix estratègia: la màquina la usarà quan l'humà estigui a punt d'alliberar cartes importants.
- La reserva de cartes permet guardar anells de plata o d'or quan la jerarquia no permet alliberar-los immediatament.
