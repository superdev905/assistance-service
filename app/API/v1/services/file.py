from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from ..helpers.format_date import format_date_to_string


def create_visit_report(data):
    date_string = format_date_to_string()
    report_name = 'Reporte'+data["correlative"]
    report = SimpleDocTemplate("./"+report_name, topMargin=2.54*cm,
                               bottomMargin=2.54*cm,
                               leftMargin=2.54*cm,
                               rightMargin=2.54*cm)

    styles = getSampleStyleSheet()
    title = "Reporte Visita "+data["correlative"]
    hero = "Informo a usted con respecto a la visita realizada el dia " + \
        date_string + " a la obra " + \
        data["construction_name"] + \
        " por " + \
        data["user"] + \
        " , profesional de atencién en obra de la Fundacion Social C.Ch.C.."
    sub_intro = "En la ocasión se obtuvo el siguiente resultado:"
    result = {
        "Trabjadores atendidos": '<b>' + data["total"] + ' personas</b>',
        "Charlas": "No se realizaron",
        "Folletos": "No se realizaron",
        "Afiches": "No se realizaron",
        "Casos relevantes": data["relevant"],
        "Observaciones de la visita": data["observations"],

    }
    table_data = []
    table_style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black, ),
                   ("BACKGROUND", (0, 0), (0, 0), colors.lightgrey),
                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                   ]
    index = 0
    for k, v in result.items():
        index = index + 1
        table_data.append([Paragraph(k), Paragraph(v)])
        table_style.append(
            ("BACKGROUND", (0, index), (0, 0), colors.lightgrey))

    result_table = Table(data=table_data, style=table_style,
                         hAlign="LEFT", colWidths=["30%", "70%"])
    report_title = Paragraph(title, styles["h1"])
    report_intro = Paragraph(hero)
    report_sub_intro = Paragraph(sub_intro)
    report_sub_intro.spaceAfter = 20
    result_table.spaceAfter = 15
    report_greenting_title = Paragraph("Atentamente")
    report_greenting_title.spaceAfter = 5
    professional_data = {
        "names": "<b>" + data["user"] + "</b>",
        "charge": "Asistente Social Atención Social Empresas",
        "phone": "Teléfono: "+data["user_phone"],
        "email": data["user_email"],
        "entity": "<b>FUNDACION SOCIAL C.Ch.c.</b>",
        "entity_phrase": "SOMOS C.CH.C."
    }
    sign_elements = []
    style_right = ParagraphStyle(name='right', parent=styles[
        'Normal'])
    for k, v in professional_data.items():
        sign_elements.append(Paragraph(v, style_right))

    report.build([report_title, report_intro, report_sub_intro, result_table,
                 report_greenting_title, *sign_elements])
    return report_name
