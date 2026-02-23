# app.py
# Portal público de Projetos de Iniciação Científica e Extensão (UFF/PROEX)
# Compatível com Streamlit 1.53+
#
# Requisitos:
#   pip install -U streamlit pandas openpyxl
#   (opcional p/ thumbnails) pip install pillow
#
# Estrutura:
#   app.py
#   /data/modelo_projetos_ic_extensao.xlsx
#   /imgs/p_0001.png, p_0002.png, p_0003.jpg, ...
#   /imgs/_default.png  (fallback recomendado)
#   /assets/uff_proex_logo.png (opcional)

import os
import base64
import html as html_lib
from typing import Optional, Tuple

import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Projetos IC & Extensão — UFF/PROEX", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARQ_EXCEL = os.environ.get(
    "ARQ_EXCEL",
    os.path.join(BASE_DIR, "data", "modelo_projetos_ic_extensao.xlsx"),
)
ABA = os.environ.get("ABA_EXCEL", "projetos")

LOGO_PATH = os.path.join(BASE_DIR, "assets", "uff_proex_logo.png")  # opcional

IMG_DIR = os.path.join(BASE_DIR, "imgs")
THUMB_DIR = os.path.join(IMG_DIR, "_thumbs")
DEFAULT_IMG = os.path.join(IMG_DIR, "_default.png")  # fallback (recomendado)

BRAND_GREEN = "#1F6F4A"
BRAND_GREEN_DARK = "#15553A"
BG = "#F6F7F8"

CARD_IMG_HEIGHT = 165
GRID_COLS = 3

# Proporção padrão para thumbnails: 16:9 (boa p/ cards)
THUMB_SIZE = (1200, 675)  # (w, h)

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

div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: white !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
  border-radius: 18px !important;
  padding: 14px !important;
  box-shadow: 0 8px 18px rgba(0,0,0,0.05) !important;
  margin-bottom: 12px !important;
}}

/* Pills: aumentar tamanho e legibilidade */
div[data-testid="stPills"] button {{
  padding: 10px 16px !important;
  font-size: 0.95rem !important;
  font-weight: 950 !important;
  border-radius: 999px !important;
  white-space: normal !important;
  line-height: 1.15 !important;
}}

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
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding: 6px 14px;
  border-radius:999px;
  font-size:13px;
  font-weight:950;
  border:1px solid rgba(0,0,0,0.08);
  max-width: 100%;
  white-space: normal;
  line-height: 1.15;
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
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Query Params (Deep Link) — APENAS LEITURA
# =========================
def _qp_get_one(key: str) -> str:
    v = st.query_params.get(key, "")
    if isinstance(v, list):
        return v[0] if v else ""
    return str(v or "")

# =========================
# Helpers
# =========================
def _safe_str(x) -> str:
    return "" if pd.isna(x) else str(x).strip()

def _escape(s: str) -> str:
    return html_lib.escape(s or "")

def _normalize_id(x: str) -> str:
    s = _safe_str(x).strip()
    # Excel numérico virando float: "p_0002.0"
    if s.endswith(".0"):
        s = s[:-2]
    return s.strip().lower()

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

def _ensure_dirs():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

def _resolve_local_image_from_value(value: str) -> str:
    v = _safe_str(value)
    if not v:
        return ""
    if v.startswith("imgs/") or v.startswith("imgs\\"):
        p = os.path.join(BASE_DIR, v.replace("/", os.sep).replace("\\", os.sep))
        return p if os.path.exists(p) else ""
    p = os.path.join(IMG_DIR, v)
    return p if os.path.exists(p) else ""

def _auto_map_image_by_id(proj_id: str) -> str:
    pid = _safe_str(proj_id)
    if not pid:
        return ""
    exts = [".png", ".jpg", ".jpeg", ".webp"]
    for ext in exts:
        p = os.path.join(IMG_DIR, f"{pid}{ext}")
        if os.path.exists(p):
            return p
    return ""

def _pick_image_path(row: pd.Series) -> str:
    p = _resolve_local_image_from_value(row.get("imagem", ""))
    if p:
        return p
    p = _auto_map_image_by_id(row.get("id", ""))
    if p:
        return p
    if os.path.exists(DEFAULT_IMG):
        return DEFAULT_IMG
    return ""

def _image_to_data_uri(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    if ext not in ("png", "jpg", "jpeg", "webp"):
        ext = "png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    return f"data:{mime};base64,{b64}"

def _thumb_path_for(src_path: str, size: Tuple[int, int]) -> str:
    if not src_path:
        return ""
    try:
        mtime = int(os.path.getmtime(src_path))
    except OSError:
        mtime = 0
    base = os.path.basename(src_path)
    name, _ext = os.path.splitext(base)
    w, h = size
    return os.path.join(THUMB_DIR, f"{name}__{mtime}__{w}x{h}.jpg")

@st.cache_data(show_spinner=False)
def _make_thumbnail(src_path: str, size: Tuple[int, int]) -> str:
    if not src_path or not os.path.exists(src_path):
        return ""
    dst = _thumb_path_for(src_path, size)
    if dst and os.path.exists(dst):
        return dst
    try:
        from PIL import Image, ImageOps  # type: ignore
    except Exception:
        return src_path
    try:
        im = Image.open(src_path).convert("RGB")
        thumb = ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        os.makedirs(THUMB_DIR, exist_ok=True)
        thumb.save(dst, format="JPEG", quality=88, optimize=True)
        return dst
    except Exception:
        return src_path

def render_card_html(row: pd.Series) -> str:
    titulo = _escape(_safe_str(row["titulo_curto"]))
    resumo = _escape(_safe_str(row["resumo_curto"]))

    categoria = _escape(_safe_str(row["categoria"]) or "Sem categoria")
    tipo = _escape(_safe_str(row["tipo"]))
    periodo = _escape(_safe_str(row.get("periodo", "")))
    st_proj = _escape(_safe_str(row["status_projeto"]))
    st_ins = _escape(_safe_str(row["status_inscricoes"]))

    img_path = _pick_image_path(row)
    if img_path:
        img_path = _make_thumbnail(img_path, THUMB_SIZE)

    img_src = _image_to_data_uri(img_path)
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
# Data
# =========================
@st.cache_data(show_spinner=False)  # sem ttl: evita “recarregar no meio”
def carregar_projetos(path: str, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet).fillna("")

    expected = [
        "id",
        "titulo_curto", "resumo_curto",
        "titulo_expandido", "resumo_expandido", "perfil",
        "titulo", "resumo", "descricao",
        "tipo", "categoria", "palavras_chave",
        "status_projeto", "status_inscricoes", "periodo", "imagem",
        "coordenador", "laboratorio", "vagas", "requisitos", "carga_horaria", "local",
        "link_edital", "contato_email", "observacoes",
    ]
    for c in expected:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].astype(str).str.strip()

    df["titulo_curto"] = df["titulo_curto"].where(df["titulo_curto"] != "", df["titulo"])
    df["resumo_curto"] = df["resumo_curto"].where(df["resumo_curto"] != "", df["resumo"])
    df["titulo_expandido"] = df["titulo_expandido"].where(df["titulo_expandido"] != "", df["titulo"])
    df["resumo_expandido"] = df["resumo_expandido"].where(
        df["resumo_expandido"] != "",
        df["descricao"].where(df["descricao"] != "", df["resumo"])
    )

    df = df[df["titulo_curto"] != ""].copy()

    df["id"] = df["id"].where(df["id"] != "", None)
    df["id"] = df["id"].fillna(pd.Series([f"p_{i+1:04d}" for i in range(len(df))], index=df.index))

    df["_id_norm"] = df["id"].map(_normalize_id)
    return df

def aplicar_busca(df: pd.DataFrame, q: str) -> pd.DataFrame:
    q = (q or "").strip().lower()
    if not q:
        return df

    def contains(col):
        return df[col].str.lower().str.contains(q, na=False)

    return df[
        contains("titulo_curto") |
        contains("titulo_expandido") |
        contains("resumo_curto") |
        contains("resumo_expandido") |
        contains("perfil") |
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

# =========================
# Modal
# =========================
def close_modal():
    # NÃO mexe em query params para evitar rerun/fechar dialog no 1.53
    st.session_state["open_id"] = ""

def _find_row_by_id(df_all: pd.DataFrame, any_id: str) -> Optional[pd.Series]:
    target = _normalize_id(any_id)
    if not target:
        return None

    hit = df_all[df_all["_id_norm"] == target]
    if len(hit) == 1:
        return hit.iloc[0]

    hit2 = df_all[df_all["_id_norm"].str.contains(target, na=False)]
    if len(hit2) == 1:
        return hit2.iloc[0]

    return None

def abrir_modal_projeto(row: pd.Series):
    titulo_modal = _safe_str(row.get("titulo_expandido", "")) or _safe_str(row.get("titulo_curto", "")) or "Detalhes"
    img_path = _pick_image_path(row)
    proj_id = _safe_str(row.get("id", ""))

    @st.dialog(titulo_modal, width="large")
    def _modal():
        # ✅ bytes (evita /media 404 em casos de reexecução)
        if img_path and os.path.exists(img_path):
            try:
                with open(img_path, "rb") as f:
                    st.image(f.read(), use_container_width=True)
            except Exception:
                pass

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

        if proj_id:
            st.caption(f"Link direto: ?id={html_lib.escape(proj_id)}")

        tit_exp = _safe_str(row.get("titulo_expandido", ""))
        if tit_exp:
            st.markdown(f"### {html_lib.escape(tit_exp)}", unsafe_allow_html=True)

        resumo_exp = _safe_str(row.get("resumo_expandido", ""))
        if resumo_exp:
            st.subheader("Resumo")
            st.markdown(resumo_exp, unsafe_allow_html=True)

        perfil = _safe_str(row.get("perfil", ""))
        if perfil:
            st.subheader("Perfil")
            st.markdown(perfil, unsafe_allow_html=True)

        def kv(label, value):
            v = _safe_str(value)
            if v:
                st.markdown(f"**{label}:** {v}")

        st.divider()
        kv("Coordenadores", row.get("coordenador", ""))
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
_ensure_dirs()

if not os.path.exists(ARQ_EXCEL):
    st.error(
        "Arquivo não encontrado.\n\n"
        f"**ARQ_EXCEL:** `{ARQ_EXCEL}`\n\n"
        "Verifique se existe:\n"
        f"- `{os.path.join(BASE_DIR, 'data', os.path.basename(ARQ_EXCEL))}`\n"
        "Ou defina a variável de ambiente `ARQ_EXCEL` com o caminho correto."
    )
    st.stop()

df = carregar_projetos(ARQ_EXCEL, ABA)

# Session defaults (ANTES de criar widgets)
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

# Deep link (somente leitura)
url_id = _qp_get_one("id").strip()
if url_id and st.session_state["open_id"] != url_id:
    st.session_state["open_id"] = url_id

# ===== UI =====
st.markdown('<div class="ribbon"></div>', unsafe_allow_html=True)

hl, hr = st.columns([4, 1])
with hl:
    st.markdown(
        """
        <div class="header">
          <div>
            <h1>Projetos de Iniciação Científica e Extensão</h1>
            <p>Portal para conhecer projetos de iniciação científica e extensão, acompanhar status e ver inscrições abertas. Clique em um card para detalhes.</p>
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

# FILTROS
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

# Aplica filtros
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

# Categorias com pills
cat_counts = counts_por_categoria(df_base)
total = len(df_base)
cats_sorted = sorted(cat_counts.items(), key=lambda x: (-x[1], x[0]))
cat_options = [f"Todas ({total})"] + [f"{cat} ({cnt})" for cat, cnt in cats_sorted]

st.markdown("**Categorias**")
sel = st.pills(
    label="Categorias",
    options=cat_options,
    default=st.session_state.get("categoria_chip_ui", f"Todas ({total})"),
    label_visibility="collapsed",
)
if sel is None:
    sel = f"Todas ({total})"

if st.session_state.get("categoria_chip_ui", "") != sel:
    st.session_state["categoria_chip_ui"] = sel
    close_modal()
    st.rerun()

if sel.startswith("Todas"):
    sel_cat = "Todas"
else:
    sel_cat = sel.rsplit(" (", 1)[0].strip()

df_f = df_base.copy()
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

# Grid de cards
cols = st.columns(GRID_COLS, gap="large")
for idx, (_, row) in enumerate(df_f.iterrows()):
    with cols[idx % GRID_COLS]:
        proj_id = _safe_str(row["id"]) or f"row_{idx}"
        st.markdown(render_card_html(row), unsafe_allow_html=True)

        b1, b2, b3 = st.columns([1, 1, 1])
        with b2:
            clicked = st.button("Abrir", key=f"open_{proj_id}", use_container_width=True)

        if clicked:
            # NADA de query_params aqui (evita “rerun extra” que fecha dialog)
            st.session_state["open_id"] = proj_id
            st.rerun()

# =========================
# ✅ ABRIR MODAL POR ÚLTIMO (fim do script)
# =========================
open_id = st.session_state.get("open_id", "")
if open_id:
    hit_row = _find_row_by_id(df, open_id)
    if hit_row is not None:
        abrir_modal_projeto(hit_row)
    else:
        # se id não existe, só não abre
        st.session_state["open_id"] = ""
        st.warning(f"Projeto id='{open_id}' não encontrado.")