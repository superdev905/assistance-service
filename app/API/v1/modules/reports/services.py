
from fastapi.encoders import jsonable_encoder
import xlsxwriter
from fastapi import Request
from typing import List
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm.session import Session
from app.settings import SERVICES
from ...helpers.fetch_data import fetch_users_service, get_managment_data
from ...services.file import create_visit_report
from ..assistance.model import Assistance


def validateValue(value):
    if(value == None):
        return ''
    else: 
        return value


def generate_visits_excel(req: Request,
                          list: List[dict],
                          start_date: datetime,
                          end_date: datetime) -> None:

    dataList = []
    for item in list:
        user = fetch_users_service(req.token, str(item["assigned_id"]))
        user_name = (f"{user['names']} {user['paternal_surname']} {user['maternal_surname']}")

        dataList.append({**item, "assigned": user_name,
                        "date": item["date"].strftime('%d-%m-%Y'),
                         "end_date": item["end_date"].strftime('%H:%M:%S'),
                         "start_date": item["start_date"].strftime('%H:%M:%S'),
                         "shift_name": item["shift_name"].capitalize(),
                         "status": item["status"].capitalize(),
                         "business_name": validateValue(item["business_name"]),
                         "construction_name": validateValue(item["construction_name"])
                         })

    headings = [{"name": "Fecha", "width": 10},
                {"name": "Hora de inicio", "width": 20},
                {"name": "Hora de fin", "width": 20},
                {"name": "Estado", "width": 15},
                {"name": "Jornada", "width": 15},
                {"name": "Título", "width": 50},
                {"name": "Profesional", "width": 20},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Observaciones", "width": 100}]

    attrs = ["date", 
            "start_date", 
            "end_date", 
            "status",
            "shift_name",
            "title", 
            "assigned",
            "business_name", 
            "construction_name",
            "observation"]

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    })

    if(start_date == None and end_date == None):
        worksheet.write(1, 0, "Todos los Registros de Visitas a la Fecha")

    elif(start_date and end_date):
        worksheet.write(1, 0, "Visitas del " +
                    start_date.strftime('%d-%m-%Y') + " al " + end_date.strftime('%d-%m-%Y'))
        
    elif (end_date == None):
        worksheet.write(1, 0, "Visitas del " +
                    start_date.strftime('%d-%m-%Y') + " a la Fecha")
        
    elif (start_date == None):
        worksheet.write(1, 0, "Visitas desde el inicio hasta " + end_date.strftime('%d-%m-%Y'))

    

    heading_index = 0
    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    row = 4

    for item in dataList:
        col = 0
        for attr in attrs:
            worksheet.write(
                row, col, item[attr], cell)
            col += 1

        row += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output

def generate_visits_by_company_excel(req: Request, list: List[dict], company_name: str, start_: datetime, end_: datetime):

    dataList = []
    for item in list:
        user = fetch_users_service(req.token, str(item["assigned_id"]))
        user_name = (f"{user['names']} {user['paternal_surname']} {user['maternal_surname']}")
        

        dataList.append({**item, "assigned": user_name,
                        "date": item["date"].strftime('%d-%m-%Y'),
                         "end_date": item["end_date"].strftime('%H:%M:%S'),
                         "start_date": item["start_date"].strftime('%H:%M:%S'),
                         "shift_name": item["shift_name"].capitalize(),
                         "status": item["status"].capitalize(),
                         "business_name": validateValue(item["business_name"]),
                         "construction_name": validateValue(item["construction_name"])
                         })

    headings = [{"name": "Fecha", "width": 10},
                {"name": "Hora de inicio", "width": 20},
                {"name": "Hora de fin", "width": 20},
                {"name": "Estado", "width": 15},
                {"name": "Jornada", "width": 15},
                {"name": "Título", "width": 50},
                {"name": "Profesional", "width": 20},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Observaciones", "width": 100}]

    attrs = ["date", 
            "start_date", 
            "end_date", 
            "status",
            "shift_name",
            "title", 
            "assigned",
            "business_name", 
            "construction_name",
            "observation"]

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    })

    if(start_ == None and end_ == None):
        worksheet.write(1, 0, f"Todos los Registros de Visitas de la Empresa: {company_name}")

    elif(start_ and end_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas de la Empresa: {company_name} desde {start_.strftime('%d-%m-%Y')} al {end_.strftime('%d-%m-%Y')}")

    elif (end_ == None and start_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas de la Empresa: {company_name} desde {start_.strftime('%d-%m-%Y')} hasta hoy")

    elif (start_ == None and end_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas de la Empresa: {company_name} hasta {end_.strftime('%d-%m-%Y')}")
        
    

    heading_index = 0
    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    row = 4

    for item in dataList:
        col = 0
        for attr in attrs:
            worksheet.write(
                row, col, item[attr], cell)
            col += 1

        row += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output

def generate_visits_by_assigned_excel(req: Request, list: List[dict], start_: datetime, end_: datetime):

    dataList = []
    for item in list:
        user = fetch_users_service(req.token, str(item["assigned_id"]))
        user_name = (f"{user['names']} {user['paternal_surname']} {user['maternal_surname']}")

        dataList.append({**item, "assigned": user_name,
                        "date": item["date"].strftime('%d-%m-%Y'),
                         "end_date": item["end_date"].strftime('%H:%M:%S'),
                         "start_date": item["start_date"].strftime('%H:%M:%S'),
                         "shift_name": item["shift_name"].capitalize(),
                         "status": item["status"].capitalize(),
                         "business_name": validateValue(item["business_name"]),
                         "construction_name": validateValue(item["construction_name"])
                         })

    headings = [{"name": "Fecha", "width": 10},
                {"name": "Hora de inicio", "width": 20},
                {"name": "Hora de fin", "width": 20},
                {"name": "Estado", "width": 15},
                {"name": "Jornada", "width": 15},
                {"name": "Título", "width": 50},
                {"name": "Profesional", "width": 20},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Observaciones", "width": 100}]

    attrs = ["date", 
            "start_date", 
            "end_date", 
            "status",
            "shift_name",
            "title", 
            "assigned",
            "business_name", 
            "construction_name",
            "observation"]

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    })

    if(start_ == None and end_ == None):
        worksheet.write(1, 0, f"Todos los Registros de Visitas del Profesional: {user_name}")

    elif(start_ and end_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas del Profesional: {user_name} desde {start_.strftime('%d-%m-%Y')} al {end_.strftime('%d-%m-%Y')}")

    elif (end_ == None and start_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas del Profesional: {user_name} desde {start_.strftime('%d-%m-%Y')} hasta hoy")

    elif (start_ == None and end_):
        worksheet.write(1, 0, f"Todos los Registros de Visitas del Profesional: {user_name} hasta {end_.strftime('%d-%m-%Y')}")

    heading_index = 0
    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    row = 4

    for item in dataList:
        col = 0
        for attr in attrs:
            worksheet.write(
                row, col, item[attr], cell)
            col += 1

        row += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output

def generate_assistance_by_employee_excel(req: Request, list: List[dict], rut_employee: str, start_: datetime, end_: datetime):
    dataList = []
    for item in list:

        managment = get_managment_data(req.token, str(item["management_id"]))
        user = fetch_users_service(req.token, str(item["assigned_id"]))
        user_name = (f"{user['names']} {user['paternal_surname']} {user['maternal_surname']}")
        
        dataList.append({
            "id": item["id"],
            "status": item["status"],
            "managment_type": managment["name"],
            "contact_method": item["contact_method"],
            "date": item["date"].strftime('%d-%m-%Y'),
            "update_at": item["update_at"].strftime('%d-%m-%Y'),
            "employee_rut": item["employee_rut"],
            "employee_name": item["employee_name"],
            "business_name": item["business_name"],
            "construction_name": item["construction_name"],
            "source_business": item["source_business"],
            "attention_place": item["attention_place"],
            "assigned": user_name,
            "area_name": item["area_name"],
            "attended_name": item["attended_name"],
            "source_system": item["source_system"],
            "observation": item["observation"],
            "company_report_observation": item["company_report_observation"],
            "case_id": item["case_id"]
        })

    headings = [{"name": "Id", "width": 10},
                {"name": "Estado", "width": 20},
                {"name": "Tipo de Gestion", "width": 20},
                {"name": "Tipo de intervención", "width": 25},
                {"name": "Fecha de derivación", "width": 25},
                {"name": "Ultima Actualización", "width": 27},
                {"name": "R.U.T", "width": 50},
                {"name": "Nombre Trabajador", "width": 27},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Fuente de Empresa", "width": 40},
                {"name": "Oficina", "width": 40},
                {"name": "Profesional", "width": 40},
                {"name": "Area", "width": 40},
                {"name": "Persona Atendido", "width": 40},
                {"name": "Sistema de Origen", "width": 40},
                {"name": "Observaciones", "width": 100},
                {"name": "Observaciones Empresa", "width": 100},
                {"name": "Nro Caso", "width": 10}]

    attrs = ["id", 
            "status",
            "managment_type",
            "contact_method", 
            "date",
            "update_at",
            "employee_rut", 
            "employee_name",
            "business_name", 
            "construction_name",
            "source_business",
            "attention_place",
            "assigned",
            "area_name",
            "attended_name",
            "source_system",
            "observation",
            "company_report_observation",
            "case_id"]

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    })

    if(start_ == None and end_ == None):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias del Trabajador con el rut: {rut_employee}")

    elif(start_ and end_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias del Trabajador con el rut: {rut_employee} desde {start_.strftime('%d-%m-%Y')} al {end_.strftime('%d-%m-%Y')}")

    elif (end_ == None and start_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias del Trabajador con el rut: {rut_employee} desde {start_.strftime('%d-%m-%Y')} hasta hoy")

    elif (start_ == None and end_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias del Trabajador con el rut: {rut_employee} hasta {end_.strftime('%d-%m-%Y')}")

    heading_index = 0
    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    row = 4

    for item in dataList:
        col = 0
        for attr in attrs:
            worksheet.write(
                row, col, item[attr], cell)
            col += 1

        row += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output

def generate_assistance_by_company_excel(req: Request, list: List[dict], company_name: str, start_: datetime, end_: datetime):
    dataList = []
    for item in list:

        managment = get_managment_data(req.token, str(item["management_id"]))
        user = fetch_users_service(req.token, str(item["assigned_id"]))
        user_name = (f"{user['names']} {user['paternal_surname']} {user['maternal_surname']}")
        dataList.append({
            "id": item["id"],
            "status": item["status"],
            "managment_type": managment["name"],
            "contact_method": item["contact_method"],
            "date": item["date"].strftime('%d-%m-%Y'),
            "update_at": item["update_at"].strftime('%d-%m-%Y'),
            "employee_rut": item["employee_rut"],
            "employee_name": item["employee_name"],
            "business_name": item["business_name"],
            "construction_name": item["construction_name"],
            "source_business": item["source_business"],
            "attention_place": item["attention_place"],
            "assigned": user_name,
            "area_name": item["area_name"],
            "attended_name": item["attended_name"],
            "source_system": item["source_system"],
            "observation": item["observation"],
            "company_report_observation": item["company_report_observation"],
            "case_id": item["case_id"]
        })

    headings = [{"name": "Id", "width": 10},
                {"name": "Estado", "width": 20},
                {"name": "Tipo de Gestion", "width": 20},
                {"name": "Tipo de intervención", "width": 25},
                {"name": "Fecha de derivación", "width": 25},
                {"name": "Ultima Actualización", "width": 27},
                {"name": "R.U.T", "width": 50},
                {"name": "Nombre Trabajador", "width": 27},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Fuente de Empresa", "width": 40},
                {"name": "Oficina", "width": 40},
                {"name": "Profesional", "width": 40},
                {"name": "Area", "width": 40},
                {"name": "Persona Atendido", "width": 40},
                {"name": "Sistema de Origen", "width": 40},
                {"name": "Observaciones", "width": 100},
                {"name": "Observaciones Empresa", "width": 100},
                {"name": "Nro Caso", "width": 10}]

    attrs = ["id", 
            "status",
            "managment_type",
            "contact_method", 
            "date",
            "update_at",
            "employee_rut", 
            "employee_name",
            "business_name", 
            "construction_name",
            "source_business",
            "attention_place",
            "assigned",
            "area_name",
            "attended_name",
            "source_system",
            "observation",
            "company_report_observation",
            "case_id"]

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})
    cell = workbook.add_format({
        'color': 'black',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    })

    if(start_ == None and end_ == None):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias de la Empresa: {company_name}")

    elif(start_ and end_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias de la Empresa: {company_name} desde {start_.strftime('%d-%m-%Y')} al {end_.strftime('%d-%m-%Y')}")

    elif (end_ == None and start_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias de la Empresa: {company_name} desde {start_.strftime('%d-%m-%Y')} hasta hoy")

    elif (start_ == None and end_):
        worksheet.write(1, 0, f"Todos los Registros de Asistencias de la Empresa: {company_name} hasta {end_.strftime('%d-%m-%Y')}")

    heading_index = 0
    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    row = 4

    for item in dataList:
        col = 0
        for attr in attrs:
            worksheet.write(
                row, col, item[attr], cell)
            col += 1

        row += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output


# def generate_report_and_upload(db: Session, visit_id: int, body: VisitReportSchema, token: str):
#     visit = db.query(Visit).filter(Visit.id == visit_id).first()
#     total_formatted = ""
#     total_assistance = len(db.query(Assistance).filter(
#         Assistance.visit_id == visit_id).all())
#     if(total_assistance > 0):
#         total_formatted = str(total_assistance) + \
#             " personas" if total_assistance > 1 else "1 persona"
#     else:
#         total_formatted = "No se atienderon personas"

#     table_data = []
#     table_data.append(
#         {"display": "Trabjadores atendidos", "data": total_formatted})
#     for item in body.items:
#         table_data.append(
#             {"display": item.item_name, "data": str(item.value)})

#     table_data.append({"display": "Casos relevantes", "data": body.relevant})
#     table_data.append(
#         {"display": "Observaciones de la visita", "data": body.observations})

#     data = {"construction_name": visit.construction_name,
#             "user": body.user_name,
#             "date": body.date,
#             "correlative": str(visit.id),
#             "user_email": body.user_email,
#             "user_phone": body.user_phone,
#             "relevant": body.relevant,
#             "observations": body.observations,
#             "total": str(total_assistance),
#             "table_data": table_data
#             }
#     report_upload = create_visit_report(token, data)

#     return report_upload


# def generate_visit_report(db: Session, visit_id: int, body: VisitReportSchema, req: Request) -> None:

#     report = generate_report_and_upload(db, visit_id, body, req.token)

#     obj_report = jsonable_encoder(body)
#     del obj_report["contacts"]
#     del obj_report["date"]
#     del obj_report["items"]
#     obj_report["created_by"] = req.user_id
#     obj_report["is_active"] = True
#     obj_report["visit_id"] = visit_id
#     obj_report["report_key"] = report["file_key"]
#     obj_report["report_url"] = report["file_url"]
#     obj_report["create_date"] = datetime.now()
#     db_report = VisitReport(**obj_report)
#     db.add(db_report)
#     db.commit()
#     db.flush(db_report)

#     if body.contacts:
#         create_report_contacts(db, body.contacts, db_report.id, req.user_id)
#     if len(body.items) > 0:
#         create_report_items(db, body.items, db_report.id, req.user_id)


# def generate_to_attend_employees_excel(visit_id: int):

#     output = BytesIO()

#     workbook = xlsxwriter.Workbook(output)
#     worksheet = workbook.add_worksheet()

#     cell_format = workbook.add_format()
#     cell_format.set_text_wrap()

#     headings = [{"name": "Run", "width": 15},
#                 {"name": "Nombres", "width": 25},
#                 {"name": "Apellidos", "width": 25},
#                 {"name": "Nacionalidad", "width": 10},
#                 {"name": "Sexo", "width": 8},
#                 {"name": "Cargo de obra", "width": 20},
#                 ]

#     header_style = {
#         'bg_color': '#AED5FF',
#         'color': 'black',
#         'align': 'center',
#         'valign': 'top',
#         'border': 1,
#         'text_wrap': True
#     }

#     center_header = workbook.add_format({**header_style, "align": "center"})

#     heading_index = 0
#     worksheet.write(
#         1, heading_index, "Trabajadores por atender: Visita " + str(visit_id))

#     for head in headings:
#         worksheet.set_column(3, heading_index, head["width"])
#         worksheet.write(
#             3, heading_index, head["name"], center_header)
#         heading_index += 1

#     worksheet.hide_gridlines(2)

#     workbook.close()
#     output.seek(0)

#     return output


# def get_owner_status(role: str, assigned_id: int, user_id: int):
#     if role != "SOCIAL_ASSISTANCE":
#         return True
#     return assigned_id == user_id
