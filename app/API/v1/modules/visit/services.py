
from fastapi.encoders import jsonable_encoder
import xlsxwriter
from fastapi import Request
from typing import List
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm.session import Session
from ...helpers.fetch_data import fetch_parameter_data, fetch_users_service
from ...services.file import create_visit_report
from ..assistance.model import Assistance
from .schema import VisitReportSchema
from .model import ReportItem, Visit, ReportTarget, VisitReport


def format_business_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "business_name": details["business_name"],
            "rut": details["rut"],
            }


def format_construction_details(details: dict) -> dict:
    if not details:
        return None

    return {"address": details["address"],
            "latitude": details["latitude"],
            "longitude": details["longitude"],
            "name": details["name"],
            }


def get_blocked_status(visit: Visit) -> bool:
    current_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

    end_date = datetime.strftime(
        visit.end_date.replace(hour=23, minute=59, second=59, microsecond=999), '%Y-%m-%d %H:%M:%S')
    return current_date >= end_date


def close_visit(db: Session, visit: Visit) -> None:
    if get_blocked_status(visit):
        if not visit.is_close:
            visit.is_close = True
            db.add(visit)
            db.commit()
            db.flush(visit)


def get_assigned_user(req: Request, id: int) -> str:
    user_details = fetch_users_service(req.token, id)

    return user_details["names"] + " "+user_details["paternalSurname"]


def generate_visits_excel(req: Request, list: List[dict], start_date: datetime, end_date: datetime) -> None:

    dataList = []
    for item in list:
        user = get_assigned_user(req, item["assigned_id"])
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
                {"name": "Jornada", "width": 15},
                {"name": "Estado", "width": 15},
                {"name": "Título", "width": 50},
                {"name": "Empresa", "width": 40},
                {"name": "Obra", "width": 40},
                {"name": "Responsable", "width": 20}]

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


def create_report_contacts(db: Session, contacts: List, visit_report_id: int, user_id: int) -> None:
    for item in contacts:
        new_contact = jsonable_encoder(item)
        new_contact["created_by"] = user_id
        new_contact["visit_report_id"] = visit_report_id
        db_contact = ReportTarget(**new_contact)
        db.add(db_contact)
        db.commit()
        db.flush(db_contact)


def create_report_items(db: Session, items: List, report_id: int, user_id: int):
    for item in items:
        obj_item = jsonable_encoder(item)
        obj_item["report_id"] = report_id
        obj_item["created_by"] = user_id
        del obj_item["item_name"]

        db_item = ReportItem(**obj_item)

        db.add(db_item)
        db.commit()
        db.refresh(db_item)


def generate_report_and_upload(db: Session, visit_id: int, body: VisitReportSchema, token: str):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    total_formatted = ""
    total_assistance = len(db.query(Assistance).filter(
        Assistance.visit_id == visit_id).all())
    if(total_assistance > 0):
        total_formatted = str(total_assistance) + \
            " personas" if total_assistance > 1 else "persona"
    else:
        total_formatted = "No se atienderon personas"

    table_data = []
    table_data.append(
        {"display": "Trabjadores atendidos", "data": total_formatted})
    for item in body.items:
        table_data.append(
            {"display": item.item_name, "data": str(item.value)})

    table_data.append({"display": "Casos relevantes", "data": body.relevant})
    table_data.append(
        {"display": "Observaciones de la visita", "data": body.observations})

    data = {"construction_name": visit.construction_name,
            "user": body.user_name,
            "date": body.date,
            "correlative": str(visit.id),
            "user_email": body.user_email,
            "user_phone": body.user_phone,
            "relevant": body.relevant,
            "observations": body.observations,
            "total": str(total_assistance),
            "table_data": table_data
            }
    report_upload = create_visit_report(token, data)

    return report_upload


def generate_visit_report(db: Session, visit_id: int, body: VisitReportSchema, req: Request) -> None:

    report = generate_report_and_upload(db, visit_id, body, req.token)

    obj_report = jsonable_encoder(body)
    del obj_report["contacts"]
    del obj_report["date"]
    del obj_report["items"]
    obj_report["created_by"] = req.user_id
    obj_report["is_active"] = True
    obj_report["visit_id"] = visit_id
    obj_report["report_key"] = report["file_key"]
    obj_report["report_url"] = report["file_url"]
    obj_report["create_date"] = datetime.now()
    db_report = VisitReport(**obj_report)
    db.add(db_report)
    db.commit()
    db.flush(db_report)

    if body.contacts:
        create_report_contacts(db, body.contacts, db_report.id, req.user_id)
    if len(body.items) > 0:
        create_report_items(db, body.items, db_report.id, req.user_id)


def generate_to_attend_employees_excel(visit_id: int):

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    headings = [{"name": "Run", "width": 15},
                {"name": "Nombres", "width": 25},
                {"name": "Apellidos", "width": 25},
                {"name": "Nacionalidad", "width": 10},
                {"name": "Sexo", "width": 8},
                {"name": "Cargo de obra", "width": 20},
                ]

    header_style = {
        'bg_color': '#AED5FF',
        'color': 'black',
        'align': 'center',
        'valign': 'top',
        'border': 1,
        'text_wrap': True
    }

    center_header = workbook.add_format({**header_style, "align": "center"})

    heading_index = 0
    worksheet.write(
        1, heading_index, "Trabajadores por atender: Visita " + str(visit_id))

    for head in headings:
        worksheet.set_column(3, heading_index, head["width"])
        worksheet.write(
            3, heading_index, head["name"], center_header)
        heading_index += 1

    worksheet.hide_gridlines(2)

    workbook.close()
    output.seek(0)

    return output
