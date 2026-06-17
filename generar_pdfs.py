#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera PDFs de AsistenciaRed: propuesta comercial + manuales por rol"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, PageBreak)
from reportlab.pdfgen import canvas as pdfcanvas
import os

OUT = "/sessions/eager-stoic-heisenberg/mnt/CFI2/"

# ── Paleta ──────────────────────────────────────────
AZUL      = colors.HexColor("#1a365d")
AZUL_MED  = colors.HexColor("#2a4a7f")
DORADO    = colors.HexColor("#f6ad55")
VERDE     = colors.HexColor("#276749")
ROJO      = colors.HexColor("#9b2c2c")
GRIS      = colors.HexColor("#718096")
GRIS_CLR  = colors.HexColor("#f7fafc")
BLANCO    = colors.white

# ── Estilos base ────────────────────────────────────
def estilos():
    s = getSampleStyleSheet()
    base = dict(fontName="Helvetica", leading=14, textColor=colors.HexColor("#2d3748"))

    s.add(ParagraphStyle("Titulo",      fontName="Helvetica-Bold", fontSize=26,
                         textColor=BLANCO, alignment=TA_CENTER, leading=32, spaceAfter=6))
    s.add(ParagraphStyle("Subtitulo",   fontName="Helvetica",      fontSize=13,
                         textColor=DORADO, alignment=TA_CENTER, leading=18, spaceAfter=4))
    s.add(ParagraphStyle("H1",          fontName="Helvetica-Bold", fontSize=16,
                         textColor=AZUL, leading=20, spaceBefore=18, spaceAfter=8))
    s.add(ParagraphStyle("H2",          fontName="Helvetica-Bold", fontSize=13,
                         textColor=AZUL_MED, leading=17, spaceBefore=12, spaceAfter=6))
    s.add(ParagraphStyle("H3",          fontName="Helvetica-Bold", fontSize=11,
                         textColor=AZUL, leading=15, spaceBefore=8, spaceAfter=4))
    s.add(ParagraphStyle("Cuerpo",      fontSize=10.5, leading=16, spaceAfter=6,
                         alignment=TA_JUSTIFY, **{k:v for k,v in base.items() if k!="textColor"},
                         textColor=colors.HexColor("#2d3748")))
    s.add(ParagraphStyle("Item",        fontSize=10, leading=15, spaceAfter=3,
                         leftIndent=16, firstLineIndent=-10,
                         fontName="Helvetica", textColor=colors.HexColor("#2d3748")))
    s.add(ParagraphStyle("CentroGris",  fontSize=9, leading=13, alignment=TA_CENTER,
                         textColor=GRIS, fontName="Helvetica"))
    s.add(ParagraphStyle("Destacado",   fontName="Helvetica-Bold", fontSize=11,
                         textColor=AZUL, leading=15, spaceAfter=4))
    s.add(ParagraphStyle("Paso",        fontName="Helvetica-Bold", fontSize=10.5,
                         textColor=VERDE, leading=15, spaceBefore=6, spaceAfter=2))
    s.add(ParagraphStyle("PasoDesc",    fontSize=10, leading=14, spaceAfter=4,
                         leftIndent=14, fontName="Helvetica",
                         textColor=colors.HexColor("#2d3748")))
    return s

S = estilos()

# ── Header/Footer ────────────────────────────────────
def header_footer(canv, doc, titulo_doc, rol_color=AZUL):
    canv.saveState()
    w, h = A4
    # Header
    canv.setFillColor(rol_color)
    canv.rect(0, h-1.8*cm, w, 1.8*cm, fill=1, stroke=0)
    canv.setFillColor(BLANCO)
    canv.setFont("Helvetica-Bold", 10)
    canv.drawString(1.5*cm, h-1.1*cm, "AsistenciaRed — Sistema Institucional")
    canv.setFont("Helvetica", 9)
    canv.drawRightString(w-1.5*cm, h-1.1*cm, titulo_doc)
    # Footer
    canv.setFillColor(GRIS)
    canv.setFont("Helvetica", 8)
    canv.drawString(1.5*cm, 0.7*cm, "AsistenciaRed | Sistema de Gestion de Asistencia Institucional")
    canv.drawRightString(w-1.5*cm, 0.7*cm, f"Pagina {doc.page}")
    canv.restoreState()

def portada_block(story, titulo, subtitulo, color=AZUL):
    """Bloque de portada con fondo de color"""
    story.append(Spacer(1, 1.5*cm))
    data = [[Paragraph(titulo, S["Titulo"])],
            [Spacer(1, 0.3*cm)],
            [Paragraph(subtitulo, S["Subtitulo"])]]
    t = Table(data, colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("ROUNDEDCORNERS", [12]),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.8*cm))

def caja_destacada(texto, color_borde=DORADO, color_fondo=colors.HexColor("#fffaf0")):
    data = [[Paragraph(texto, S["Cuerpo"])]]
    t = Table(data, colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), color_fondo),
        ("LINEAFTER",     (0,0), (0,-1), 4, color_borde),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
    ]))
    return t

def tabla_pasos(pasos):
    """Lista numerada con estilo de pasos"""
    rows = []
    for i, (titulo, desc) in enumerate(pasos, 1):
        rows.append([
            Paragraph(str(i), ParagraphStyle("Num", fontName="Helvetica-Bold",
                      fontSize=14, textColor=BLANCO, alignment=TA_CENTER)),
            Paragraph(f"<b>{titulo}</b><br/>{desc}", S["Cuerpo"])
        ])
    t = Table(rows, colWidths=[1*cm, 15*cm], rowHeights=None)
    style = [
        ("BACKGROUND",    (0,0), (0,-1), AZUL),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,1), (-1,-1), 12),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [GRIS_CLR, BLANCO]),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]
    t.setStyle(TableStyle(style))
    return t

def chips(items, colores):
    """Fila de chips/tarjetas de resumen"""
    row = []
    for texto, col in zip(items, colores):
        p = Paragraph(texto, ParagraphStyle("Chip", fontName="Helvetica-Bold",
                      fontSize=9.5, textColor=BLANCO, alignment=TA_CENTER, leading=14))
        row.append(p)
    ancho = 16*cm / len(items)
    t = Table([row], colWidths=[ancho]*len(items))
    style_list = [("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                  ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]
    for i, col in enumerate(colores):
        style_list.append(("BACKGROUND",(i,0),(i,0), col))
    t.setStyle(TableStyle(style_list))
    return t

# ════════════════════════════════════════════════════
#  1. PROPUESTA COMERCIAL
# ════════════════════════════════════════════════════
def pdf_propuesta():
    path = os.path.join(OUT, "AsistenciaRed_Propuesta_Comercial.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)

    def hf(canv, d): header_footer(canv, d, "Propuesta Comercial")

    story = []

    # Portada
    portada_block(story,
        "AsistenciaRed",
        "Sistema Digital de Gestion de Asistencia Institucional\nPropuesta para Instituciones Educativas")

    story.append(Paragraph("Fecha: 2026 | Contacto: Mauricio Lepore · 11-6805-6796", S["CentroGris"]))
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=DORADO))
    story.append(Spacer(1, 0.4*cm))

    # Intro
    story.append(caja_destacada(
        "<b>AsistenciaRed</b> es una solucion web para la gestion digital de la asistencia escolar. "
        "Permite que docentes, preceptores y directivos accedan en tiempo real a los registros de asistencia "
        "desde cualquier dispositivo conectado a internet, sin instalar ninguna aplicacion."
    ))
    story.append(Spacer(1, 0.5*cm))

    # El problema
    story.append(Paragraph("El problema que resuelve", S["H1"]))
    story.append(Paragraph(
        "La gestion de asistencia en instituciones educativas sigue siendo, en su gran mayoria, un proceso "
        "manual basado en papel. Esto genera una serie de problemas concretos que afectan la eficiencia "
        "institucional y la calidad de la informacion disponible:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))

    problemas = [
        ("Registros dispersos y dificiles de consultar",
         "Cada docente lleva su propio cuaderno o planilla. No hay una vision unificada de la asistencia institucional."),
        ("Demoras en la deteccion de ausentismo",
         "El preceptor o directivo tarda dias o semanas en tener datos consolidados sobre la asistencia de los alumnos."),
        ("Errores de calculo",
         "Los porcentajes de asistencia se calculan a mano, con riesgo de error y perdida de tiempo docente."),
        ("Imposibilidad de trabajo remoto",
         "Un docente no puede consultar sus registros desde su casa ni desde otro dispositivo."),
        ("Falta de trazabilidad",
         "No queda registro claro de quien cargo la asistencia ni cuando, lo que dificulta la rendicion de cuentas."),
    ]
    story.append(tabla_pasos(problemas))
    story.append(Spacer(1, 0.5*cm))

    # La solucion
    story.append(Paragraph("La solucion: AsistenciaRed", S["H1"]))
    story.append(Paragraph(
        "AsistenciaRed digitaliza completamente el proceso de registro de asistencia y lo centraliza en una "
        "plataforma web accesible desde cualquier dispositivo con internet. Los datos se sincronizan en tiempo "
        "real entre todos los usuarios de la institucion.", S["Cuerpo"]))
    story.append(Spacer(1, 0.3*cm))

    story.append(chips(
        ["100% Web\nSin instalacion", "Tiempo real\nSincronizado", "Multi-rol\n4 perfiles",
         "Multi-curso\nTodos los cursos", "Datos en\nla nube"],
        [AZUL, AZUL_MED, VERDE, colors.HexColor("#2c7a7b"), colors.HexColor("#6b46c1")]
    ))
    story.append(Spacer(1, 0.5*cm))

    # Beneficios por rol
    story.append(Paragraph("Beneficios para cada actor institucional", S["H1"]))

    roles_ben = [
        ("👨‍🏫 Docente", AZUL, [
            "Toma asistencia desde el celular o la computadora en segundos.",
            "Calcula automaticamente los porcentajes de asistencia e inasistencia por alumno.",
            "Registra dias especiales: feriados, paros docentes, dias lluviosos.",
            "Accede al historial completo del curso desde cualquier dispositivo.",
            "Gestiona multiples cursos desde una sola plataforma.",
        ]),
        ("📋 Preceptor", VERDE, [
            "Ve en tiempo real el estado de asistencia de todos los cursos del dia.",
            "Detecta de inmediato que cursos no tienen asistencia registrada.",
            "Puede tomar asistencia en un curso cuando el docente esta ausente.",
            "Accede al resumen completo por curso: presencias, ausencias y porcentajes.",
        ]),
        ("🏫 Directivo", colors.HexColor("#6b46c1"), [
            "Tiene una vision global de la asistencia institucional en tiempo real.",
            "Consulta estadisticas mensuales por curso y por docente.",
            "Identifica rapidamente cursos con alto nivel de ausentismo.",
            "Cuenta con datos confiables para la toma de decisiones pedagogicas.",
        ]),
        ("⚙️ Administrador", colors.HexColor("#2c7a7b"), [
            "Registra la institucion y genera codigos de acceso para cada rol.",
            "Gestiona el alta de docentes y la asignacion de cursos.",
            "Carga los listados de alumnos por curso.",
            "Controla quienes tienen acceso al sistema.",
        ]),
    ]

    for nombre, color, items in roles_ben:
        header_row = [[Paragraph(nombre, ParagraphStyle("RolH", fontName="Helvetica-Bold",
                       fontSize=12, textColor=BLANCO))]]
        ht = Table(header_row, colWidths=[16*cm])
        ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),color),
                                ("TOPPADDING",(0,0),(-1,-1),8),
                                ("BOTTOMPADDING",(0,0),(-1,-1),8),
                                ("LEFTPADDING",(0,0),(-1,-1),14)]))
        story.append(ht)
        for item in items:
            story.append(Paragraph(f"• {item}", S["Item"]))
        story.append(Spacer(1, 0.3*cm))

    story.append(PageBreak())

    # Caracteristicas tecnicas
    story.append(Paragraph("Caracteristicas tecnicas", S["H1"]))

    tecnicas = [
        ["Tecnologia", "Aplicacion web progresiva. Funciona en cualquier navegador moderno (Chrome, Firefox, Safari)."],
        ["Compatibilidad", "Computadoras de escritorio, laptops, tablets y telefonos moviles (Android e iOS)."],
        ["Base de datos", "Firebase Realtime Database (Google). Datos sincronizados en tiempo real."],
        ["Seguridad", "Acceso por codigos unicos por rol. Sin registro de email ni contrasenas personales."],
        ["Disponibilidad", "99.9% de uptime garantizado por la infraestructura de Google Firebase."],
        ["Actualizaciones", "Automaticas. La institucion siempre usa la version mas reciente."],
        ["Sin instalacion", "No requiere descargar ninguna aplicacion. Se abre desde el navegador."],
    ]

    t = Table(tecnicas, colWidths=[4.5*cm, 11.5*cm])
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("TEXTCOLOR",     (0,0), (0,-1), AZUL),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [GRIS_CLR, BLANCO]),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("LINEBELOW",     (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6*cm))

    # Proceso de implementacion
    story.append(Paragraph("Proceso de implementacion", S["H1"]))
    story.append(Paragraph(
        "La puesta en marcha del sistema es rapida y no requiere conocimientos tecnicos avanzados. "
        "El proceso completo puede completarse en menos de una hora:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))

    impl = [
        ("Alta de la institucion", "El administrador crea la institucion en el sistema y obtiene los codigos de acceso para cada rol."),
        ("Carga de docentes", "Se registran los docentes y se genera un codigo unico para cada uno."),
        ("Carga de cursos y alumnos", "Se crean los cursos y se cargan los listados de alumnos (varones, mujeres y domiciliarios)."),
        ("Distribucion de codigos", "El administrador comparte los codigos con cada docente, preceptor y directivo."),
        ("Inicio de uso", "Cada usuario accede al sistema con su codigo desde su dispositivo y empieza a operar."),
    ]
    story.append(tabla_pasos(impl))
    story.append(Spacer(1, 0.6*cm))

    # Comparativa
    story.append(Paragraph("Comparativa con el metodo tradicional", S["H1"]))

    comp = [
        ["Aspecto", "Metodo tradicional (papel)", "AsistenciaRed"],
        ["Registro de asistencia", "Manual, en papel o planilla", "Digital, desde cualquier dispositivo"],
        ["Calculo de porcentajes", "Manual, propenso a errores", "Automatico e instantaneo"],
        ["Acceso a los datos", "Solo el docente, en el aula", "Todos los roles, en tiempo real"],
        ["Consolidacion institucional", "Dias o semanas de demora", "Instantanea"],
        ["Costo de materiales", "Papeleria, fotocopias, libros", "Sin costo de materiales"],
        ["Riesgo de perdida", "Alto (papel puede perderse)", "Cero (datos en la nube)"],
    ]

    t = Table(comp, colWidths=[4*cm, 6*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), AZUL),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANCO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1), (1,-1), "Helvetica"),
        ("FONTNAME",      (2,1), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR",     (2,1), (2,-1), VERDE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [GRIS_CLR, BLANCO]),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6*cm))

    # Contacto
    story.append(HRFlowable(width="100%", thickness=1, color=DORADO))
    story.append(Spacer(1, 0.3*cm))
    story.append(caja_destacada(
        "<b>Para consultas y contratacion:</b><br/>"
        "Mauricio Lepore | WhatsApp: 11-6805-6796<br/>"
        "Disponible para visitas institucionales, demostraciones y capacitacion del personal.",
        color_borde=AZUL, color_fondo=colors.HexColor("#ebf8ff")
    ))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"OK: {path}")

# ════════════════════════════════════════════════════
#  2. MANUAL ADMINISTRADOR
# ════════════════════════════════════════════════════
def pdf_admin():
    path = os.path.join(OUT, "AsistenciaRed_Manual_Administrador.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    COL = colors.HexColor("#2c7a7b")
    def hf(canv, d): header_footer(canv, d, "Manual del Administrador", COL)
    story = []

    portada_block(story, "Manual del Administrador",
                  "AsistenciaRed — Sistema Institucional", COL)

    story.append(caja_destacada(
        "El <b>Administrador</b> es el responsable de configurar y mantener el sistema. "
        "Registra la institucion, gestiona docentes y cursos, y distribuye los codigos de acceso.",
        color_borde=COL, color_fondo=colors.HexColor("#e6fffa")
    ))
    story.append(Spacer(1, 0.5*cm))

    # Acceso inicial
    story.append(Paragraph("1. Primer acceso: registrar la institucion", S["H1"]))
    story.append(Paragraph(
        "La primera vez que se usa el sistema, el administrador debe crear la institucion. "
        "Esto solo se hace una vez:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    pasos = [
        ("Abrir el sistema", "Ingresar la URL del sistema en el navegador del celular o computadora."),
        ("Crear la institucion", "Hacer clic en el link '¿Sos administrador? Registra tu institucion' en la pantalla de inicio."),
        ("Completar los datos", "Ingresar el nombre de la institucion, el ciclo lectivo (ej: 2026) y una contrasena de administrador."),
        ("Guardar los codigos", "El sistema genera automaticamente los codigos de acceso. GUARDARLOS en un lugar seguro."),
    ]
    story.append(tabla_pasos(pasos))
    story.append(Spacer(1, 0.4*cm))

    story.append(caja_destacada(
        "<b>Codigos que se generan:</b><br/>"
        "- <b>INST-XXXXXX</b>: codigo de la institucion. Se comparte con TODOS los usuarios como primer paso del login.<br/>"
        "- <b>PREC-XXXXXX</b>: codigo de preceptoria. Solo para el preceptor o preceptores.<br/>"
        "- <b>DIR-XXXXXX</b>: codigo de direccion. Solo para directivos.<br/>"
        "- <b>La contrasena que elegiste</b>: solo para el administrador.",
        color_borde=DORADO
    ))
    story.append(Spacer(1, 0.5*cm))

    # Gestion de docentes
    story.append(Paragraph("2. Agregar docentes", S["H1"]))
    story.append(Paragraph(
        "Una vez dentro del sistema como administrador, la pantalla principal muestra el panel de administracion:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    pasos2 = [
        ("Ir a la seccion 'Docentes'", "En el panel del administrador, buscar la tarjeta de Docentes."),
        ("Hacer clic en '+ Nuevo docente'", "Se abre un formulario para completar el nombre del docente."),
        ("Ingresar el nombre y guardar", "El sistema genera automaticamente un codigo DOC-XXXXXX unico para ese docente."),
        ("Compartir el codigo", "Anotarlo y enviarselo al docente. Ese codigo es su acceso personal al sistema."),
    ]
    story.append(tabla_pasos(pasos2))
    story.append(Spacer(1, 0.4*cm))

    # Gestion de cursos
    story.append(Paragraph("3. Crear cursos", S["H1"]))
    pasos3 = [
        ("Ir a la seccion 'Cursos'", "En el panel del administrador, buscar la tarjeta de Cursos."),
        ("Hacer clic en '+ Nuevo curso'", "Se abre un formulario para completar nombre del curso y asignar un docente."),
        ("Completar el formulario", "Ingresar el nombre del curso y seleccionar el docente responsable de la lista."),
        ("Guardar", "El curso queda creado y asociado al docente seleccionado."),
    ]
    story.append(tabla_pasos(pasos3))
    story.append(Spacer(1, 0.5*cm))

    # Gestion de alumnos
    story.append(Paragraph("4. Cargar alumnos", S["H1"]))
    story.append(Paragraph(
        "Los alumnos se cargan dentro de cada curso. Hay tres categorias:", S["Cuerpo"]))
    for cat, desc in [
        ("♂ Varones", "Alumnos varones que asisten presencialmente."),
        ("♀ Mujeres", "Alumnas mujeres que asisten presencialmente."),
        ("🏠 Domiciliarios", "Alumnos con modalidad domiciliaria. Cuentan como inscriptos pero no tienen registro de asistencia diaria."),
    ]:
        story.append(Paragraph(f"<b>{cat}:</b> {desc}", S["Item"]))
    story.append(Spacer(1, 0.2*cm))
    pasos4 = [
        ("Hacer clic en '👥 Alumnos' del curso", "Se abre el panel de gestion de alumnos para ese curso."),
        ("Elegir la categoria correcta", "Varones, Mujeres o Domiciliarios segun corresponda."),
        ("Escribir 'Apellido, Nombre' y hacer clic en '+'", "El alumno queda agregado a la lista."),
        ("Repetir para todos los alumnos", "Se pueden agregar y eliminar alumnos en cualquier momento."),
    ]
    story.append(tabla_pasos(pasos4))
    story.append(Spacer(1, 0.5*cm))

    # Ver codigos
    story.append(Paragraph("5. Ver y copiar codigos de acceso", S["H1"]))
    story.append(Paragraph(
        "En cualquier momento, el administrador puede ver los codigos de acceso de la institucion "
        "en la tarjeta 'Codigos de acceso' del panel. Cada codigo tiene un boton 'Copiar' para "
        "facilitar su envio por WhatsApp u otro medio.", S["Cuerpo"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=COL))
    story.append(Spacer(1, 0.3*cm))
    story.append(caja_destacada(
        "<b>Consejos importantes:</b><br/>"
        "- Guardar todos los codigos en un lugar seguro antes de cerrar sesion.<br/>"
        "- Los codigos no cambian a menos que se cree una nueva institucion.<br/>"
        "- Si un docente pierde su codigo, el administrador puede verlo en la lista de docentes.<br/>"
        "- Se pueden agregar y eliminar docentes, cursos y alumnos en cualquier momento.",
        color_borde=COL, color_fondo=colors.HexColor("#e6fffa")
    ))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"OK: {path}")

# ════════════════════════════════════════════════════
#  3. MANUAL DOCENTE
# ════════════════════════════════════════════════════
def pdf_docente():
    path = os.path.join(OUT, "AsistenciaRed_Manual_Docente.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    COL = AZUL
    def hf(canv, d): header_footer(canv, d, "Manual del Docente", COL)
    story = []

    portada_block(story, "Manual del Docente",
                  "AsistenciaRed — Sistema Institucional", COL)

    story.append(caja_destacada(
        "Como <b>docente</b>, el sistema te permite registrar la asistencia de tus cursos dia a dia, "
        "consultar el historial y ver estadisticas completas por alumno, todo desde tu celular o computadora."
    ))
    story.append(Spacer(1, 0.5*cm))

    # Primer acceso
    story.append(Paragraph("1. Primer acceso al sistema", S["H1"]))
    pasos = [
        ("Abrir la URL en el navegador", "Ingresar la direccion web del sistema en Chrome, Firefox o Safari."),
        ("Ingresar el codigo de la institucion", "El administrador te lo proporciona. Tiene el formato INST-XXXXXX."),
        ("Seleccionar el rol 'Docente'", "Hacer clic en la opcion 'Docente' en la pantalla de seleccion de rol."),
        ("Ingresar tu codigo personal", "El administrador te asigna un codigo unico con formato DOC-XXXXXX. Ese es tu acceso."),
        ("Listo", "El sistema te recuerda en el mismo dispositivo, no es necesario volver a ingresar el codigo."),
    ]
    story.append(tabla_pasos(pasos))
    story.append(Spacer(1, 0.5*cm))

    # Tomar asistencia
    story.append(Paragraph("2. Tomar asistencia del dia", S["H1"]))
    story.append(Paragraph(
        "Al ingresar al sistema ves la pantalla de asistencia con la fecha de hoy. "
        "Si tenes mas de un curso, aparecen pestanas para cambiar entre ellos:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    pasos2 = [
        ("Verificar la fecha", "La fecha actual aparece en el centro. Usa las flechas para navegar a otro dia si necesitas corregir."),
        ("Seleccionar el tipo de dia", "Normal / Feriado / Paro / Lluvia. Si no es un dia normal, los botones de asistencia se deshabilitan."),
        ("Agregar el dia si no esta creado", "Si el dia no existe en el registro, aparece el boton '+ Agregar este dia'."),
        ("Marcar cada alumno", "Toca el boton al lado del nombre para alternar entre Presente (P), Ausente (A) y sin marcar."),
        ("Los cambios se guardan solos", "Cada toque se guarda automaticamente en la nube. No hay boton de guardar."),
    ]
    story.append(tabla_pasos(pasos2))
    story.append(Spacer(1, 0.4*cm))

    story.append(caja_destacada(
        "<b>Tipos de dia:</b><br/>"
        "- <b>Normal</b>: dia habil. Se registra asistencia.<br/>"
        "- <b>Feriado</b>: no cuenta como dia habil ni afecta porcentajes.<br/>"
        "- <b>Paro docente</b>: no cuenta como dia habil.<br/>"
        "- <b>Dia lluvioso</b>: no cuenta como dia habil."
    ))
    story.append(Spacer(1, 0.5*cm))

    # Ver resumen
    story.append(Paragraph("3. Ver el resumen de asistencia", S["H1"]))
    story.append(Paragraph(
        "Hace clic en el boton <b>Resumen</b> para ver las estadisticas acumuladas del curso:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))

    estadisticas = [
        ["Estadistica", "Descripcion"],
        ["Total inscriptos", "Cantidad total de alumnos del curso (incluyendo domiciliarios)."],
        ["Dias habiles", "Cantidad de dias con registro de tipo Normal."],
        ["Total asistencias", "Suma de todas las presencias registradas en el curso."],
        ["Total inasistencias", "Suma de todas las ausencias registradas en el curso."],
        ["% Asistencia", "Presencias / (dias habiles x alumnos) x 100."],
        ["% Inasistencia", "Ausencias / (dias habiles x alumnos) x 100."],
        ["% Asistencia media", "Promedio de los porcentajes individuales de cada alumno."],
    ]
    t = Table(estadisticas, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), AZUL),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANCO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1), AZUL),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [GRIS_CLR, BLANCO]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Tabla por alumno", S["H2"]))
    story.append(Paragraph(
        "Debajo de las estadisticas generales aparece una tabla detallada por alumno con sus presencias, "
        "ausencias, porcentaje de asistencia y porcentaje de inasistencia individuales. "
        "Los alumnos con menos del 75% de asistencia aparecen en rojo.", S["Cuerpo"]))
    story.append(Spacer(1, 0.5*cm))

    # Multiples cursos
    story.append(Paragraph("4. Gestionar multiples cursos", S["H1"]))
    story.append(Paragraph(
        "Si el administrador te asigno mas de un curso, aparecen pestanas en la parte superior de la pantalla "
        "con el nombre de cada curso. Podes cambiar entre cursos con un solo toque. "
        "El boton Resumen siempre muestra las estadisticas del curso activo.", S["Cuerpo"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=DORADO))
    story.append(Spacer(1, 0.3*cm))
    story.append(caja_destacada(
        "<b>Preguntas frecuentes:</b><br/>"
        "- <b>¿Puedo corregir un dia anterior?</b> Si. Usa las flechas de fecha para ir al dia que quieras editar.<br/>"
        "- <b>¿Que pasa si me quedo sin internet?</b> El sistema requiere conexion para guardar. Espera tener senial antes de tomar asistencia.<br/>"
        "- <b>¿Puedo entrar desde el celular?</b> Si, funciona desde cualquier navegador en cualquier dispositivo.<br/>"
        "- <b>¿Los datos se pierden si cierro el navegador?</b> No. Todo se guarda en la nube automaticamente."
    ))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"OK: {path}")

# ════════════════════════════════════════════════════
#  4. MANUAL PRECEPTOR
# ════════════════════════════════════════════════════
def pdf_preceptor():
    path = os.path.join(OUT, "AsistenciaRed_Manual_Preceptor.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    COL = VERDE
    def hf(canv, d): header_footer(canv, d, "Manual del Preceptor", COL)
    story = []

    portada_block(story, "Manual del Preceptor",
                  "AsistenciaRed — Sistema Institucional", COL)

    story.append(caja_destacada(
        "Como <b>preceptor</b>, el sistema te da una vision completa de la asistencia de todos los cursos "
        "en tiempo real. Podas ver el estado del dia, consultar el resumen por curso y tomar asistencia "
        "cuando un docente esta ausente.",
        color_borde=COL, color_fondo=colors.HexColor("#f0fff4")
    ))
    story.append(Spacer(1, 0.5*cm))

    # Acceso
    story.append(Paragraph("1. Acceso al sistema", S["H1"]))
    pasos = [
        ("Abrir la URL en el navegador", "Ingresar la direccion web del sistema."),
        ("Ingresar el codigo de la institucion", "Formato INST-XXXXXX. Te lo proporciona el administrador."),
        ("Seleccionar el rol 'Preceptor'", "Hacer clic en la opcion Preceptor en la pantalla de seleccion de rol."),
        ("Ingresar el codigo de preceptoria", "Formato PREC-XXXXXX. Es unico para toda la preceptoria, no por persona."),
    ]
    story.append(tabla_pasos(pasos))
    story.append(Spacer(1, 0.5*cm))

    # Vista del dia
    story.append(Paragraph("2. Vista de asistencia del dia", S["H1"]))
    story.append(Paragraph(
        "Al ingresar, ves la pantalla principal con la tabla de todos los cursos para la fecha actual. "
        "Podes navegar entre dias con las flechas o volver a hoy con el boton 'Hoy':", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))

    estados = [
        ["Estado", "Significado"],
        ["Sin registrar", "El docente todavia no tomo asistencia para este dia. Podes tomarla vos."],
        ["Registrada", "El docente ya registro la asistencia. Muestra la cantidad de presentes, ausentes y sin marcar."],
        ["Feriado / Paro / Lluvia", "Dia no habil. No cuenta para el calculo de porcentajes."],
    ]
    t = Table(estados, colWidths=[4.5*cm, 11.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), COL),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANCO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1), COL),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [GRIS_CLR, BLANCO]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Tomar asistencia
    story.append(Paragraph("3. Tomar asistencia por ausencia del docente", S["H1"]))
    story.append(Paragraph(
        "Cuando un docente esta ausente y no registro la asistencia, el sistema te muestra un boton "
        "<b>'Tomar'</b> en la columna de estado de ese curso. Asi funciona:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    pasos2 = [
        ("Identificar el curso sin registrar", "En la tabla del dia, buscar los cursos con estado 'Sin registrar'."),
        ("Hacer clic en 'Tomar'", "Se abre la pantalla completa de toma de asistencia para ese curso, igual que la vista del docente."),
        ("Agregar el dia", "Hacer clic en '+ Agregar este dia' para habilitar el registro."),
        ("Registrar la asistencia", "Tocar el boton de cada alumno para marcar Presente (P) o Ausente (A)."),
        ("Volver a la tabla general", "Hacer clic en '← Volver a todos los cursos'."),
    ]
    story.append(tabla_pasos(pasos2))
    story.append(Spacer(1, 0.4*cm))

    story.append(caja_destacada(
        "<b>Importante:</b> La preceptoria solo puede tomar asistencia en cursos donde el dia no fue registrado. "
        "Si el docente ya registro el dia, el registro queda como solo lectura para el preceptor.",
        color_borde=DORADO
    ))
    story.append(Spacer(1, 0.5*cm))

    # Resumen
    story.append(Paragraph("4. Ver resumen por curso", S["H1"]))
    story.append(Paragraph(
        "Hace clic en el boton <b>Resumen por curso</b> para acceder a las estadisticas detalladas. "
        "Aparecen pestanas con cada curso. Al seleccionar uno, ves:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    for item in [
        "Tarjetas de resumen: inscriptos, dias habiles, total asistencias, total inasistencias, % asistencia, % inasistencia y % media.",
        "Tabla detallada por alumno con presencias, ausencias y porcentajes individuales.",
        "Alumnos con menos del 75% de asistencia marcados en rojo para facil identificacion.",
    ]:
        story.append(Paragraph(f"• {item}", S["Item"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=COL))
    story.append(Spacer(1, 0.3*cm))
    story.append(caja_destacada(
        "<b>Recordatorio:</b><br/>"
        "- El sistema actualiza la informacion en tiempo real. No es necesario recargar la pagina.<br/>"
        "- Podes acceder desde tu celular, tablet o computadora.<br/>"
        "- El codigo de preceptoria es compartido entre todos los preceptores de la institucion.",
        color_borde=COL, color_fondo=colors.HexColor("#f0fff4")
    ))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"OK: {path}")

# ════════════════════════════════════════════════════
#  5. MANUAL DIRECTIVO
# ════════════════════════════════════════════════════
def pdf_directivo():
    path = os.path.join(OUT, "AsistenciaRed_Manual_Directivo.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    COL = colors.HexColor("#6b46c1")
    def hf(canv, d): header_footer(canv, d, "Manual del Directivo", COL)
    story = []

    portada_block(story, "Manual del Directivo",
                  "AsistenciaRed — Sistema Institucional", COL)

    story.append(caja_destacada(
        "Como <b>directivo</b>, el sistema te da acceso a la informacion global de la institucion: "
        "estadisticas de asistencia por curso, comparativas mensuales y el resumen detallado por alumno "
        "de cualquier curso, todo en tiempo real.",
        color_borde=COL, color_fondo=colors.HexColor("#faf5ff")
    ))
    story.append(Spacer(1, 0.5*cm))

    # Acceso
    story.append(Paragraph("1. Acceso al sistema", S["H1"]))
    pasos = [
        ("Abrir la URL en el navegador", "Ingresar la direccion web del sistema desde cualquier dispositivo."),
        ("Ingresar el codigo de la institucion", "Formato INST-XXXXXX. Te lo proporciona el administrador."),
        ("Seleccionar el rol 'Directivo'", "Hacer clic en la opcion Directivo en la pantalla de seleccion de rol."),
        ("Ingresar el codigo de direccion", "Formato DIR-XXXXXX. Es unico para el rol directivo de la institucion."),
    ]
    story.append(tabla_pasos(pasos))
    story.append(Spacer(1, 0.5*cm))

    # Vista global
    story.append(Paragraph("2. Vista global de la institucion", S["H1"]))
    story.append(Paragraph(
        "La pantalla principal muestra la <b>Vista global</b> con estadisticas del mes en curso:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))

    tarjetas = [
        ["Tarjeta", "Informacion que muestra"],
        ["Cursos", "Cantidad total de cursos activos en la institucion."],
        ["Docentes", "Cantidad de docentes registrados en el sistema."],
        ["Alumnos", "Total de alumnos inscriptos en todos los cursos."],
        ["% Asist. mes", "Porcentaje global de asistencia para el mes actual."],
        ["Presencias mes", "Total de presencias registradas en el mes actual."],
        ["Ausencias mes", "Total de ausencias registradas en el mes actual."],
    ]
    t = Table(tarjetas, colWidths=[4.5*cm, 11.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), COL),
        ("TEXTCOLOR",     (0,0), (-1,0), BLANCO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1), COL),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [GRIS_CLR, BLANCO]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Tabla de resumen por curso", S["H2"]))
    story.append(Paragraph(
        "Debajo de las tarjetas, una tabla muestra el resumen del mes por curso con: nombre del curso, "
        "docente a cargo, cantidad de alumnos, dias registrados y porcentaje de asistencia. "
        "Los cursos con menos del 75% aparecen en rojo.", S["Cuerpo"]))
    story.append(Spacer(1, 0.5*cm))

    # Resumen por curso
    story.append(Paragraph("3. Resumen detallado por curso", S["H1"]))
    story.append(Paragraph(
        "Hace clic en el boton <b>Resumen por curso</b> para acceder al detalle completo de cualquier curso. "
        "Selecciona el curso con las pestanas superiores:", S["Cuerpo"]))
    story.append(Spacer(1, 0.2*cm))
    for item in [
        "Tarjetas de resumen acumulado: inscriptos, dias habiles, total asistencias, inasistencias, % asistencia, % inasistencia y % asistencia media.",
        "Tabla por alumno con presencias, ausencias, % asistencia y % inasistencia individuales.",
        "Identificacion visual de alumnos en riesgo (menos del 75% de asistencia).",
    ]:
        story.append(Paragraph(f"• {item}", S["Item"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(caja_destacada(
        "<b>Uso sugerido para la gestion institucional:</b><br/>"
        "- Revisar la Vista global al inicio de cada semana para detectar cursos con bajo porcentaje de asistencia.<br/>"
        "- Consultar el Resumen por curso antes de entrevistas con docentes o familias.<br/>"
        "- Los datos se actualizan en tiempo real: lo que ves refleja el estado actual del sistema.",
        color_borde=COL, color_fondo=colors.HexColor("#faf5ff")
    ))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("4. Informacion que el directivo NO puede modificar", S["H1"]))
    story.append(Paragraph(
        "El rol directivo es de <b>solo lectura</b>. No puede modificar la asistencia, agregar ni eliminar "
        "alumnos, cursos o docentes. Para esas acciones, se requiere el acceso de administrador.", S["Cuerpo"]))
    story.append(Spacer(1, 0.4*cm))

    story.append(HRFlowable(width="100%", thickness=1, color=COL))
    story.append(Spacer(1, 0.3*cm))
    story.append(caja_destacada(
        "<b>Ventajas clave para la conduccion institucional:</b><br/>"
        "- Informacion actualizada en tiempo real, sin depender de informes manuales.<br/>"
        "- Acceso desde cualquier dispositivo, dentro o fuera de la institucion.<br/>"
        "- Vision completa: desde estadisticas globales hasta el historial de cada alumno.",
        color_borde=DORADO
    ))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"OK: {path}")

# ── MAIN ────────────────────────────────────────────
if __name__ == "__main__":
    pdf_propuesta()
    pdf_admin()
    pdf_docente()
    pdf_preceptor()
    pdf_directivo()
    print("Todos los PDFs generados correctamente.")
