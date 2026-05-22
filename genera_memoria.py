"""Script per generar la memòria en format Word (.docx)."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# ── Estils globals ──────────────────────────────────────────────────────────
style_normal = doc.styles['Normal']
style_normal.font.name = 'Calibri'
style_normal.font.size = Pt(11)

def heading1(text):
    p = doc.add_heading(text, level=1)
    p.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    return p

def heading2(text):
    p = doc.add_heading(text, level=2)
    p.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    return p

def heading3(text):
    p = doc.add_heading(text, level=3)
    p.runs[0].font.color.rgb = RGBColor(0x5B, 0x9B, 0xD5)
    return p

def para(text, bold_parts=None):
    """Afegeix un paràgraf. bold_parts és una llista de substrings a posar en negreta."""
    p = doc.add_paragraph()
    if bold_parts:
        remaining = text
        for bp in bold_parts:
            idx = remaining.find(bp)
            if idx == -1:
                continue
            if idx > 0:
                p.add_run(remaining[:idx])
            r = p.add_run(bp)
            r.bold = True
            remaining = remaining[idx + len(bp):]
        if remaining:
            p.add_run(remaining)
    else:
        p.add_run(text)
    return p

def bullet(text, bold_start=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_start:
        r = p.add_run(bold_start)
        r.bold = True
        p.add_run(text[len(bold_start):])
    else:
        p.add_run(text)
    return p

def code_block(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Courier New'
    r.font.size = Pt(9)
    p.paragraph_format.left_indent = Inches(0.4)
    return p

# ── Portada ─────────────────────────────────────────────────────────────────
title = doc.add_heading('Memòria — El Senyor dels Anells', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.runs[0].font.color.rgb = RGBColor(0xC5, 0x9A, 0x00)

sub = doc.add_paragraph('Tècniques d\'Intel·ligència Artificial — Pràctica 2 (2026)')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.runs[0].font.size = Pt(12)
sub.runs[0].font.color.rgb = RGBColor(0x40, 0x40, 0x40)

doc.add_paragraph()

# ── PART 1 ──────────────────────────────────────────────────────────────────
heading1('Part 1: El Laberint de l\'Anell d\'Or (laberint.py)')

heading2('Algorisme de cerca: A*')

para(
    'S\'utilitza l\'algorisme A* per trobar el camí de cost mínim des de la posició '
    'actual del jugador fins a recollir tots els anells en ordre jeràrquic '
    '(bronze → plata → or).',
    bold_parts=['A*']
)

para('Estat de l\'A*: (posició_jugador, frozenset_d\'anells_recollits)')
para(
    'Funció de cost: cada moviment (4 direccions: amunt, avall, esquerra, dreta) '
    'té cost 1. No es permet el moviment diagonal.',
    bold_parts=['Funció de cost:']
)

heading2('Heurística (h(n))')

para(
    'La heurística calcula una cota inferior admissible del cost restant:',
    bold_parts=['cota inferior admissible']
)

bullet('Identifica quins anells queden per recollir en cada nivell (bronze, plata, or).')
bullet(
    'Per al nivell actual (el primer no completat), calcula la distància mínima per '
    'visitar tots els objectius restants usant:'
)
p = doc.add_paragraph(style='List Bullet 2')
p.add_run('Per a ≤5 objectius: ').bold = False
r = p.add_run('permutació exhaustiva')
r.bold = True
p.add_run(' per trobar l\'ordre òptim (cost exacte).')

p = doc.add_paragraph(style='List Bullet 2')
p.add_run('Per a >5 objectius: ').bold = False
r = p.add_run('arbre d\'expansió mínim (MST) de Prim')
r.bold = True
p.add_run(' sobre els punts (cota inferior admissible).')

bullet('Encadena els nivells usant nearest-neighbour per estimar la posició final de cada nivell.')

heading3('Admissibilitat')

para(
    'Amb moviment estrictament 4-direccional (sense diagonals), la distància de Manhattan '
    'és exactament admissible i consistent: el cost real d\'anar d\'un punt a un altre sense '
    'barreres és exactament la distància de Manhattan, i les barreres només poden '
    'augmentar-lo, mai reduir-lo. Per tant, h(n) ≤ cost real sempre.',
    bold_parts=['distància de Manhattan', 'h(n) ≤ cost real sempre']
)

heading3('Justificació de l\'elecció d\'A*')

para(
    'S\'ha escollit A* davant d\'altres algorismes de cerca informada pels motius següents:'
)
bullet('Optimalitat: A* garanteix trobar el camí de cost mínim si la heurística és admissible.')
bullet('Eficiència: la heurística MST/permutació redueix significativament l\'espai explorat respecte a BFS.')
bullet(
    'Espai d\'estats manejable: amb 10 anells, hi ha 2¹⁰ = 1.024 subconjunts possibles '
    '× 144 posicions = ~147.000 estats màxims.'
)
bullet('Greedy Best-First no garanteix optimalitat; UCS (Dijkstra) és equivalent a A* amb h=0, menys eficient.')

heading2('Mode Pista (HINT MODE)')

para(
    'Executa A* des de la posició actual i ressalta en groc únicament la primera '
    'cel·la del camí òptim. El jugador sap cap a on moure\'s al següent pas.',
    bold_parts=['primera cel·la']
)

heading2('Mode Déu (GOD MODE)')

para(
    'Executa A* des de la posició actual i ressalta en verd totes les cel·les '
    'del camí òptim fins a recollir l\'anell d\'or.',
    bold_parts=['totes les cel·les']
)

heading2('Condició de derrota')

para(
    'El jugador perd si cost_actual > cost_mínim_inicial + 5. '
    'El cost mínim es calcula una sola vegada en iniciar la partida amb A* '
    'des de la posició de sortida.',
    bold_parts=['cost_actual > cost_mínim_inicial + 5']
)

doc.add_page_break()

# ── PART 2 ──────────────────────────────────────────────────────────────────
heading1('Part 2: Joc de Cartes (joc_cartes.py)')

heading2('Algorisme de decisió: Minimax amb poda Alfa-Beta')

para(
    'La màquina usa Minimax amb poda Alfa-Beta per decidir la millor acció cada torn.',
    bold_parts=['Minimax amb poda Alfa-Beta']
)
para('Profunditat: 4 nivells (configurable amb MINIMAX_DEPTH).', bold_parts=['Profunditat:'])

heading2('Funció d\'utilitat')

para('La funció d\'utilitat avalua l\'estat del joc des de la perspectiva de la màquina:')
code_block('U = punts_maquina - punts_humà')
para('On els punts es calculen amb pesos jeràrquics:')
bullet('Bronze: 1 punt — anells bàsics, necessaris però de poc valor estratègic.')
bullet('Plata: 3 punts — anells intermedis, clau per desbloquear l\'or.')
bullet('Or: 10 punts — objectiu final, pes molt superior per reflectir la seva importància.')
para('Els casos terminals retornen ±10.000, garantint que guanyar/perdre sempre domina qualsevol altra avaluació.', bold_parts=['±10.000'])

heading2('Accions disponibles cada torn')

bullet('Alliberar carta revelada — si la jerarquia ho permet.')
bullet('Reservar carta revelada — guardar-la per un torn posterior.')
bullet('Alliberar carta reservada — si ara ja es pot alliberar.')
bullet('Tornar carta al munt — retornar-la i barrejar.')
bullet('Bloquejar el torn de l\'oponent — sacrifica la carta per bloquejar.')

heading2('Justificació de la poda Alfa-Beta')

para(
    'La poda Alfa-Beta és una optimització de Minimax que elimina branques que '
    'no poden influir en la decisió final sense afectar el resultat òptim.',
    bold_parts=['Alfa-Beta']
)
bullet(
    'Amb profunditat 4 i 5 accions possibles, Minimax pur explora 5⁴ = 625 nodes.'
)
bullet(
    'Alfa-Beta en el millor cas redueix a √625 ≈ 25 nodes (poda perfecta), '
    'i en el cas mitjà a ~5² = 25–100 nodes.'
)
bullet(
    'Sense poda, la màquina trigaria massa a cada torn; amb poda la resposta és immediata.'
)

para(
    'Es va descartar MCTS (Monte Carlo Tree Search) perquè l\'espai de joc és petit '
    'i determinista, i Minimax amb Alfa-Beta és suficient i més precís.',
    bold_parts=['MCTS']
)

doc.add_page_break()

# ── CONCLUSIONS ─────────────────────────────────────────────────────────────
heading1('Conclusions')

heading2('Problemes tècnics i conceptuals trobats')

bullet(
    'Moviment diagonal: inicialment el codi incloïa 8 direccions, però l\'enunciat '
    'especifica "casella adjacent" sense diagonals. S\'ha restringit a 4 direccions '
    'ortogonals, cosa que fa la heurística de Manhattan consistent i exacta.'
)
bullet(
    'Compatibilitat de pygame a Windows: Python 3.13/3.14 no té wheels pre-compilats '
    'de pygame. Solució: usar Python 3.11 o 3.12 amb pip install pygame --prefer-binary.'
)
bullet(
    'Espai d\'estats del A*: amb 10 anells i 144 caselles, l\'espai pot ser gran. '
    'La heurística MST/permutació el redueix considerablement.'
)

heading2('Com s\'han solucionat els reptes')

bullet('Diagonal: canvi a DIRECTIONS = 4 ortogonals + eliminació de tecles Q/E/Z/C.')
bullet('Pygame: documentació al README amb la comanda correcta per a cada versió de Python.')
bullet('Eficiència A*: permutació exacta per a ≤5 objectius, MST de Prim per a més.')

heading2('Què milloraríem amb més temps')

bullet('Animació visual del moviment del jugador per fer el joc més fluid.')
bullet('Mode multijugador en xarxa per al laberint.')
bullet('Nivells de dificultat configurables (mida del tauler, nombre de barreres).')
bullet('Millora de la IA del joc de cartes amb MCTS per a profunditats majors.')
bullet('Interfície gràfica més polida amb imatges d\'anells reals.')

# ── Desa ────────────────────────────────────────────────────────────────────
doc.save('memoria.docx')
print("Fitxer memoria.docx generat correctament.")
