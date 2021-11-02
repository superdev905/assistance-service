
import xlsxwriter
from fastapi import Request
from typing import List
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from sqlalchemy.orm.session import Session
from ...helpers.fetch_data import fetch_parameter_data, fetch_users_service
from .model import Visit


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
    current_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    end_date = datetime.strftime(
        visit.end_date + timedelta(hours=48), '%Y-%m-%d')

    return current_date >= end_date


def block_visit(db: Session, visit: Visit) -> None:
    if get_blocked_status(visit) and visit.is_active:
        visit.is_active = False
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
