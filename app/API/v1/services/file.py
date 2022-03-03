import requests
from io import BytesIO
from reportlab.platypus import Paragraph, Table
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from app.settings import SERVICES


def render_item(quantity, end="persona", empty="No se realizaron") -> str:
    if quantity == 0:
        return empty
    if quantity == 1:
        return str(quantity) + " " + end
    return str(quantity) + " " + end + "s"


def render_table_item(value, end="persona", empty="No se realizaron") -> str:
    if (isinstance(value, int)):
        return render_item(value, end, empty)
    return value


def upload_report(filename, file):
    files = {'file': (filename, file, 'application/pdf')}
    response = requests.post(
        SERVICES["parameters"]+"/file/upload", files=files)
    return response.json()


def create_visit_report(token: str, data):

    buffer = BytesIO()
    date_string = data["date"]
    report_name = 'Reporte'+data["correlative"] + ".pdf"
    report = SimpleDocTemplate(buffer,
                               topMargin=2.54*cm,
                               bottomMargin=2.54*cm,
                               leftMargin=2.54*cm,
                               rightMargin=2.54*cm)

    styles = getSampleStyleSheet()
    title = "Reporte Visita "+data["correlative"]
    hero = "Informo a usted con respecto a la visita realizada el dia " + \
        date_string + " a la obra " + \
        data["construction_name"] + \
        " por " + data["user"] + \
        " , profesional de atencién en obra de la Fundacion Social C.Ch.C.."
    sub_intro = "En la ocasión se obtuvo el siguiente resultado:"
    table_data = []
    table_style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black, ),
                   ("BACKGROUND", (0, 0), (0, 0), colors.lightgrey),
                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                   ]
    index = 0
    for item in data["table_data"]:
        index = index + 1
        table_data.append([Paragraph(item["display"]),
                           Paragraph(render_table_item(item["data"]))])
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

    files = {'file': (report_name,  buffer.getvalue(), "application/pdf")}
    print(SERVICES["parameters"]+"/file/upload")
    response = requests.post(
        SERVICES["parameters"]+"/file/upload", files=files, headers={
            "Authorization": "Bearer %s" % token
        })
    buffer.seek(0)
    return response.json()
