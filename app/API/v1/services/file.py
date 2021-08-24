from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


def create_visit_report():

    report = SimpleDocTemplate("./report.pdf", topMargin=2.54*cm,
                               bottomMargin=2.54*cm,
                               leftMargin=2.54*cm,
                               rightMargin=2.54*cm)

    styles = getSampleStyleSheet()
    title = "Reporte Visita 3"
    hero = "Informo a usted con respecto a la visita realizada el dia Lunes 07 de Diciembre de 2020, a la obra Manquecura valle Lo Campino por Alexandra Aguirre Lastra, profesional de atencién en obra de la Fundacion Social C.Ch.C.."
    sub_intro = "En la ocasión se obtuvo el siguiente resultado:"
    result = {
        "Trabjadores atendidos": '<b>10 personas</b>',
        "Charlas": "No se realizaron",
        "Folletos": "No se realizaron",
        "Afiches": "No se realizaron",
        "Casos relevantes": "Enim nec dui nunc mattis enim ut tellus elementum sagittis. Dolor purus non enim praesent. Amet aliquam id diam maecenas ultricies mi. Netus et malesuada fames ac. Vitae purus faucibus ornare suspendisse sed nisi lacus. Ac turpis egestas sed tempus. Magna sit amet purus gravida quis. Senectus et netus et malesuada",
        "Observaciones de la visita": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",

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
        "names": "<b>Alexandra Aguirre Lastra</b>",
        "charge": "Asistente Social Atención Social Empresas",
        "phone": "Teléfono: (02)25858000",
        "email": "aaguirre@fundacioncchc.cl",
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
    return 'created'
