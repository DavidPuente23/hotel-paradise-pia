"""Genera los documentos en Word a partir de los archivos Markdown.

Uso:
    python docs/generar_documentos.py

Convierte DOCUMENTO_TECNICO.md y MANUAL_USUARIO.md a formato .docx con
portada, títulos, listas, tablas e imágenes.
"""

import io
import re
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

BASE_DIR = Path(__file__).resolve().parent
AZUL = RGBColor(0x1F, 0x3C, 0x5A)
GRIS = RGBColor(0x6C, 0x75, 0x7D)


def configurar_estilos(documento):
    estilo = documento.styles['Normal']
    estilo.font.name = 'Calibri'
    estilo.font.size = Pt(11)
    estilo.paragraph_format.space_after = Pt(6)
    estilo.paragraph_format.line_spacing = 1.15

    for nivel, tamanio in [('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 12)]:
        encabezado = documento.styles[nivel]
        encabezado.font.name = 'Calibri'
        encabezado.font.size = Pt(tamanio)
        encabezado.font.color.rgb = AZUL
        encabezado.font.bold = True
        encabezado.paragraph_format.keep_with_next = True
        encabezado.paragraph_format.space_before = Pt(12 if nivel != 'Heading 1' else 0)
        encabezado.paragraph_format.space_after = Pt(4)

    for nombre in ['List Bullet', 'List Bullet 2', 'List Bullet 3', 'List Number']:
        try:
            lista = documento.styles[nombre]
        except KeyError:
            continue
        lista.paragraph_format.space_after = Pt(2)
        lista.paragraph_format.line_spacing = 1.1

    for seccion in documento.sections:
        seccion.top_margin = Inches(1)
        seccion.bottom_margin = Inches(1)
        seccion.left_margin = Inches(1)
        seccion.right_margin = Inches(1)


def escribir_texto_con_formato(parrafo, texto):
    """Escribe texto aplicando **negritas** y `código`."""
    partes = re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', texto)
    for parte in partes:
        if not parte:
            continue
        if parte.startswith('**') and parte.endswith('**'):
            run = parrafo.add_run(parte[2:-2])
            run.bold = True
        elif parte.startswith('`') and parte.endswith('`'):
            run = parrafo.add_run(parte[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
        else:
            parrafo.add_run(parte)


def agregar_tabla(documento, filas):
    if not filas:
        return
    columnas = len(filas[0])
    tabla = documento.add_table(rows=0, cols=columnas)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    try:
        tabla.style = 'Light Grid Accent 1'
    except KeyError:
        tabla.style = 'Table Grid'

    for indice, fila in enumerate(filas):
        celdas = tabla.add_row().cells
        for posicion, contenido in enumerate(fila[:columnas]):
            celdas[posicion].text = ''
            parrafo = celdas[posicion].paragraphs[0]
            escribir_texto_con_formato(parrafo, contenido)
            for run in parrafo.runs:
                run.font.size = Pt(9.5)
                if indice == 0:
                    run.bold = True
    documento.add_paragraph()


def dividir_tabla(linea):
    return [celda.strip() for celda in linea.strip().strip('|').split('|')]


def agregar_imagen(documento, ruta, descripcion):
    archivo = BASE_DIR / ruta
    if not archivo.exists():
        parrafo = documento.add_paragraph(f'[Imagen no encontrada: {ruta}]')
        parrafo.runs[0].font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)
        return
    documento.add_picture(str(archivo), width=Inches(6.1))
    documento.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    pie = documento.add_paragraph()
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = pie.add_run(descripcion)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = GRIS


def insertar_portada(ruta_docx):
    """Coloca la portada oficial al inicio del documento, en su propia sección.

    Se copia el contenido de portada.docx conservando sus márgenes, su borde de
    página y sus imágenes, y se cierra la sección con un salto de página para que
    el cuerpo del documento empiece en la página siguiente.
    """
    destino = Document(str(ruta_docx))
    portada = Document(str(BASE_DIR / 'portada.docx'))

    cuerpo_destino = destino.element.body
    cuerpo_portada = portada.element.body
    primero = cuerpo_destino[0]

    # Registrar en el documento destino las imágenes de la portada
    for imagen in cuerpo_portada.iter(qn('a:blip')):
        r_id = imagen.get(qn('r:embed'))
        if not r_id:
            continue
        parte = portada.part.related_parts[r_id]
        nuevo_r_id, _ = destino.part.get_or_add_image(io.BytesIO(parte.blob))
        imagen.set(qn('r:embed'), nuevo_r_id)

    for elemento in list(cuerpo_portada.iterchildren()):
        if elemento.tag == qn('w:sectPr'):
            continue
        primero.addprevious(deepcopy(elemento))

    # Propiedades de la sección de la portada (márgenes y borde de página)
    seccion_portada = deepcopy(cuerpo_portada.find(qn('w:sectPr')))
    salto = OxmlElement('w:p')
    propiedades = OxmlElement('w:pPr')
    propiedades.append(seccion_portada)
    salto.append(propiedades)
    primero.addprevious(salto)

    destino.save(str(ruta_docx))


def convertir_markdown(ruta_md, ruta_docx):
    lineas = ruta_md.read_text(encoding='utf-8').splitlines()

    # La portada oficial vive en portada.docx; el contenido empieza tras el primer separador
    corte = lineas.index('---') if '---' in lineas else 0
    cuerpo = lineas[corte + 1:]

    documento = Document()
    configurar_estilos(documento)

    i = 0
    while i < len(cuerpo):
        linea = cuerpo[i]

        # Bloques de código
        if linea.strip().startswith('```'):
            i += 1
            codigo = []
            while i < len(cuerpo) and not cuerpo[i].strip().startswith('```'):
                codigo.append(cuerpo[i])
                i += 1
            i += 1
            parrafo = documento.add_paragraph()
            parrafo.paragraph_format.left_indent = Inches(0.3)
            run = parrafo.add_run('\n'.join(codigo))
            run.font.name = 'Consolas'
            run.font.size = Pt(9)
            continue

        # Imágenes
        coincidencia = re.match(r'!\[(.*?)\]\((.*?)\)', linea.strip())
        if coincidencia:
            agregar_imagen(documento, coincidencia.group(2), coincidencia.group(1))
            i += 1
            continue

        # Tablas
        if linea.strip().startswith('|'):
            filas = []
            while i < len(cuerpo) and cuerpo[i].strip().startswith('|'):
                contenido = dividir_tabla(cuerpo[i])
                if not all(re.fullmatch(r':?-{2,}:?', celda or '---') for celda in contenido):
                    filas.append(contenido)
                i += 1
            agregar_tabla(documento, filas)
            continue

        # Encabezados
        if linea.startswith('#'):
            nivel = len(linea) - len(linea.lstrip('#'))
            texto = linea[nivel:].strip()
            if nivel == 1:
                documento.add_heading(texto, level=0)
            else:
                documento.add_heading(texto, level=min(nivel - 1, 3))
            i += 1
            continue

        # Separadores
        if linea.strip() == '---':
            i += 1
            continue

        # Citas
        if linea.strip().startswith('> '):
            parrafo = documento.add_paragraph()
            parrafo.paragraph_format.left_indent = Inches(0.4)
            escribir_texto_con_formato(parrafo, linea.strip()[2:])
            for run in parrafo.runs:
                run.italic = True
                run.font.color.rgb = GRIS
            i += 1
            continue

        # Listas
        if re.match(r'^\s*[-*] ', linea):
            sangria = len(linea) - len(linea.lstrip(' '))
            nivel = min(sangria // 3 + 1, 3)
            estilo = 'List Bullet' if nivel == 1 else f'List Bullet {nivel}'
            try:
                parrafo = documento.add_paragraph(style=estilo)
            except KeyError:
                parrafo = documento.add_paragraph(style='List Bullet')
            escribir_texto_con_formato(parrafo, re.sub(r'^\s*[-*] ', '', linea))
            i += 1
            continue

        if re.match(r'^\s*\d+\. ', linea):
            parrafo = documento.add_paragraph(style='List Number')
            escribir_texto_con_formato(parrafo, re.sub(r'^\s*\d+\. ', '', linea))
            i += 1
            continue

        # Líneas vacías
        if not linea.strip():
            i += 1
            continue

        # Párrafo normal
        parrafo = documento.add_paragraph()
        escribir_texto_con_formato(parrafo, linea.strip())
        i += 1

    documento.save(ruta_docx)
    insertar_portada(ruta_docx)
    print(f'Documento generado: {ruta_docx.name}')


if __name__ == '__main__':
    convertir_markdown(BASE_DIR / 'DOCUMENTO_TECNICO.md', BASE_DIR / 'Documento_Tecnico.docx')
    convertir_markdown(BASE_DIR / 'MANUAL_USUARIO.md', BASE_DIR / 'Manual_de_Usuario.docx')
    convertir_markdown(BASE_DIR / 'GUION_VIDEO.md', BASE_DIR / 'Guion_Video.docx')
