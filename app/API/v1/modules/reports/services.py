
from fastapi.encoders import jsonable_encoder
import xlsxwriter
from fastapi import Request
from typing import List
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm.session import Session
from app.settings import SERVICES
from ...helpers.fetch_data import fetch_parameter_data, fetch_users_service, fetch_service
from ...services.file import create_visit_report
from ..assistance.model import Assistance


def generate_visits_excel(req: Request,
                          list: List[dict],
                          start_date: datetime,
                          end_date: datetime) -> None:

    dataList = []
    for item in list:
        user = "EXAMPLE"
        shift_details = fetch_parameter_data(
            req.token, "shift", item["shift_id"])
        dataList.append({**item, "assigned": user,
                        "date": item["date"].strftime('%d-%m-%Y'),
                         "end_date": item["end_date"].strftime('%H:%M:%S'),
                         "start_date": item["start_date"].strftime('%H:%M:%S'),
                         "shift_name": shift_details["name"].capitalize(),
                         "status": item["status"].capitalize()})

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

    attrs = ["date", "start_date", "end_date", "shift_name", "status", "title",
             "business_name", "construction_name", "assigned"]

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
    header = workbook.add_format({**header_style})

    worksheet.write(1, 0, "Visitas del " +
                    start_date.strftime('%d-%m-%Y') + " al " + end_date.strftime('%d-%m-%Y'))

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