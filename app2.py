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
    page_title="Contrôle de Python — Niveau Débutant",
    page_icon="🐍",
    layout="wide"
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES CSS (identique)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .main-title {
        text-align: center; font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, #0d47a1 0%, #42a5f5 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem; letter-spacing: -1px;
    }
    .subtitle {
        text-align: center; font-size: 1.15rem; color: #64b5f6;
        margin-bottom: 2.5rem; font-weight: 400;
    }
    .exercise-card {
        background: linear-gradient(145deg, #f3f8ff 0%, #e3f2fd 100%);
        border-radius: 16px; padding: 2rem 2.2rem;
        border: 1px solid #bbdefb; box-shadow: 0 2px 12px rgba(13,71,161,0.06);
    }
    .section-label {
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; margin-bottom: 0.8rem;
    }
    .label-qcm { background: #e3f2fd; color: #0d47a1; }
    .label-ordre { background: #fff3e0; color: #e65100; }
    .chosen-item {
        background: linear-gradient(135deg, #e1f5fe, #b3e5fc);
        border-left: 4px solid #0288d1; padding: 10px 14px;
        border-radius: 0 10px 10px 0; margin: 5px 0;
        font-family: 'Courier New', monospace; font-size: 0.95rem;
        color: #01579b; font-weight: 500;
    }
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
    .progress-container { margin-bottom: 1.2rem; }
    .progress-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
    .progress-bar-bg { height: 10px; border-radius: 5px; background: #e0e0e0; overflow: hidden; }
    .progress-bar-fill {
        height: 100%; border-radius: 5px;
        background: linear-gradient(90deg, #90caf9, #1976d2); transition: width 0.5s ease;
    }
    .info-box {
        background: #f5f5f5; border-radius: 10px; padding: 1.2rem 1.5rem;
        border: 1px solid #e0e0e0;
    }
    .result-row {
        display: flex; align-items: center; padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .result-row:last-child { border-bottom: none; }
    .num-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 28px; height: 28px; border-radius: 50%; background: #1976d2;
        color: white; font-weight: 700; font-size: 0.85rem;
        margin-right: 8px; flex-shrink: 0;
    }
    .empty-slot {
        color: #bdbdbd; font-style: italic; padding: 10px 14px;
        border: 2px dashed #e0e0e0; border-radius: 10px;
        margin: 5px 0; text-align: center;
    }
    div[data-testid="stButton"] > button {
        border-radius: 10px !important; font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
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
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

CLASSES = ["TCSL_1", "TCSF_1", "TCSF_2", "TCSF_3", "TCSF_4", "TCSF_5", "TCSF_6", "TCSF_7"]

# ══════════════════════════════════════════════════════════════════════════════
# CONTRÔLE VARIANTE : 7 EXERCICES (2 QCM + 5 MISE EN ORDRE)
# Mêmes thèmes : variables, input/print, conditions, boucles
# ══════════════════════════════════════════════════════════════════════════════
EXERCISES = [
    # QCM 1 : Conversion de type
    {
        'type': 'qcm',
        'title': 'Conversion de type',
        'question': 'Quel code permet de lire correctement un nombre entier saisi par l\'utilisateur ?',
        'options': [
            'input("Entrez un nombre : ")',
            'int(input("Entrez un nombre : "))',
            'float(input("Entrez un nombre : "))',
            'str(input("Entrez un nombre : "))'
        ],
        'correct': 1,
        'points': 4,
        'explanation': 'La fonction <b>input()</b> retourne toujours une chaîne de caractères. Pour obtenir un nombre entier, on utilise <b>int()</b> autour de input().'
    },
    # QCM 2 : Opérateur de comparaison
    {
        'type': 'qcm',
        'title': 'Conditions',
        'question': 'Quel opérateur permet de tester si deux valeurs sont égales en Python ?',
        'options': [
            '=',
            '==',
            '!=',
            '==='
        ],
        'correct': 1,
        'points': 4,
        'explanation': 'En Python, on utilise <b>==</b> pour tester l\'égalité. Le simple <b>=</b> sert à l\'affectation.'
    },
    # Ordre 1 : Demander et afficher l'âge
    {
        'type': 'ordering',
        'title': 'Demander et afficher l\'âge',
        'description': 'Placez les instructions dans l\'ordre pour demander l\'âge à l\'utilisateur, puis afficher "Tu as X ans".',
        'instructions': [
            'age = input("Quel est ton âge ? ")',
            'print(f"Tu as {age} ans")'
        ],
        'points': 4
    },
    # Ordre 2 : Vérifier la majorité
    {
        'type': 'ordering',
        'title': 'Vérifier la majorité',
        'description': 'Placez les instructions pour lire un âge, puis afficher "Majeur" si l\'âge est >= 18, sinon "Mineur".',
        'instructions': [
            'age = int(input("Entrez votre âge : "))',
            'if age >= 18:',
            '    print("Majeur")',
            'else:',
            '    print("Mineur")'
        ],
        'points': 4
    },
    # Ordre 3 : Afficher les nombres pairs de 0 à 10
    {
        'type': 'ordering',
        'title': 'Afficher les nombres pairs de 0 à 10',
        'description': 'Placez les instructions pour afficher les nombres pairs de 0 à 10 avec une boucle for.',
        'instructions': [
            'for i in range(0, 11, 2):',
            '    print(i)'
        ],
        'points': 4
    },
    # Ordre 4 : Calcul du périmètre d'un carré
    {
        'type': 'ordering',
        'title': 'Calcul du périmètre d\'un carré',
        'description': 'Placez les instructions pour lire le côté d\'un carré, calculer son périmètre (4 × côté), puis afficher le résultat.',
        'instructions': [
            'cote = float(input("Entrez la longueur du côté : "))',
            'perimetre = 4 * cote',
            'print(f"Le périmètre est : {perimetre}")'
        ],
        'points': 4,
        'swappable_groups': []  # Ordre strict ici
    },
    # Ordre 5 : Compter à rebours de 5 à 1 avec while
    {
        'type': 'ordering',
        'title': 'Compter à rebours avec while',
        'description': 'Placez les instructions pour afficher les nombres de 5 à 1 (descendant) avec une boucle while.',
        'instructions': [
            'i = 5',
            'while i >= 1:',
            '    print(i)',
            '    i -= 1'
        ],
        'points': 4
    }
]

TOTAL_POINTS = sum(ex['points'] for ex in EXERCISES)
TOTAL_EXERCISES = len(EXERCISES)

# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES & PDF (identique)
# ══════════════════════════════════════════════════════════════════════════════
def get_progress():
    return len(st.session_state.validated)

def get_current_score():
    return sum(st.session_state.scores.values())

def remove_accents(input_str):
    input_str = input_str.replace('←', '<-')
    input_str = input_str.replace('→', '->')
    input_str = input_str.replace('⟶', '->')
    input_str = input_str.replace('×', 'x')
    input_str = input_str.replace('²', '2')
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
    <div class="progress-container">
        <div class="progress-header">
            <span style="font-size:0.85rem;color:#666;">Progression</span>
            <span style="font-size:0.85rem;font-weight:600;color:#1976d2;">
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
            self.cell(0, 10, 'Controle de Python - Correction', border=False, ln=True, align='C')
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, f'Date : {datetime.now().strftime("%d/%m/%Y")}', border=False, ln=True, align='C')
            self.ln(5)

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(13, 71, 161)
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
        ex_type = "QCM" if ex['type'] == 'qcm' else "Mise en ordre"

        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(227, 242, 253)
        pdf.cell(0, 7, f'Exercice {i + 1} ({ex_type}) : {remove_accents(ex["title"])}', ln=True, fill=True)

        pdf.set_font('Helvetica', '', 9)
        pdf.cell(0, 5, f'Points obtenus : {score} / {ex["points"]}', ln=True)
        pdf.ln(2)

        if ex['type'] == 'qcm':
            user_ans = st.session_state.answers.get(i, -1)
            for j, opt in enumerate(ex['options']):
                letter = chr(65 + j)
                is_correct = j == ex['correct']
                is_user = j == user_ans

                if is_correct:
                    pdf.set_text_color(0, 128, 0)
                    pdf.set_font('Helvetica', 'B', 9)
                    symbole = "[VRAI] "
                elif is_user:
                    pdf.set_text_color(200, 0, 0)
                    pdf.set_font('Helvetica', 'B', 9)
                    symbole = "[FAUX] "
                else:
                    pdf.set_text_color(80, 80, 80)
                    pdf.set_font('Helvetica', '', 9)
                    symbole = ""

                pdf.multi_cell(0, 5, f'{symbole}{letter}) {remove_accents(opt)}')
        else:
            correct_order = list(range(len(ex['instructions'])))
            user_order = st.session_state.answers.get(i, [])

            pdf.set_text_color(0, 128, 0)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 5, 'Correction attendue :', ln=True)
            pdf.set_font('Courier', '', 8)
            pdf.set_text_color(0, 0, 0)
            for pos, idx in enumerate(correct_order):
                pdf.cell(0, 4, f'  {pos + 1}. {remove_accents(ex["instructions"][idx])}', ln=True)

            pdf.ln(2)
            pdf.set_text_color(200, 0, 0)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 5, 'Votre reponse :', ln=True)
            pdf.set_font('Courier', '', 8)
            pdf.set_text_color(0, 0, 0)
            for pos in range(len(user_order)):
                idx = user_order[pos]
                pdf.cell(0, 4, f'  {pos + 1}. {remove_accents(ex["instructions"][idx])}', ln=True)

        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    classe_folder = os.path.join("resultats_python", st.session_state.classe)
    os.makedirs(classe_folder, exist_ok=True)

    safe_nom = remove_accents(st.session_state.nom).replace(" ", "_")
    filename = f"{safe_nom}.pdf"
    full_path = os.path.join(classe_folder, filename)

    pdf.output(full_path)

    with open(full_path, "rb") as f:
        pdf_bytes = f.read()

    return full_path, io.BytesIO(pdf_bytes)

# ══════════════════════════════════════════════════════════════════════════════
# RENDU QCM (identique)
# ══════════════════════════════════════════════════════════════════════════════
def render_qcm(ex_idx):
    ex = EXERCISES[ex_idx]
    num = ex_idx + 1
    st.markdown(f"""<div class="exercise-card">
        <span class="section-label label-qcm">QCM — {ex['points']} pts</span>
        <h3 style="margin-top:0.5rem;">Question {num} : {ex['title']}</h3>
        <p style="font-size:1.05rem;font-weight:500;margin-bottom:1rem;">{ex['question']}</p>
    </div>""", unsafe_allow_html=True)

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
                st.markdown(
                    f'<div style="padding:10px 14px;color:#757575;border-radius:10px;margin:5px 0;font-size:0.95rem;">{letter}) {opt}</div>',
                    unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""<div style="background-color: #e0f7fa; padding: 12px 15px; border-radius: 8px; 
                     border-left: 4px solid #00bcd4; color: #006064;">
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
            key=f'qcm_radio_{ex_idx}',
            label_visibility="collapsed"
        )

        def validate_qcm():
            st.session_state.answers[ex_idx] = choice
            st.session_state.validated[ex_idx] = True
            st.session_state.scores[ex_idx] = ex['points'] if choice == ex['correct'] else 0

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        st.button("✅  Valider ma réponse", type='primary', key=f'val_qcm_{ex_idx}', use_container_width=True,
                  on_click=validate_qcm)

# ══════════════════════════════════════════════════════════════════════════════
# RENDU EXERCICE DE MISE EN ORDRE (identique)
# ══════════════════════════════════════════════════════════════════════════════
def render_ordering(ex_idx):
    ex = EXERCISES[ex_idx]
    num = ex_idx + 1
    key = f'ord_{ex_idx}'
    st.markdown(f"""<div class="exercise-card">
        <span class="section-label label-ordre">Mise en ordre — {ex['points']} pts</span>
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
        for pos in range(total_instr):
            user_idx = user_order[pos] if pos < len(user_order) else -1
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
                st.markdown(f'<div class="correct-item"><span class="num-badge">{pos + 1}</span>✅ {instr_text}</div>',
                            unsafe_allow_html=True)
            else:
                correct_idx = correct_order[pos]
                correct_text = ex['instructions'][correct_idx]
                st.markdown(
                    f'<div class="wrong-item"><span class="num-badge" style="background:#c62828;">{pos + 1}</span>❌ Vous : <i>{instr_text}</i><br>&nbsp;&nbsp;&nbsp;&nbsp;⟶ Correction : <b>{correct_text}</b></div>',
                    unsafe_allow_html=True)

        st.markdown("---")
        if partial_score == ex['points']:
            st.success(f"🎉 **Parfait ! {correct_count}/{total_instr} — {partial_score}/{ex['points']} pts**")
        elif partial_score > 0:
            st.warning(f"⚠️ **Partiel : {correct_count}/{total_instr} — {partial_score}/{ex['points']} pts**")
        else:
            st.error(f"❌ **Aucune position correcte — 0/{ex['points']} pts**")
        return

    def make_add_callback(idx_to_add):
        def callback():
            avail = st.session_state[key + '_available']
            if idx_to_add in avail:
                avail.remove(idx_to_add)
                st.session_state[key + '_chosen'].append(idx_to_add)
        return callback

    def make_rem_callback(pos_to_rem):
        def callback():
            chosen_list = st.session_state[key + '_chosen']
            if pos_to_rem < len(chosen_list):
                removed = chosen_list.pop(pos_to_rem)
                st.session_state[key + '_available'].append(removed)
        return callback

    def reset_all():
        indices = list(range(total_instr))
        random.shuffle(indices)
        st.session_state[key + '_available'] = indices
        st.session_state[key + '_chosen'] = []

    def validate_order():
        st.session_state.answers[ex_idx] = list(st.session_state[key + '_chosen'])
        st.session_state.validated[ex_idx] = True

    col_avail, col_chosen = st.columns(2)
    with col_avail:
        st.markdown("#### 📌 Instructions disponibles")
        st.caption("👆 Cliquez pour ajouter à votre réponse")
        if available:
            for i in available:
                st.button(f"➕  {ex['instructions'][i]}", key=f'{key}_add_{i}', use_container_width=True,
                          on_click=make_add_callback(i))
        else:
            st.success("✅ Toutes les instructions sont placées !")

    with col_chosen:
        st.markdown("#### ✅ Votre réponse (dans l’ordre)")
        st.caption("👆 Cliquez ✖ pour retirer une instruction")
        if chosen:
            for pos_idx, instr_idx in enumerate(chosen):
                c1, c2, c3 = st.columns([0.6, 7, 0.6])
                with c1:
                    st.markdown(f'<div class="num-badge">{pos_idx + 1}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="chosen-item">{ex["instructions"][instr_idx]}</div>',
                                unsafe_allow_html=True)
                with c3:
                    st.button("✖", key=f'{key}_rem_{pos_idx}', on_click=make_rem_callback(pos_idx))
        else:
            st.markdown(
                '<div class="empty-slot">Cliquez sur les instructions de gauche pour les placer dans l’ordre</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    all_placed = len(chosen) == total_instr
    c_reset, c_val = st.columns([1, 1])
    with c_reset:
        st.button("🔄  Recommencer", key=f'{key}_reset', use_container_width=True, on_click=reset_all)
    with c_val:
        st.button("✅  Valider mon ordre", type='primary', key=f'{key}_validate', use_container_width=True,
                  disabled=not all_placed, on_click=validate_order)

    if not all_placed:
        remaining = total_instr - len(chosen)
        st.info(f"⏳ Il reste {remaining} instruction(s) à placer avant de pouvoir valider.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGES (identique)
# ══════════════════════════════════════════════════════════════════════════════
def render_welcome():
    st.markdown('<p class="main-title">🐍 Contrôle de Python</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Niveau débutant — Variables, input/print, conditions et boucles</p>', unsafe_allow_html=True)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="info-box"><h4 style="margin-top:0;">📋 Informations</h4>
        <ul style="line-height:2;"><li><b>Exercices :</b> 7</li><li><b>Score brut :</b> 28 points, converti en note /20</li>
        <li><b>2 QCM</b> (8 pts) | <b>5 mises en ordre</b> (20 pts)</li></ul></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-box"><h4 style="margin-top:0;">📜 Thèmes</h4>
        <ul style="line-height:2;"><li>🔹 Types de variables et conversion</li><li>🔹 Opérateurs de comparaison</li>
        <li>🔹 Conditions if/else</li><li>🔹 Boucles for et while</li></ul></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:linear-gradient(135deg,#fff8e1,#ffecb3);border-radius:12px;padding:1rem 1.5rem;border:1px solid #ffe082;margin-top:1rem;">
    <b>⚠️ Règles :</b> Validation individuelle définitive. Points partiels pour les exercices de mise en ordre.</div>""",
                unsafe_allow_html=True)

    if not FPDF_AVAILABLE:
        st.warning(
            "⚠️ La bibliothèque `fpdf` n'est pas installée. La génération du PDF à la fin sera désactivée. Tapez `pip install fpdf` dans votre terminal.",
            icon="⚠️"
        )

    st.markdown("---")
    with st.form("start_form"):
        nom = st.text_input("👤 Nom et Prénom :", placeholder="Ex : Mohammed Amrani", label_visibility="collapsed")
        classe = st.selectbox("🏫 Classe :", options=CLASSES)
        submitted = st.form_submit_button("🚀  Commencer le contrôle", type='primary', use_container_width=True)
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
        color, bg, mention = '#c62828', '#ffebee', 'Insuffisant — À retravailler ! 💪'

    st.markdown(f'<p class="main-title">📊 Résultats du Contrôle</p>', unsafe_allow_html=True)
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
        ex_type = "QCM" if ex['type'] == 'qcm' else "Ordre"
        icon = "✅" if score == ex['points'] else ("⚠️" if score > 0 else "❌")
        pct = (score / ex['points']) * 100 if ex['points'] > 0 else 0
        bar_color = '#2e7d32' if pct == 100 else ('#f57f17' if pct > 0 else '#c62828')
        st.markdown(f"""<div class="result-row">
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
                st.success(f"✅ PDF sauvegardé sur le serveur dans : `{path}`")
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
        if st.button("🔄  Recommencer le contrôle", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()
    with c2:
        if st.button("🏠  Retour à l'accueil", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_session()
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE (identique)
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
            f"<div style='text-align:right;font-size:0.9rem;color:#1976d2;font-weight:600;'>Exercice {ex_idx + 1} / {TOTAL_EXERCISES}</div>",
            unsafe_allow_html=True)

    show_progress_bar()
    st.markdown("<br>", unsafe_allow_html=True)

    if ex['type'] == 'qcm':
        render_qcm(ex_idx)
    else:
        render_ordering(ex_idx)

    st.markdown("---")
    can_proceed = ex_idx in st.session_state.validated
    show_prev = ex_idx > 0
    is_last = ex_idx == TOTAL_EXERCISES - 1
    nav_c1, nav_c2 = st.columns([1, 1])

    with nav_c1:
        if show_prev:
            if st.button("◀  Précédent", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        else:
            st.markdown("&nbsp;")

    with nav_c2:
        if is_last:
            btn_label, btn_action = "📊  Voir mes résultats", 'finish'
        else:
            btn_label, btn_action = "Suivant  ▶", 'next'

        if st.button(btn_label, type='primary', use_container_width=True, disabled=not can_proceed):
            if btn_action == 'finish':
                st.session_state.finished = True
            else:
                st.session_state.page += 1
            st.rerun()

    if not can_proceed:
        st.info("⚠️ **Veuillez valider votre réponse avant de passer à la suite.**")s
