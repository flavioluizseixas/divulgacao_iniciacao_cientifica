# app.py
# Portal público de Projetos de Iniciação Científica e Extensão (UFF/PROEX)
# Compatível com Streamlit 1.53+
#
# Como rodar:
#   pip install -U streamlit pandas openpyxl
#   streamlit run app.py
#
# Requer: modelo_projetos_ic_extensao_v2.xlsx na mesma pasta (ou ajuste ARQ_EXCEL)

import os
import base64
import html as html_lib
import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Projetos IC & Extensão — UFF/PROEX", layout="wide")

ARQ_EXCEL = "modelo_projetos_ic_extensao_v2.xlsx"
ABA = "projetos"

LOGO_PATH = "assets/uff_proex_logo.png"  # opcional

BRAND_GREEN = "#1F6F4A"
BRAND_GREEN_DARK = "#15553A"
BG = "#F6F7F8"

CARD_IMG_HEIGHT = 165
GRID_COLS = 3

# =========================
# CSS
# =========================
st.markdown(
    f"""
<style>
html, body, [class*="css"] {{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}}
.stApp {{ background: {BG}; }}
.block-container {{ padding-top: 0.9rem; }}

.ribbon {{
  height: 10px;
  background: linear-gradient(90deg, {BRAND_GREEN}, {BRAND_GREEN_DARK});
  border-radius: 999px;
  margin-bottom: 14px;
}}

.header {{
  display:flex; align-items:center; justify-content:space-between;
  gap: 14px;
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 16px 18px;
  box-shadow: 0 8px 22px rgba(0,0,0,0.06);
}}
.header h1 {{ font-size: 26px; margin: 0; }}
.header p {{ margin: 6px 0 0 0; color: rgba(0,0,0,0.65); }}

.kpi-wrap {{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
  margin-bottom: 14px;
}}
.kpi {{
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: 12px 14px;
  box-shadow: 0 8px 18px rgba(0,0,0,0.05);
}}
.kpi .label {{
  color: rgba(0,0,0,0.62);
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .04em;
}}
.kpi .value {{
  font-size: 26px;
  font-weight: 950;
  margin-top: 2px;
}}
.kpi .hint {{
  color: rgba(0,0,0,0.55);
  font-size: 12px;
  margin-top: 4px;
}}

/* Container com border=True (usado nos filtros) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: white !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
  border-radius: 18px !important;
  padding: 14px !important;
  box-shadow: 0 8px 18px rgba(0,0,0,0.05) !important;
  margin-bottom: 12px !important;
}}

/* Chips */
.chip-btn button,
.chip-btn-active button {{
  border-radius: 999px !important;
  height: 36px !important;
  padding: 0 16px !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
  background: #fff !important;
  font-size: 0.90rem !important;
  font-weight: 950 !important;
  line-height: 36px !important;
  box-shadow: none !important;
  margin: 0 !important;
}}
.chip-btn button {{
  color: rgba(0,0,0,0.78) !important;
}}
.chip-btn button:hover {{
  background: rgba(0,0,0,0.03) !important;
}}
.chip-btn-active button {{
  background: {BRAND_GREEN} !important;
  color: #fff !important;
  border-color: {BRAND_GREEN} !important;
}}
.chip-btn-active button:hover {{
  background: {BRAND_GREEN_DARK} !important;
  border-color: {BRAND_GREEN_DARK} !important;
}}

/* Card HTML */
.cardwrap {{
  position: relative;
  margin-bottom: 14px;
}}
.card {{
  background:#fff;
  border-radius:18px;
  padding:14px;
  border:1px solid rgba(0,0,0,0.06);
  box-shadow:0 10px 24px rgba(0,0,0,0.07);
  transition: transform 140ms ease, box-shadow 140ms ease;
}}
.card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(0,0,0,0.10);
}}
.card-title {{
  font-size:18px;
  font-weight:950;
  margin-top:10px;
  margin-bottom:6px;
}}
.card-sub {{
  color: rgba(0,0,0,0.65);
  font-size:14px;
  min-height:44px;
}}
.badges {{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  margin-top:6px;
  margin-bottom:10px;
}}
.badge {{
  display:inline-block;
  padding:4px 10px;
  border-radius:999px;
  font-size:12px;
  font-weight:950;
  border:1px solid rgba(0,0,0,0.08);
}}
.b-cat {{ background:#fff7ed; color:#9a3412; }}
.b-periodo {{ background:#f5f3ff; color:#5b21b6; }}
.b-novo {{ background:#e3f2fd; color:#1565c0; }}
.b-andamento {{ background:#e8f5e9; color:#2e7d32; }}
.b-encerrado {{ background:#eeeeee; color:#424242; }}
.b-abertas {{ background:#d1fae5; color:#065f46; }}
.b-encerradas {{ background:#fee2e2; color:#991b1b; }}

.card-img {{
  width:100%;
  height: {CARD_IMG_HEIGHT}px;
  border-radius:14px;
  overflow:hidden;
  background: rgba(0,0,0,0.04);
}}
.card-img img {{
  width:100%;
  height:100%;
  object-fit:cover;
  display:block;
}}

/* Botão invisível por cima do card (para clique abrir modal) */
.cardwrap .open-overlay {{
  position: absolute;
  inset: 0;
  z-index: 50;
}}
.cardwrap .open-overlay button {{
  width: 100% !important;
  height: 100% !important;
  opacity: 0 !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}}
.cardwrap .open-overlay button:focus {{
  outline: 3px solid rgba(31, 111, 74, 0.25) !important;
  outline-offset: 2px !important;
  opacity: 0.0001 !important;
}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================
def _safe_str(x) -> str:
    return "" if pd.isna(x) else str(x).strip()

def _escape(s: str) -> str:
    return html_lib.escape(s or "")

def _badge_status_projeto(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "projeto novo" or "novo" in s:
        return "b-novo"
    if s == "em andamento" or "and" in s:
        return "b-andamento"
    return "b-encerrado"

def _badge_status_insc(status: str) -> str:
    s = (status or "").strip().lower()
    return "b-abertas" if "abert" in s else "b-encerradas"

def _resolve_image_path(img_value: str) -> str:
    v = _safe_str(img_value)
    if not v:
        return ""
    if v.startswith("http://") or v.startswith("https://"):
        return v
    if os.path.isabs(v) and os.path.exists(v):
        return v
    rel = os.path.join(os.getcwd(), v)
    if os.path.exists(rel):
        return rel
    return ""

def _image_to_data_uri(path_or_url: str) -> str:
    if not path_or_url:
        return ""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if not os.path.exists(path_or_url):
        return ""
    ext = os.path.splitext(path_or_url)[1].lower().replace(".", "")
    if ext not in ("png", "jpg", "jpeg", "webp"):
        ext = "png"
    with open(path_or_url, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    return f"data:{mime};base64,{b64}"

@st.cache_data(show_spinner=False)
def carregar_projetos(path: str, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet).fillna("")
    expected = [
        "id","titulo","resumo","descricao","tipo","categoria","palavras_chave",
        "status_projeto","status_inscricoes","periodo","imagem",
        "coordenador","laboratorio","vagas","requisitos","carga_horaria","local",
        "link_edital","contato_email","observacoes"
    ]
    for c in expected:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].astype(str).str.strip()
    df = df[df["titulo"] != ""].copy()
    return df

def aplicar_busca(df: pd.DataFrame, q: str) -> pd.DataFrame:
    q = (q or "").strip().lower()
    if not q:
        return df
    def contains(col):
        return df[col].str.lower().str.contains(q, na=False)
    return df[
        contains("titulo") |
        contains("resumo") |
        contains("descricao") |
        contains("palavras_chave") |
        contains("coordenador") |
        contains("laboratorio")
    ]

def counts_por_categoria(df: pd.DataFrame) -> dict:
    return df["categoria"].replace("", "Sem categoria").value_counts().to_dict()

def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    ativos = (df["status_projeto"].str.strip().str.lower() != "encerrado").sum()
    abertas = (df["status_inscricoes"].str.strip().str.lower() == "abertas").sum()
    encerrados = (df["status_projeto"].str.strip().str.lower() == "encerrado").sum()
    return {"total": int(total), "ativos": int(ativos), "abertas": int(abertas), "encerrados": int(encerrados)}

def close_modal():
    st.session_state["open_id"] = ""

def render_card_html(row: pd.Series) -> str:
    titulo = _escape(_safe_str(row["titulo"]))
    resumo = _escape(_safe_str(row["resumo"]))
    categoria = _escape(_safe_str(row["categoria"]) or "Sem categoria")
    tipo = _escape(_safe_str(row["tipo"]))
    periodo = _escape(_safe_str(row.get("periodo", "")))
    st_proj = _escape(_safe_str(row["status_projeto"]))
    st_ins = _escape(_safe_str(row["status_inscricoes"]))

    img_src = _image_to_data_uri(_resolve_image_path(row["imagem"]))
    badge_proj = _badge_status_projeto(st_proj)
    badge_ins = _badge_status_insc(st_ins)
    periodo_html = f'<span class="badge b-periodo">{periodo}</span>' if periodo else ""

    if img_src:
        img_html = f'<div class="card-img"><img src="{img_src}" alt=""/></div>'
    else:
        img_html = '<div class="card-img" style="display:flex;align-items:center;justify-content:center;color:rgba(0,0,0,0.55);font-weight:900;">Sem imagem</div>'

    return f"""
    <div class="cardwrap">
      <div class="card">
        {img_html}
        <div class="card-title">{titulo}</div>
        <div class="badges">
          <span class="badge b-cat">{categoria}</span>
          <span class="badge b-cat">{tipo}</span>
          {periodo_html}
          <span class="badge {badge_proj}">{st_proj}</span>
          <span class="badge {badge_ins}">{st_ins}</span>
        </div>
        <div class="card-sub">{resumo}</div>
      </div>
    </div>
    """

# =========================
# Dialog (Streamlit 1.53)
# =========================
def abrir_modal_projeto(row: pd.Series):
    titulo = _safe_str(row["titulo"])
    img = _resolve_image_path(row["imagem"])

    @st.dialog(titulo, width="large")
    def _modal():
        if img:
            st.image(img, use_container_width=True)

        categoria = _safe_str(row["categoria"]) or "Sem categoria"
        tipo = _safe_str(row["tipo"])
        periodo = _safe_str(row.get("periodo", ""))
        st_proj = _safe_str(row["status_projeto"])
        st_ins = _safe_str(row["status_inscricoes"])

        badges_html = f"""
        <div class="badges">
          <span class="badge b-cat">{_escape(categoria)}</span>
          <span class="badge b-cat">{_escape(tipo)}</span>
        """
        if periodo:
            badges_html += f'<span class="badge b-periodo">{_escape(periodo)}</span>'
        badges_html += f"""
          <span class="badge {_badge_status_projeto(st_proj)}">{_escape(st_proj)}</span>
          <span class="badge {_badge_status_insc(st_ins)}">{_escape(st_ins)}</span>
        </div>
        """
        st.markdown(badges_html, unsafe_allow_html=True)

        st.subheader("Descrição")
        st.write(_safe_str(row.get("descricao", "")))

        def kv(label, value):
            v = _safe_str(value)
            if v:
                st.markdown(f"**{label}:** {v}")

        st.divider()
        kv("Coordenador", row.get("coordenador", ""))
        kv("Laboratório", row.get("laboratorio", ""))
        kv("Período", row.get("periodo", ""))
        kv("Vagas", row.get("vagas", ""))
        kv("Requisitos", row.get("requisitos", ""))
        kv("Carga horária", row.get("carga_horaria", ""))
        kv("Local", row.get("local", ""))
        kv("Palavras-chave", row.get("palavras_chave", ""))
        kv("Contato (e-mail)", row.get("contato_email", ""))
        kv("Observações", row.get("observacoes", ""))

        link = _safe_str(row.get("link_edital", ""))
        if link:
            st.link_button("📄 Edital / Inscrição", link, use_container_width=True)

        st.divider()
        if st.button("✖ Fechar", use_container_width=True):
            close_modal()
            st.rerun()

    _modal()

# =========================
# APP
# =========================
if not os.path.exists(ARQ_EXCEL):
    st.error(f"Arquivo não encontrado: {ARQ_EXCEL}. Coloque o Excel junto do app.py ou ajuste ARQ_EXCEL.")
    st.stop()

df = carregar_projetos(ARQ_EXCEL, ABA)

# Session defaults
if "categoria_chip" not in st.session_state:
    st.session_state["categoria_chip"] = "Todas"
if "open_id" not in st.session_state:
    st.session_state["open_id"] = ""

if "busca" not in st.session_state:
    st.session_state["busca"] = ""
if "f_tipo" not in st.session_state:
    st.session_state["f_tipo"] = "Todos"
if "f_status_proj" not in st.session_state:
    st.session_state["f_status_proj"] = "Projeto Novo"
if "f_status_insc" not in st.session_state:
    st.session_state["f_status_insc"] = "Abertas"

st.markdown('<div class="ribbon"></div>', unsafe_allow_html=True)

hl, hr = st.columns([4, 1])
with hl:
    st.markdown(
        """
        <div class="header">
          <div>
            <h1>Projetos de Iniciação Científica e Extensão</h1>
            <p>Portal público para conhecer projetos, acompanhar status e ver inscrições abertas. Clique em um card para detalhes.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hr:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.caption("Logo opcional: `assets/uff_proex_logo.png`.")

# FILTROS (mudou = fecha modal)
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([3.2, 1.1, 1.6, 1.8])

    with c1:
        st.text_input(
            "🔍 Buscar",
            placeholder="Ex.: python, saúde, robótica, dados...",
            key="busca",
            on_change=close_modal,
        )

    with c2:
        tipo_opts = ["Todos"] + sorted([t for t in df["tipo"].unique().tolist() if t.strip()])
        if st.session_state["f_tipo"] not in tipo_opts:
            st.session_state["f_tipo"] = "Todos"
        st.selectbox("Tipo", tipo_opts, key="f_tipo", on_change=close_modal)

    with c3:
        stproj_order = ["Todos", "Projeto Novo", "Em andamento", "Encerrado"]
        stproj_unique = [s for s in df["status_projeto"].unique().tolist() if s.strip()]
        stproj_opts = [x for x in stproj_order if x == "Todos" or x in stproj_unique] + sorted(
            [s for s in stproj_unique if s not in stproj_order]
        )
        if st.session_state["f_status_proj"] not in stproj_opts:
            st.session_state["f_status_proj"] = "Todos"
        st.selectbox("Status do projeto", stproj_opts, key="f_status_proj", on_change=close_modal)

    with c4:
        sinsc_order = ["Todos", "Abertas", "Encerradas"]
        sinsc_unique = [s for s in df["status_inscricoes"].unique().tolist() if s.strip()]
        sinsc_opts = [x for x in sinsc_order if x == "Todos" or x in sinsc_unique] + sorted(
            [s for s in sinsc_unique if s not in sinsc_order]
        )
        if st.session_state["f_status_insc"] not in sinsc_opts:
            st.session_state["f_status_insc"] = "Todos"
        st.selectbox("Status das inscrições", sinsc_opts, key="f_status_insc", on_change=close_modal)

# Aplicação dos filtros
df_base = aplicar_busca(df, st.session_state["busca"])
if st.session_state["f_tipo"] != "Todos":
    df_base = df_base[df_base["tipo"] == st.session_state["f_tipo"]]
if st.session_state["f_status_proj"] != "Todos":
    df_base = df_base[df_base["status_projeto"] == st.session_state["f_status_proj"]]
if st.session_state["f_status_insc"] != "Todos":
    df_base = df_base[df_base["status_inscricoes"] == st.session_state["f_status_insc"]]

# KPIs
m = kpis(df_base)
st.markdown(
    f"""
<div class="kpi-wrap">
  <div class="kpi"><div class="label">Projetos (filtro atual)</div><div class="value">{m["total"]}</div><div class="hint">Total exibível no momento</div></div>
  <div class="kpi"><div class="label">Projetos ativos</div><div class="value">{m["ativos"]}</div><div class="hint">Não encerrados</div></div>
  <div class="kpi"><div class="label">Inscrições abertas</div><div class="value">{m["abertas"]}</div><div class="hint">Disponíveis agora</div></div>
  <div class="kpi"><div class="label">Projetos encerrados</div><div class="value">{m["encerrados"]}</div><div class="hint">Finalizados</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# Chips de categoria
cat_counts = counts_por_categoria(df_base)
total = len(df_base)

st.markdown("**Categorias**")
chip_cols = st.columns(9)

def _chip_key(s: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in s)

with chip_cols[0]:
    active = st.session_state["categoria_chip"] == "Todas"
    st.markdown(f'<div class="{"chip-btn-active" if active else "chip-btn"}">', unsafe_allow_html=True)
    if st.button(f"Todas ({total})", key="chip_todas"):
        st.session_state["categoria_chip"] = "Todas"
        close_modal()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

cats_sorted = sorted(cat_counts.items(), key=lambda x: (-x[1], x[0]))
for i, (cat, cnt) in enumerate(cats_sorted, start=1):
    with chip_cols[i % len(chip_cols)]:
        active = st.session_state["categoria_chip"] == cat
        st.markdown(f'<div class="{"chip-btn-active" if active else "chip-btn"}">', unsafe_allow_html=True)
        if st.button(f"{cat} ({cnt})", key=f"chip_{_chip_key(cat)}"):
            st.session_state["categoria_chip"] = cat
            close_modal()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Filtro por categoria (chip)
df_f = df_base.copy()
sel_cat = st.session_state["categoria_chip"]
if sel_cat != "Todas":
    if sel_cat == "Sem categoria":
        df_f = df_f[df_f["categoria"].replace("", "Sem categoria") == "Sem categoria"]
    else:
        df_f = df_f[df_f["categoria"] == sel_cat]

st.divider()
st.write(f"**{len(df_f)}** projeto(s) encontrado(s).")

if len(df_f) == 0:
    st.info("Nenhum projeto encontrado com os filtros atuais.")
    st.stop()

# Modal aberto por open_id
open_id = st.session_state.get("open_id", "")
if open_id:
    hit = df_f[df_f["id"] == open_id]
    if len(hit) == 1:
        abrir_modal_projeto(hit.iloc[0])
    else:
        close_modal()

# Grid de cards + overlay button que abre modal
cols = st.columns(GRID_COLS, gap="large")
for idx, (_, row) in enumerate(df_f.iterrows()):
    with cols[idx % GRID_COLS]:
        proj_id = _safe_str(row["id"]) or f"row_{idx}"

        # Card HTML
        st.markdown(render_card_html(row), unsafe_allow_html=True)

        # Botão invisível (overlay) para abrir modal sem navegação/aba
        # A chave precisa ser única por card
        #st.markdown('<div class="cardwrap"><div class="open-overlay">', unsafe_allow_html=True)
        #clicked = st.button("Abrir", key=f"open_{proj_id}")
        #st.markdown("</div></div>", unsafe_allow_html=True)

        # Botão "Abrir" centralizado abaixo do card
        b1, b2, b3 = st.columns([1, 1, 1])
        with b2:
            clicked = st.button("Abrir", key=f"open_{proj_id}", use_container_width=True)

        if clicked:
            st.session_state["open_id"] = proj_id
            st.rerun()