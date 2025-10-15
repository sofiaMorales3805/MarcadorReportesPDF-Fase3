# app.py
import os
import io
import requests
from datetime import datetime

from fastapi import FastAPI, Query, Header, Response, HTTPException
from fastapi.responses import PlainTextResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from fastapi import Query, Response

# -----------------------------------------------------------------------------
# Config básica
# -----------------------------------------------------------------------------
app = FastAPI(title="Marcador Reportes", version="1.0.0")

BACK_BASE = os.getenv("BACK_BASE", "http://localhost:5130")
EQUIPOS_PATH = os.getenv("EQUIPOS_PATH", "/api/equipos")
PLAYERS_BY_TEAM = os.getenv("PLAYERS_BY_TEAM", "/api/jugadores")
# En tu C#: la ruta que expusiste finalmente es /api/partidos/historial
MATCH_HISTORY = os.getenv("MATCH_HISTORY", "/api/partidos/historial")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _hdr(authorization: str | None):
    return {"Authorization": authorization} if authorization else {}

def _ensure_ok(r: requests.Response, url: str):
    if not r.ok:
        # Propaga el status real del backend
        detail = r.text[:300] if r.text else ""
        raise HTTPException(status_code=r.status_code, detail=f"{url} → {r.status_code}: {detail}")

def _pdf_bytes(
    title: str,
    headers: list[list | str],
    rows: list[list[str]],
    subtitle: str | None = None,
) -> bytes:
    """
    Crea un PDF simple con título y una tabla.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=36, rightMargin=36, topMargin=42, bottomMargin=42
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=24,
        spaceAfter=6
    )
    sub = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#666"),
        spaceAfter=16,
    )

    story: list = []
    story.append(Paragraph(title, h1))
    story.append(Paragraph("Generado por MarcadorReportesPDF-Fase3", sub))
    if subtitle:
        story.append(Paragraph(subtitle, sub))

    data = [headers] + rows
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.HexColor("#222")),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fbfbfb")]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    story.append(table)
    doc.build(story)
    buf.seek(0)
    return buf.read()

# -----------------------------------------------------------------------------
# Health / root
# -----------------------------------------------------------------------------
@app.get("/", response_class=PlainTextResponse)
def root():
    return "Marcador Reportes API – OK"

@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"

# -----------------------------------------------------------------------------
# /pdf/equipos
# -----------------------------------------------------------------------------
@app.get("/pdf/equipos")
def pdf_equipos(
    search: str | None = Query(default=None),
    ciudad: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    url = f"{BACK_BASE}{EQUIPOS_PATH}"
    params = {}
    if search: params["search"] = search
    if ciudad: params["ciudad"] = ciudad

    r = requests.get(url, params=params, headers=_hdr(authorization), timeout=30)
    _ensure_ok(r, url)
    equipos = r.json() or []

    # Create PDF with logos
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=42, bottomMargin=42)
    
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, leading=24, spaceAfter=6)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#666"), spaceAfter=16)
    
    story = []
    story.append(Paragraph("Reporte de Equipos Registrados", h1))
    story.append(Paragraph("Generado por MarcadorReportesPDF-Fase3", sub))
    
    # Table with logos
    headers_tbl = ["Logo", "Id", "Equipo", "Ciudad", "Puntos", "Faltas"]
    data = [headers_tbl]
    
    for e in equipos:
        # Try to get logo from LogoUrl field
        logo_cell = ""
        logo_url = e.get("LogoUrl") or e.get("logoUrl")
        
        # Also try using team name as fallback for assets
        team_name = str(e.get("nombre") or e.get("Nombre") or "").lower().replace(" ", "_")
        
        if logo_url:
            try:
                logo_response = requests.get(logo_url, timeout=5)
                if logo_response.status_code == 200:
                    logo_img = Image(ImageReader(io.BytesIO(logo_response.content)), width=30, height=30)
                    logo_cell = logo_img
                else:
                    logo_cell = "Sin logo"
            except:
                logo_cell = "Sin logo"
        else:
            # Try assets folder with team name
            try:
                assets_path = f"assets/{team_name}.png"
                if os.path.exists(assets_path):
                    logo_img = Image(assets_path, width=30, height=30)
                    logo_cell = logo_img
                else:
                    logo_cell = "Sin logo"
            except:
                logo_cell = "Sin logo"
            
        data.append([
            logo_cell,
            str(e.get("id") or e.get("Id") or ""),
            str(e.get("nombre") or e.get("Nombre") or ""),
            str(e.get("ciudad") or e.get("Ciudad") or "–"),
            str(e.get("puntos") or e.get("Puntos") or 0),
            str(e.get("faltas") or e.get("Faltas") or 0),
        ])
    
    table = Table(data, colWidths=[50, 30, 120, 80, 50, 50], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#222")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfbfb")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    
    story.append(table)
    doc.build(story)
    buf.seek(0)
    
    return Response(
        content=buf.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Equipos_Registrados.pdf"'}
    )

# -----------------------------------------------------------------------------
# /pdf/jugadores-por-equipo
# -----------------------------------------------------------------------------
@app.get("/pdf/jugadores-por-equipo")
def pdf_jugadores_por_equipo(
    equipoId: int = Query(..., description="Id del equipo"),
    authorization: str | None = Header(default=None),
):
    url = f"{BACK_BASE}{PLAYERS_BY_TEAM}"
    params = {"equipoId": equipoId}

    r = requests.get(url, params=params, headers=_hdr(authorization), timeout=30)
    _ensure_ok(r, url)
    jugadores = r.json() or []

    headers_tbl = ["#", "Jugador", "Posición", "Número", "Edad", "Estatura (cm)", "Nacionalidad"]
    rows: list[list[str]] = []
    for i, j in enumerate(jugadores, start=1):
        rows.append([
            str(i),
            str(j.get("Nombre") or j.get("nombre") or ""),
            str(j.get("Posicion") or j.get("posicion") or "–"),
            str(j.get("Numero") or j.get("numero") or "–"),
            str(j.get("Edad") or j.get("edad") or "–"),
            str(j.get("Estatura") or j.get("estatura") or "–"),
            str(j.get("Nacionalidad") or j.get("nacionalidad") or "–"),
        ])

    subtitle = f"Equipo Id: {equipoId}"
    pdf = _pdf_bytes("Reporte de Jugadores por Equipo", headers_tbl, rows, subtitle)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="JugadoresXEquipo_{equipoId}.pdf"'}
    )

# -----------------------------------------------------------------------------
# /pdf/historial-partidos
# -----------------------------------------------------------------------------
@app.get("/pdf/historial-partidos")
def pdf_historial_partidos(
    temporadaId: int | None = Query(None),
    authorization: str | None = Header(default=None),
):
    # Soporta variable de entorno; si alguien dejó "historico", también funciona.
    path = MATCH_HISTORY or "/api/partidos/historial"
    if path.endswith("historico"):
        path = "/api/partidos/historial"
    url = f"{BACK_BASE}{path}"

    params = {}
    if temporadaId is not None:
        params["temporadaId"] = temporadaId

    r = requests.get(url, params=params, headers=_hdr(authorization), timeout=30)
    _ensure_ok(r, url)
    response = r.json() or {}
    # El endpoint devuelve una estructura paginada con 'items'
    partidos = response.get('items', []) if isinstance(response, dict) else response or []

    headers_tbl = ["#", "Fecha/Hora", "Local", "Visitante", "Marcador"]
    rows: list[list[str]] = []
    for i, p in enumerate(partidos, start=1):
        # Ensure p is a dictionary
        if not isinstance(p, dict):
            continue
        # intenta nombres si el back los trae; si no, el Id
        local = p.get("EquipoLocalNombre") or p.get("equipoLocalNombre") or p.get("EquipoLocalId") or "?"
        vis   = p.get("EquipoVisitanteNombre") or p.get("equipoVisitanteNombre") or p.get("EquipoVisitanteId") or "?"
        
        # Si viene "Local" o "Visitante" como texto, usar los IDs en su lugar
        if local in ["Local", "local"]:
            local = f"Equipo {p.get('EquipoLocalId') or p.get('equipoLocalId') or '?'}"
        if vis in ["Visitante", "visitante"]:
            vis = f"Equipo {p.get('EquipoVisitanteId') or p.get('equipoVisitanteId') or '?'}"
        ml = p.get("MarcadorLocal") or p.get("PuntosLocal") or p.get("marcadorLocal") or 0
        mv = p.get("MarcadorVisitante") or p.get("PuntosVisitante") or p.get("marcadorVisitante") or 0
        fh = p.get("FechaHora") or p.get("fechaHora") or ""
        try:
            # formateo agradable si viene ISO
            fh_fmt = datetime.fromisoformat(str(fh).replace("Z","")).strftime("%Y-%m-%d %H:%M")
        except Exception:
            fh_fmt = str(fh)

        rows.append([
            str(i),
            fh_fmt,
            str(local),
            str(vis),
            f"{ml} - {mv}",
        ])

    subtitle = f"Temporada: {temporadaId if temporadaId is not None else 'todas'}"
    pdf = _pdf_bytes("Historial de partidos", headers_tbl, rows, subtitle)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Historial_Partidos.pdf"'}
    )

# -----------------------------------------------------------------------------
# /pdf/roster
# -----------------------------------------------------------------------------
@app.get("/pdf/roster")
def pdf_roster(
    partidoId: int = Query(...),
    authorization: str | None = Header(default=None),
):
    # En tu C# dejamos GET: /api/partidos/{id}/roster
    url = f"{BACK_BASE}/api/partidos/{partidoId}/roster"

    r = requests.get(url, headers=_hdr(authorization), timeout=30)
    _ensure_ok(r, url)
    roster = r.json() or []

    headers_tbl = ["#", "EquipoId", "Jugador", "Posición"]
    rows: list[list[str]] = []
    for i, item in enumerate(roster, start=1):
        rows.append([
            str(i),
            str(item.get("EquipoId") or item.get("equipoId") or ""),
            str(item.get("JugadorNombre") or item.get("jugadorNombre") or ""),
            str(item.get("Posicion") or item.get("posicion") or "–"),
        ])

    pdf = _pdf_bytes(f"Roster – Partido {partidoId}", headers_tbl, rows)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Roster_Partido_{partidoId}.pdf"'}
    )

# -----------------------------------------------------------------------------
# /pdf/scouting (opcional; si aún no tienes estadísticas, imprime ceros)
# -----------------------------------------------------------------------------
@app.get("/pdf/scouting")
def pdf_scouting(
    jugadorId: int = Query(...),
    authorization: str | None = Header(default=None),
):
    # 1) Trae datos básicos del jugador
    jurl = f"{BACK_BASE}/api/jugadores/{jugadorId}"
    rj = requests.get(jurl, headers=_hdr(authorization), timeout=30)
    _ensure_ok(rj, jurl)
    j = rj.json() or {}

    nombre = str(j.get("Nombre") or j.get("nombre") or "")
    posicion = str(j.get("Posicion") or j.get("posicion") or "–")
    edad = str(j.get("Edad") or j.get("edad") or "–")
    estatura = str(j.get("Estatura") or j.get("estatura") or "–")
    equipo = str(j.get("EquipoNombre") or j.get("equipoNombre") or j.get("EquipoId") or j.get("equipoId") or "")

    # 2) (Opcional) intenta traer promedios si ya tienes un endpoint de stats
    #    Si no existe, usamos ceros/guiones y listo (no rompe).
    ppg = rpg = apg = spg = bpg = 0
    fg = tp = ft = 0.0
    tov = pf = 0
    minutes = 0

    # Construimos una "tabla de métricas"
    headers_tbl = ["PPG", "RPG", "APG", "SPG", "BPG", "FG%", "3P%", "FT%", "MIN", "TOV", "PF"]
    rows = [[
        str(ppg), str(rpg), str(apg), str(spg), str(bpg),
        f"{fg:.1f}", f"{tp:.1f}", f"{ft:.1f}",
        str(minutes), str(tov), str(pf)
    ]]

    subtitle = f"{nombre} • {posicion} • {equipo}  |  Edad: {edad}  |  Estatura: {estatura} cm"
    pdf = _pdf_bytes("Scouting – Jugador", headers_tbl, rows, subtitle)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="scouting_jugador_{jugadorId}.pdf"'}
    )
 
 # /pdf/lideres?metric=puntos|faltas&equipoId=?
@app.get("/pdf/lideres")
def pdf_lideres(
    metric: str = Query(default="puntos", regex="^(puntos|faltas)$"),
    equipoId: int | None = Query(default=None),
    authorization: str | None = Header(default=None)
):
    # 1) intenta API de líderes
    base = os.getenv("BACK_BASE", "http://localhost:5130")
    url_l = f"{base}/api/estadisticas/lideres"
    params = {"metric": metric}
    if equipoId: params["equipoId"] = equipoId

    try:
        r = requests.get(url_l, params=params, headers=_hdr(authorization), timeout=20)
        if r.status_code == 200:
            data = r.json()
        else:
            raise Exception("no leaders endpoint")
    except Exception:
        # 2) Fallback a /api/jugadores
        params_j = {}
        if equipoId: params_j["equipoId"] = equipoId
        r2 = requests.get(f"{base}/api/jugadores", params=params_j, headers=_hdr(authorization), timeout=20)
        _ensure_ok(r2, "/api/jugadores")
        players = r2.json()
        field = "puntos" if metric == "puntos" else "faltas"
        # normaliza nombres / valores
        norm = []
        for j in players:
            norm.append({
                "nombre": j.get("nombre") or j.get("Nombre"),
                "equipoNombre": j.get("equipoNombre") or j.get("EquipoNombre") or "",
                "posicion": j.get("posicion") or j.get("Posicion") or "—",
                "valor": j.get(field) or j.get(field.capitalize()) or 0,
            })
        data = sorted(norm, key=lambda x: x["valor"], reverse=True)

    # top-3 + resto
    top3 = data[:3]
    resto = data[3:13]

    # ===== PDF =====
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=42, bottomMargin=36)
    st = getSampleStyleSheet()
    H1 = st['Title']; H1.fontSize = 24
    P  = st['Normal']; P.leading = 14

    story = []
    title = f"Líderes – { 'Puntos' if metric=='puntos' else 'Faltas personales' }"
    if equipoId: title += f" (Equipo {equipoId})"
    story += [Paragraph(title, H1), Spacer(1, 8), Paragraph("Generado por MarcadorReportesPDF", st['Italic']), Spacer(1, 14)]

    # TOP 3 (sencillo, en tabla)
    if top3:
        tdata = [["#", "Jugador", "Equipo", "Posición", "Valor"]]
        for i, p in enumerate(top3, start=1):
            tdata.append([i, p.get("nombre",""), p.get("equipoNombre",""), p.get("posicion","—"), p.get("valor",0)])
        t = Table(tdata, colWidths=[24, 200, 150, 80, 60])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (3,-1), 'LEFT'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOX', (0,0), (-1,-1), 0.75, colors.grey),
            ('FONTSIZE', (0,0), (-1,0), 12),
        ]))
        story += [Paragraph("<b>Top 3</b>", st['Heading2']), Spacer(1,6), t, Spacer(1,14)]

    # RANKING
    if resto:
        rdata = [["#", "Jugador", "Equipo", "Posición", "Valor"]]
        for i, p in enumerate(resto, start=4):
            rdata.append([i, p.get("nombre",""), p.get("equipoNombre",""), p.get("posicion","—"), p.get("valor",0)])
        rt = Table(rdata, colWidths=[24, 200, 150, 80, 60])
        rt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (3,-1), 'LEFT'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('BOX', (0,0), (-1,-1), 0.75, colors.lightgrey),
        ]))
        story += [Paragraph("<b>Ranking</b>", st['Heading2']), Spacer(1,6), rt]

    doc.build(story)
    buf.seek(0)
    return Response(buf.getvalue(), media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="lideres.pdf"'})

# -----------------------------------------------------------------------------
# Main (opcional si ejecutas con: py -m uvicorn app:app --reload --port 5055)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "5055")), reload=True)
