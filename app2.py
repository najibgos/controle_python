# app3.py - Variante "Algorithmes & Fonctions"

import streamlit as st
import random
import io
import os
from datetime import datetime
import unicodedata

# Tentative d'importation de fpdf pour le PDF
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DE LA PAGE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Contrôle de Python — Algorithmes",
    page_icon="🐍",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES CSS (similaire à l'original)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .main-title {
        text-align: center; font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, #1b5e20 0%, #66bb6a 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem; letter-spacing: -1px;
    }
    .subtitle {
        text-align: center; font-size: 1.15rem; color: #66bb6a;
        margin-bottom: 2.5rem; font-weight: 400;
    }
    .exercise-card {
        background: linear-gradient(145deg, #f1f8e9 0%, #dcedc8 100%);
        border-radius: 16px; padding: 2rem 2.2rem;
        border: 1px solid #a5d6a7; box-shadow: 0 2px 12px rgba(27,94,32,0.06);
    }
    .section-label {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; margin-bottom: 0.8rem;
    }
    .label-qcm { background: #e8f5e9; color: #1b5e20; }
    .label-code { background: #e3f2fd; color: #1565c0; }
    .label-assoc { background: #fff3e0; color: #e65100; }
    .correct-item {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        border-left: 4px solid #2e7d32; padding: 10px 14px;
        border-radius: 0 10px 10px 0; margin: 5px 0;
        font-family: 'Courier New', monospace; font-size: 0.95rem;
        color: #1b5e20; font-weight: 500;
    }
    .wrong-item {
        background: linear-gradient(135deg, #ffebee, #ffcdd2);
        border-left: 4px solid #c62828; padding: 10px 14px;
        border-radius: 0 10px 10px 0; margin: 5px 0;
        font-family: 'Courier New', monospace; font-size: 0.95rem;
        color: #b71c1c; font-weight: 500;
    }
    .score-circle {
        width: 170px; height: 170px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.8rem; font-weight: 800; margin: 0 auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .progress-bar-bg { height: 10px; border-radius: 5px; background: #e0e0e0; overflow: hidden; }
    .progress-bar-fill {
        height: 100%; border-radius: 5px;
        background: linear-gradient(90deg, #a5d6a7, #2e7d32); transition: width 0.5s ease;
    }
    .info-box {
        background: #f5f5f5; border-radius: 10px; padding: 1.2rem 1.5rem;
        border: 1px solid #e0e0e0;
    }
    div[data-testid="stButton"] > button {
        border-radius: 10px !important; font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INITIALISATION SESSION
# ══════════════════════════════════════════════════════════════════════════════
def init_session():
    defaults = {
        'page': 0,
        'nom': '',
        'classe': '',
        'started': False,
        'finished': False,
        'answers': {},
        'validated': {},
        'scores': {},
        'qcm_answers': {},
        'association_answers': {}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

CLASSES = ["TCSL_1", "TCSF_1", "TCSF_2", "TCSF_3", "TCSF_4", "TCSF_5", "TCSF_6", "TCSF_7"]

# ══════════════════════════════════════════════════════════════════════════════
# NOUVEAU CONTRÔLE : 6 EXERCICES (Algorithmes, Fonctions, Structures)
# ══════════════════════════════════════════════════════════════════════════════
EXERCISES = [
    {
        'type': 'qcm',
        'title': 'Fonctions et portée des variables',
        'question': 'Que va afficher ce code ?\n\n```python\ndef ma_fonction(x):\n    x = x + 5\n    return x\n\ny = 3\nresultat = ma_fonction(y)\nprint(resultat)\n```',
        'options': [
            '3',
            '8',
            '5',
            'Une erreur'
        ],
        'correct': 1,
        'points': 5,
        'explanation': 'La fonction ajoute 5 à la valeur passée en paramètre. y=3 est passé, donc x devient 8, retourné et affiché.'
    },
    {
        'type': 'qcm',
        'title': 'Listes en Python',
        'question': 'Quelle est la sortie de ce code ?\n\n```python\nma_liste = [1, 2, 3, 4, 5]\nprint(ma_liste[1:4])\n```',
        'options': [
            '[1, 2, 3]',
            '[2, 3, 4]',
            '[2, 3, 4, 5]',
            '[1, 2, 3, 4]'
        ],
        'correct': 1,
        'points': 5,
        'explanation': 'Le slicing [1:4] prend les éléments des indices 1, 2, 3 (exclut l\'indice 4).'
    },
    {
        'type': 'qcm',
        'title': 'Boucles et accumulations',
        'question': 'Que calcule cette fonction ?\n\n```python\ndef mystere(n):\n    s = 0\n    for i in range(1, n+1):\n        s = s + i\n    return s\n```',
        'options': [
            'Le produit de 1 à n',
            'La somme de 1 à n',
            'Le factoriel de n',
            'Le double de n'
        ],
        'correct': 1,
        'points': 5,
        'explanation': 'Cette fonction calcule la somme des entiers de 1 à n.'
    },
    {
        'type': 'code_order',
        'title': 'Calcul du factoriel',
        'description': 'Ordonnez les instructions pour calculer le factoriel d\'un nombre n (n!).',
        'instructions': [
            'def factoriel(n):',
            '    resultat = 1',
            '    for i in range(1, n + 1):',
            '        resultat = resultat * i',
            '    return resultat',
            'n = int(input("Entrez n : "))',
            'print(f"{n}! = {factoriel(n)}")'
        ],
        'points': 5,
        'swappable_groups': [[0, 5]]
    },
    {
        'type': 'code_order',
        'title': 'Nombre pair ou impair',
        'description': 'Ordonnez les instructions pour tester si un nombre est pair ou impair.',
        'instructions': [
            'nombre = int(input("Entrez un nombre : "))',
            'if nombre % 2 == 0:',
            '    print(f"{nombre} est pair")',
            'else:',
            '    print(f"{nombre} est impair")'
        ],
        'points': 5
    },
    {
        'type': 'association',
        'title': 'Associer les concepts',
        'description': 'Associez chaque expression à sa valeur ou résultat correct.',
        'pairs': [
            ('len([1, 2, 3, 4])', '4'),
            ('max([10, 25, 5, 30])', '30'),
            ('min([7, 3, 9, 2])', '2'),
            ('sum([1, 2, 3, 4])', '10'),
            ('"Python"[0:3]', '"Pyt"')
        ],
        'points': 5
    }
]

TOTAL_POINTS = sum(ex['points'] for ex in EXERCISES)
TOTAL_EXERCISES = len(EXERCISES)

# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════
def get_progress():
    return len(st.session_state.validated)

def get_current_score():
    return sum(st.session_state.scores.values())

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    ascii_text = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    try:
        return ascii_text.encode("latin-1", "ignore").decode("latin-1")
    except Exception:
        return ascii_text

def show_progress_bar():
    progress = get_progress() / TOTAL_EXERCISES
    score = get_current_score()
    st.markdown(f"""
    <div style="margin-bottom: 1.2rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="font-size:0.85rem;color:#666;">Progression</span>
            <span style="font-size:0.85rem;font-weight:600;color:#2e7d32;">
                {get_progress()}/{TOTAL_EXERCISES} exercices &nbsp;|&nbsp; Score : {score}/{TOTAL_POINTS}
            </span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{progress * 100}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_pdf_report():
    if not FPDF_AVAILABLE:
        return None, None

    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 12)
            self.cell(0, 10, 'Controle de Python - Algorithmes et Fonctions', border=False, ln=True, align='C')
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, f'Date : {datetime.now().strftime("%d/%m/%Y")}', border=False, ln=True, align='C')
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(27, 94, 32)
    pdf.cell(0, 8, f'Nom et Prenom : {remove_accents(st.session_state.nom)}', ln=True)
    pdf.cell(0, 8, f'Classe : {remove_accents(st.session_state.classe)}', ln=True)

    total_score = get_current_score()
    note_20 = round(total_score / TOTAL_POINTS * 20, 2)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(200, 50, 50)
    pdf.cell(0, 10, f'Note Finale : {note_20} / 20', ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    for i, ex in enumerate(EXERCISES):
        if pdf.get_y() > 250:
            pdf.add_page()

        score = st.session_state.scores.get(i, 0)
        
        if ex['type'] == 'qcm':
            ex_type = "QCM"
        elif ex['type'] == 'code_order':
            ex_type = "Mise en ordre"
        else:
            ex_type = "Association"

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(232, 245, 233)
        pdf.cell(0, 7, f'Exercice {i + 1} ({ex_type}) : {remove_accents(ex["title"])}', ln=True, fill=True)

        pdf.set_font('Helvetica', '', 9)
        pdf.cell(0, 5, f'Points obtenus : {score} / {ex["points"]}', ln=True)
        pdf.ln(2)

    classe_folder = os.path.join("resultats_python_variante", st.session_state.classe)
    os.makedirs(classe_folder, exist_ok=True)

    safe_nom = remove_accents(st.session_state.nom).replace(" ", "_")
    filename = f"{safe_nom}.pdf"
    full_path = os.path.join(classe_folder, filename)

    pdf.output(full_path)

    with open(full_path, "rb") as f:
        pdf_bytes = f.read()

    return full_path, io.BytesIO(pdf_bytes)

# ══════════════════════════════════════════════════════════════════════════════
# RENDU QCM
# ══════════════════════════════════════════════════════════════════════════════
def render_qcm(ex_idx):
    ex = EXERCISES[ex_idx]
    num = ex_idx + 1
    st.markdown(f"""<div class="exercise-card">
        <span class="section-label label-qcm">QCM — {ex['points']} pts</span>
        <h3 style="margin-top:0.5rem;">Question {num} : {ex['title']}</h3>
    </div>""", unsafe_allow_html=True)
    
    st.markdown(ex['question'])
    st.markdown("<br>", unsafe_allow_html=True)

    is_validated = ex_idx in st.session_state.validated
    if is_validated:
        user_answer = st.session_state.answers[ex_idx]
        is_correct = st.session_state.scores[ex_idx] == ex['points']
        for i, opt in enumerate(ex['options']):
            letter = chr(65 + i)
            if i == ex['correct']:
                st.markdown(f'<div class="correct-item">✅ {letter}) {opt}</div>', unsafe_allow_html=True)
            elif i == user_answer and not is_correct:
                st.markdown(f'<div class="wrong-item">❌ {letter}) {opt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="padding:10px 14px;color:#757575;">{letter}) {opt}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"""<div style="background-color: #e8f5e9; padding: 12px 15px; border-radius: 8px; 
                     border-left: 4px solid #4caf50; color: #1b5e20;">
                     💡 <b>Explication :</b> {ex['explanation']}
                     </div>""", unsafe_allow_html=True)

        if is_correct:
            st.success(f"✅ **Bonne réponse ! +{ex['points']} points**")
        else:
            st.error(f"❌ **Mauvaise réponse. 0/{ex['points']} point**")
    else:
        choice = st.radio(
            "Sélectionnez votre réponse :",
            range(len(ex['options'])),
            format_func=lambda i: f"{chr(65 + i)}) {ex['options'][i]}",
            key=f'qcm_{ex_idx}',
            label_visibility="collapsed"
        )

        def validate_qcm():
            st.session_state.answers[ex_idx] = choice
            st.session_state.validated[ex_idx] = True
            st.session_state.scores[ex_idx] = ex['points'] if choice == ex['correct'] else 0

        st.button("✅ Valider ma réponse", type='primary', key=f'val_qcm_{ex_idx}', 
                 use_container_width=True, on_click=validate_qcm)

# ══════════════════════════════════════════════════════════════════════════════
# RENDU EXERCICE DE MISE EN ORDRE DE CODE
# ══════════════════════════════════════════════════════════════════════════════
def render_code_order(ex_idx):
    ex = EXERCISES[ex_idx]
    num = ex_idx + 1
    key = f'code_{ex_idx}'
    st.markdown(f"""<div class="exercise-card">
        <span class="section-label label-code">Mise en ordre — {ex['points']} pts</span>
        <h3 style="margin-top:0.5rem;">Exercice {num} : {ex['title']}</h3>
        <p style="margin-top:0.5rem;">{ex['description']}</p>
    </div>""", unsafe_allow_html=True)

    if key + '_init' not in st.session_state:
        indices = list(range(len(ex['instructions'])))
        random.shuffle(indices)
        st.session_state[key + '_available'] = indices
        st.session_state[key + '_chosen'] = []
        st.session_state[key + '_init'] = True

    is_validated = ex_idx in st.session_state.validated
    available = st.session_state[key + '_available']
    chosen = st.session_state[key + '_chosen']
    total_instr = len(ex['instructions'])

    if is_validated:
        user_order = st.session_state.answers[ex_idx]
        correct_order = list(range(total_instr))

        swappable_groups = ex.get('swappable_groups', [])

        valid_options_at_pos = {i: {i} for i in range(total_instr)}
        for group in swappable_groups:
            group_set = set(group)
            for pos in group:
                valid_options_at_pos[pos] = group_set

        correct_count = 0
        for pos in range(min(len(user_order), total_instr)):
            user_idx = user_order[pos]
            if user_idx in valid_options_at_pos.get(pos, set()):
                correct_count += 1

        partial_score = round(correct_count / total_instr * ex['points'] * 2) / 2
        st.session_state.scores[ex_idx] = partial_score

        st.markdown("#### 📋 Correction détaillée")
        for pos in range(total_instr):
            user_idx = user_order[pos] if pos < len(user_order) else -1
            is_pos_correct = user_idx in valid_options_at_pos.get(pos, set())

            instr_text = ex['instructions'][user_idx] if 0 <= user_idx < total_instr else "(vide)"

            if is_pos_correct:
                st.markdown(f'<div class="correct-item"><span style="background:#2e7d32;color:white;border-radius:50%;display:inline-block;width:24px;text-align:center;margin-right:8px;">{pos + 1}</span>✅ {instr_text}</div>',
                           unsafe_allow_html=True)
            else:
                correct_idx = correct_order[pos]
                correct_text = ex['instructions'][correct_idx]
                st.markdown(
                    f'<div class="wrong-item"><span style="background:#c62828;color:white;border-radius:50%;display:inline-block;width:24px;text-align:center;margin-right:8px;">{pos + 1}</span>❌ Vous : <i>{instr_text}</i><br>&nbsp;&nbsp;&nbsp;&nbsp;⟶ <b>{correct_text}</b></div>',
                    unsafe_allow_html=True)

        st.markdown("---")
        if partial_score == ex['points']:
            st.success(f"🎉 **Parfait ! {partial_score}/{ex['points']} pts**")
        elif partial_score > 0:
            st.warning(f"⚠️ **Partiel : {partial_score}/{ex['points']} pts**")
        else:
            st.error(f"❌ **Aucune position correcte — 0/{ex['points']} pts**")
        return

    col_avail, col_chosen = st.columns(2)
    with col_avail:
        st.markdown("#### 📌 Blocs disponibles")
        if available:
            for i in available:
                st.code(ex['instructions'][i], language='python')
                if st.button(f"➕ Ajouter", key=f'{key}_add_{i}'):
                    st.session_state[key + '_available'].remove(i)
                    st.session_state[key + '_chosen'].append(i)
                    st.rerun()
        else:
            st.success("✅ Tous les blocs sont placés !")

    with col_chosen:
        st.markdown("#### ✅ Votre ordre")
        if chosen:
            for pos_idx, instr_idx in enumerate(chosen):
                col1, col2 = st.columns([1, 10])
                with col1:
                    st.markdown(f"**{pos_idx + 1}**")
                with col2:
                    st.code(ex['instructions'][instr_idx], language='python')
                if st.button(f"✖ Retirer", key=f'{key}_rem_{pos_idx}'):
                    removed = st.session_state[key + '_chosen'].pop(pos_idx)
                    st.session_state[key + '_available'].append(removed)
                    st.rerun()
        else:
            st.info("Cliquez sur les blocs de gauche pour les ordonner")

    st.markdown("---")
    all_placed = len(chosen) == total_instr
    c_reset, c_val = st.columns([1, 1])
    with c_reset:
        if st.button("🔄 Recommencer", key=f'{key}_reset', use_container_width=True):
            indices = list(range(total_instr))
            random.shuffle(indices)
            st.session_state[key + '_available'] = indices
            st.session_state[key + '_chosen'] = []
            st.rerun()
    with c_val:
        if st.button("✅ Valider mon ordre", type='primary', key=f'{key}_validate', 
                    use_container_width=True, disabled=not all_placed):
            st.session_state.answers[ex_idx] = list(st.session_state[key + '_chosen'])
            st.session_state.validated[ex_idx] = True
            st.rerun()

    if not all_placed:
        remaining = total_instr - len(chosen)
        st.info(f"⏳ Il reste {remaining} bloc(s) à placer.")

# ══════════════════════════════════════════════════════════════════════════════
# RENDU EXERCICE D'ASSOCIATION
# ══════════════════════════════════════════════════════════════════════════════
def render_association(ex_idx):
    ex = EXERCISES[ex_idx]
    num = ex_idx + 1
    key = f'assoc_{ex_idx}'
    
    st.markdown(f"""<div class="exercise-card">
        <span class="section-label label-assoc">Association — {ex['points']} pts</span>
        <h3 style="margin-top:0.5rem;">Exercice {num} : {ex['title']}</h3>
        <p>{ex['description']}</p>
    </div>""", unsafe_allow_html=True)

    is_validated = ex_idx in st.session_state.validated
    
    if key + '_answers' not in st.session_state:
        pairs = ex['pairs']
        expressions = [p[0] for p in pairs]
        correct_values = [p[1] for p in pairs]
        shuffled_values = correct_values.copy()
        random.shuffle(shuffled_values)
        st.session_state[key + '_expressions'] = expressions
        st.session_state[key + '_values'] = shuffled_values
        st.session_state[key + '_matches'] = {}
        st.session_state[key + '_available_values'] = shuffled_values.copy()

    expressions = st.session_state[key + '_expressions']
    available_values = st.session_state[key + '_available_values']
    matches = st.session_state[key + '_matches']

    if is_validated:
        total_pairs = len(expressions)
        correct_matches = 0
        for i, expr in enumerate(expressions):
            if matches.get(i) == ex['pairs'][i][1]:
                correct_matches += 1
        
        score = round(correct_matches / total_pairs * ex['points'])
        st.session_state.scores[ex_idx] = score
        
        st.markdown("#### 📋 Résultats")
        for i, expr in enumerate(expressions):
            user_match = matches.get(i, "Non associé")
            correct_match = ex['pairs'][i][1]
            if user_match == correct_match:
                st.markdown(f'<div class="correct-item">✅ {expr} → {user_match}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="wrong-item">❌ {expr} → {user_match} (correction: {correct_match})</div>', unsafe_allow_html=True)
        
        if score == ex['points']:
            st.success(f"🎉 **Parfait ! {score}/{ex['points']} pts**")
        else:
            st.warning(f"⚠️ **{score}/{ex['points']} pts**")
        return

    st.markdown("#### Associez chaque expression à sa valeur :")
    
    for i, expr in enumerate(expressions):
        st.markdown(f"**{expr}**")
        
        if i in matches:
            current_value = matches[i]
            remaining_values = [v for v in available_values if v != current_value] + [current_value]
        else:
            current_value = None
            remaining_values = available_values.copy()
        
        options = [""] + remaining_values
        selected = st.selectbox(
            f"Valeur pour {expr}",
            options=options,
            index=options.index(current_value) if current_value in options else 0,
            key=f"{key}_select_{i}",
            label_visibility="collapsed"
        )
        
        if selected and selected != current_value:
            if i in matches:
                old_value = matches[i]
                if old_value not in available_values:
                    available_values.append(old_value)
            matches[i] = selected
            if selected in available_values:
                available_values.remove(selected)
            st.rerun()
        elif not selected and i in matches:
            old_value = matches[i]
            del matches[i]
            if old_value not in available_values:
                available_values.append(old_value)
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

    all_matched = len(matches) == len(expressions)
    
    if st.button("✅ Valider mes associations", type='primary', disabled=not all_matched):
        st.session_state.answers[ex_idx] = matches
        st.session_state.validated[ex_idx] = True
        st.rerun()
    
    if not all_matched:
        remaining = len(expressions) - len(matches)
        st.info(f"⏳ Il reste {remaining} association(s) à faire.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════
def render_welcome():
    st.markdown('<p class="main-title">🐍 Contrôle de Python</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Algorithmes, Fonctions et Structures de données</p>', unsafe_allow_html=True)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="info-box"><h4 style="margin-top:0;">📋 Informations</h4>
        <ul><li><b>Exercices :</b> 6</li><li><b>Score brut :</b> 30 points, converti en note /20</li>
        <li><b>3 QCM</b> (15 pts) | <b>2 Mises en ordre</b> (10 pts) | <b>1 Association</b> (5 pts)</li></ul></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-box"><h4 style="margin-top:0;">📜 Thèmes</h4>
        <ul><li>🔹 Fonctions et portée des variables</li><li>🔹 Listes et slicing</li>
        <li>🔹 Boucles for et accumulations</li><li>🔹 Conditions (pair/impair)</li><li>🔹 Fonctions sur les listes (len, max, min, sum)</li></ul></div>""", unsafe_allow_html=True)

    if not FPDF_AVAILABLE:
        st.warning("⚠️ La bibliothèque `fpdf` n'est pas installée. Tapez `pip install fpdf` dans votre terminal.", icon="⚠️")

    st.markdown("---")
    with st.form("start_form"):
        nom = st.text_input("👤 Nom et Prénom :", placeholder="Ex : Fatima Zahra", label_visibility="collapsed")
        classe = st.selectbox("🏫 Classe :", options=CLASSES)
        submitted = st.form_submit_button("🚀 Commencer le contrôle", type='primary', use_container_width=True)
        if submitted:
            if nom.strip():
                st.session_state.nom = nom.strip()
                st.session_state.classe = classe
                st.session_state.started = True
                st.session_state.page = 1
                st.rerun()
            else:
                st.error("⚠️ Veuillez remplir le nom.")

def render_results():
    total_score = get_current_score()
    note_20 = round(total_score / TOTAL_POINTS * 20, 2)
    percentage = (total_score / TOTAL_POINTS) * 100

    if percentage >= 80:
        color, bg, mention = '#2e7d32', '#e8f5e9', 'Excellent ! 🌟'
    elif percentage >= 60:
        color, bg, mention = '#f57f17', '#fff8e1', 'Bien ! 👍'
    elif percentage >= 40:
        color, bg, mention = '#e65100', '#fff3e0', 'Passable 📝'
    else:
        color, bg, mention = '#c62828', '#ffebee', 'À retravailler ! 💪'

    st.markdown('<p class="main-title">📊 Résultats du Contrôle</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="subtitle">Élève : <strong>{st.session_state.nom}</strong> | Classe : <strong>{st.session_state.classe}</strong></p>',
        unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"""<div style="text-align:center;margin:1.5rem 0 2rem 0;">
        <div class="score-circle" style="background:{bg};color:{color};border:4px solid {color};">{note_20}</div>
        <p style="font-size:1.4rem;font-weight:700;color:{color};margin-top:0.8rem;">{mention}</p>
        <p style="font-size:0.95rem;color:#666;">Score brut : {total_score} / {TOTAL_POINTS} points</p></div>""",
                unsafe_allow_html=True)

    st.markdown("#### 📋 Détail par exercice")
    st.markdown('<div style="background:#fafafa;border-radius:12px;padding:1rem 1.5rem;border:1px solid #eee;">',
                unsafe_allow_html=True)
    for i, ex in enumerate(EXERCISES):
        score = st.session_state.scores.get(i, 0)
        if ex['type'] == 'qcm':
            ex_type = "QCM"
        elif ex['type'] == 'code_order':
            ex_type = "Ordre"
        else:
            ex_type = "Assoc"
        icon = "✅" if score == ex['points'] else ("⚠️" if score > 0 else "❌")
        pct = (score / ex['points']) * 100 if ex['points'] > 0 else 0
        bar_color = '#2e7d32' if pct == 100 else ('#f57f17' if pct > 0 else '#c62828')
        st.markdown(f"""<div style="display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
            <span style="margin-right:10px;font-size:1.1rem;">{icon}</span>
            <span style="flex:1;font-weight:500;"><span style="color:#999;font-size:0.8rem;margin-right:6px;">[{ex_type}]</span>Ex {i + 1} : {ex['title']}</span>
            <div style="width:100px;margin:0 15px;"><div style="height:6px;border-radius:3px;background:#eee;overflow:hidden;"><div style="height:100%;width:{pct}%;background:{bar_color};border-radius:3px;"></div></div></div>
            <span style="font-weight:700;color:{bar_color};min-width:60px;text-align:right;">{score}/{ex['points']}</span></div>""",
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    if FPDF_AVAILABLE:
        if st.button("📄 Générer et enregistrer le PDF", type="primary"):
            path, pdf_buffer = generate_pdf_report()
            if path:
                st.success(f"✅ PDF sauvegardé : `{path}`")
                st.download_button(
                    label="⬇️ Télécharger ma copie",
                    data=pdf_buffer,
                    file_name=os.path.basename(path),
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.info("Installation de `fpdf` requise pour générer le PDF (`pip install fpdf`).")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 Recommencer", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()
    with c2:
        if st.button("🏠 Retour à l'accueil", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.started:
    render_welcome()
elif st.session_state.finished:
    render_results()
else:
    ex_idx = st.session_state.page - 1
    ex = EXERCISES[ex_idx]

    header_cols = st.columns([3, 1])
    with header_cols[0]:
        st.markdown(f"👤 **{st.session_state.nom}** ({st.session_state.classe})")
    with header_cols[1]:
        st.markdown(
            f"<div style='text-align:right;font-size:0.9rem;color:#2e7d32;font-weight:600;'>Exercice {ex_idx + 1} / {TOTAL_EXERCISES}</div>",
            unsafe_allow_html=True)

    show_progress_bar()
    st.markdown("<br>", unsafe_allow_html=True)

    if ex['type'] == 'qcm':
        render_qcm(ex_idx)
    elif ex['type'] == 'code_order':
        render_code_order(ex_idx)
    else:
        render_association(ex_idx)

    st.markdown("---")
    can_proceed = ex_idx in st.session_state.validated
    show_prev = ex_idx > 0
    is_last = ex_idx == TOTAL_EXERCISES - 1
    nav_c1, nav_c2 = st.columns([1, 1])

    with nav_c1:
        if show_prev:
            if st.button("◀ Précédent", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()

    with nav_c2:
        if is_last:
            btn_label = "📊 Voir mes résultats"
            if st.button(btn_label, type='primary', use_container_width=True, disabled=not can_proceed):
                st.session_state.finished = True
                st.rerun()
        else:
            btn_label = "Suivant ▶"
            if st.button(btn_label, type='primary', use_container_width=True, disabled=not can_proceed):
                st.session_state.page += 1
                st.rerun()

    if not can_proceed:
        st.info("⚠️ **Veuillez valider votre réponse avant de passer à la suite.**")
