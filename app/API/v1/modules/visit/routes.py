from array import array
from datetime import date, datetime
from typing import List, Optional
from fastapi import status, APIRouter, Request, Query
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm.session import Session
from fastapi.param_functions import Depends
from starlette.responses import StreamingResponse
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import func
from fastapi_pagination import PaginationParams
from fastapi_pagination.ext.sqlalchemy import paginate
from app.database.main import get_database
from app.settings import SERVICES
from ...middlewares.auth import JWTBearer
from ...helpers.fetch_data import fetch_users_service, get_business_data, fetch_parameter_data, get_employee_data, get_employee_current_job
from ..assistance.model import Assistance
from ..assistance_construction.model import AssistanceConstruction
from ..report_item.model import VisitReportItem
from .model import Visit, VisitReport, VisitRevision, StatisticsView
from .schema import VisitCalendarItem, VisitCloseSchema, VisitCreate, VisitPatchSchema, VisitReportSchema, VisitWorkers, VisitsExport
from .services import close_visit, format_business_details, format_construction_details, generate_to_attend_employees_excel, generate_visit_report, get_blocked_status, generate_visits_excel, get_owner_status
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib

router = APIRouter(
    prefix="/visits", tags=["Visitas"], dependencies=[Depends(JWTBearer())])


@router.get("/calendar/stats")
def get_calendar_stats(req: Request,
                       users: List[int] = Query(None),
                       start_date: Optional[datetime] = Query(
                           None, alias="startDate"),
                       end_date: Optional[datetime] = Query(
                           None, alias="endDate"),
                       db: Session = Depends(get_database)):
    filters = []
    users_filters = []
    users_ids = []
    if start_date and end_date:
        filters.append(Visit.start_date >= start_date)
        filters.append(Visit.end_date <= end_date)
    if users:
        for i in users:
            users.append(i)
    users_ids.append(req.user_id)

    users_filters.append(Visit.assigned_id.in_(users_ids))

    result = []
    docs = db.query(func.count(Visit.id).label("value"),
                    Visit.status.label("status")).filter(and_(*filters, *users_filters)).group_by(Visit.status).all()

    total = db.query(func.count(Visit.id)).filter(
        and_(*filters, *users_filters)).all()

    result.append({"label": "Total", "value": total})

    for doc in docs:
        result.append({"label": doc.status, "value": doc.value})

    db.close()
    return result


@router.get("/calendar", response_model=List[VisitCalendarItem])
def get_calendar_events(req: Request,
                        users: List[int] = Query(None),

                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        status: Optional[str] = None,
                        db: Session = Depends(get_database)):
    """
    Optiene las asistencias y visitas para mostrar en el calendario

    - **start_date**: Fecha de inicio
    - **end_date**: Fecha de fin
    - **user_id**: Id de usuario responsable
    """
    user_id = req.user_id
    current_user = fetch_users_service(req.token, req.user_id)
    user_role = current_user["role"]["key"]

    filters = []
    users_filters = []
    users_ids = []

    if start_date and end_date:
        filters.append(Visit.start_date >= start_date)
        filters.append(Visit.end_date <= end_date)
    if status:
        filters.append(Visit.status == status)
    if users:
        for i in users:
            users_ids.append(i)
    users_ids.append(user_id)
    users_filters.append(Visit.assigned_id.in_(users_ids))

    items = []
    events = db.query(Visit).filter(
        and_(or_(*filters), *users_filters)).order_by(Visit.date).all()

    for visit in events:
        items.append(
            {**visit.__dict__,
             "is_owner": get_owner_status(user_role, visit.assigned_id, req.user_id),
             "assigned": fetch_users_service(req.token, visit.assigned_id)
             })

    db.close()
    return items


@router.get("")
def get_all(req: Request,
            user_id: Optional[int] = None,
            start_date: Optional[datetime] = None,
            search: Optional[str] = None,
            db: Session = Depends(get_database),
            params: PaginationParams = Depends()):
    """
    Retorna la lista de visitas
    ---
    Parametros:
    - **size**: P??gina de asistencias
    - **limit**: N??mero de registros por cada p??gina asistencias
    - **user_id**: Id de usuario responsable
    - **start_date**: Fecha inicial para filtrar visitas
    - **search**: Par??metro a buscar 
    """
    filters = []
    search_filters = []
    current_user = fetch_users_service(req.token, req.user_id)
    user_role = current_user["role"]["key"]
    if user_id and user_role == "SOCIAL_ASSISTANCE":
        filters.append(Visit.assigned_id == user_id)
    if start_date:
        filters.append(func.DATE(Visit.start_date) >= start_date)
    if search:
        formatted_search = '%{}%'.format(search)
        search_filters.append(Visit.title.ilike(formatted_search))
        search_filters.append(Visit.business_name.ilike(formatted_search))
        search_filters.append(
            Visit.construction_name.ilike(formatted_search))
    visits_list = paginate(db.query(Visit).filter(and_(
        *filters, or_(*search_filters), Visit.status != "CANCELADA", Visit.type_id == 1)).order_by(Visit.start_date), params)
    
    db.close()
    return visits_list

@router.get("/report-visits/{companyId}")
def get_all_visits(companyId: int,
                   start_date: datetime,
                   end_date: datetime,
                   db: Session = Depends(get_database)):
    """
    Retorna la lista de visitas para generar reporte mensual
    ---
    Parametros:
    - **companyId**: ID de la compa????a a la que se genera el reporte
    - **start_date**: Fecha inicial para b??squeda
    - **end_date**: Fecha final para b??squeda
    """
    visit_list = db.query(Visit).filter(and_(Visit.business_id == companyId, func.DATE(Visit.start_date) >= start_date, func.DATE(Visit.end_date) <= end_date)).all()
    result = jsonable_encoder(visit_list)
    return result


@router.get("/request-close")
def get_all(search: Optional[str] = None,
            db: Session = Depends(get_database),
            params: PaginationParams = Depends(),
            user_id: Optional[int] = None,
            role: Optional[str] = None):
    """
    Retorna la lista de visitas por cerrar
    ---
    Parametros:
    - **size**: P??gina de asistencias
    - **limit**: N??mero de registros por cada p??gina asistencias
    """
    search_filters = []
    if search:
        formatted_search = '%{}%'.format(search)
        search_filters.append(Visit.title.ilike(formatted_search))
        search_filters.append(Visit.business_name.ilike(formatted_search))
        search_filters.append(
            Visit.construction_name.ilike(formatted_search))
    if role == 'ADMIN':
        visits_list = paginate(db.query(Visit).filter(
            and_(
                or_(*search_filters),
                Visit.is_close_pending == True,
                Visit.status != "CANCELADA")
        ).order_by(Visit.start_date), params)
    else :
        visits_list = paginate(db.query(Visit).filter(
            and_(
                or_(*search_filters),
                Visit.assigned_id == user_id,
                Visit.is_close_pending == True,
                Visit.status != "CANCELADA")
        ).order_by(Visit.start_date), params)

    db.close()
    return visits_list


@router.get("/{id}")
def get_one(req: Request, id: int, db: Session = Depends(get_database)):
    """
    Optiene una visita
    ---
    - **id**: id de asistencia/visita
    """

    print("Inicio API de obtener una visita en id ", id)

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    print("Inicio de Solicitud =", current_time)
    
    visit = db.query(Visit).filter(Visit.id == id).first()

    print("Visita solicitada =", visit, " Hora =", current_time)

    if not visit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No existe una visita con este" + str(id))

    shift = fetch_parameter_data(req.token, "shift",  visit.shift_id)
    print("Shift parameter =", shift, " Hora =", current_time)
    bussiness = get_business_data(req.token,
                                  "business", visit.business_id)if visit.business_id else None
    print("Bussiness Parameter =", bussiness, " Hora =", current_time)
    construction = get_business_data(req.token,
                                     "constructions", visit.construction_id) if visit.construction_id else None
    print("Construction parameter =", construction, " Hora =", current_time)
    report = db.query(VisitReport).filter(
        and_(VisitReport.visit_id == id, VisitReport.is_active == True)).order_by(VisitReport.created_at.desc()).first()
    
    print("Report parameter =", report, " Hora =", current_time)

    assigned_user = fetch_users_service(req.token, visit.assigned_id)

    print("Assigned User parameter =", assigned_user, " Hora =", current_time)

    assigned_user = {
        "id": assigned_user["id"],
        "names": assigned_user["names"],
        "paternal_surname": assigned_user["paternal_surname"],
        "maternal_surname": assigned_user["maternal_surname"]}
    
    print("Assigned User JSON parameter")
    print(assigned_user["id"])
    print(assigned_user["maternal_surname"])
    print(assigned_user["names"])
    print(assigned_user["paternal_surname"])

    print("Hora =", current_time)

    db.close()
    return {**visit.__dict__,
            "shift": shift,
            "bussiness": format_business_details(bussiness),
            "construction": format_construction_details(construction),
            "report": report,
            "assigned": assigned_user}


@router.get("/{id}/report-items")
def get_one_statistics(id: int, db: Session = Depends(get_database)):
    """
    Obtiene los items para reporte de visita 
    - **id**: visit_id de la asistencia

    """
    result = []
    items = db.query(VisitReportItem).filter(
        VisitReportItem.is_active == True).all()
    for i in items:
        total = 0
        docs = db.query(AssistanceConstruction).filter(and_(
            AssistanceConstruction.type_name.ilike("%{}%".format(i.name)), AssistanceConstruction.visit_id == id)).all()

        for doc in docs:
            total += doc.quantity

        result.append({**i.__dict__, "value": total})

    db.close()
    return result


@router.get("/{id}/statistics")
def get_one_statistics(req: Request,
                       id: int,
                       db: Session = Depends(get_database)):
    """
    Obtiene las estadisticas de una visita

    - **id**: visit_id de la asistencia

    """

    """
    total = len(db.query(Assistance.employee_id.label('employee_id')).filter(Assistance.visit_id == id).group_by(Assistance.employee_id).all())
    total_house = 0
    total_sub_contract = 0
    old = 0
    new = 0
    docs = db.query(Assistance.employee_id.label('employee_id')).filter(Assistance.visit_id == id).group_by(Assistance.employee_id).all()
    ids = []

    for i in docs:
        ids.append(i.employee_id)
    
    employee = get_employee_current_job(req, ids)

    for job in employee["current_job"]:
        if job["contract_type"] == "SUB CONTRATO":
            total_sub_contract += 1
        if job["contract_type"] == "EMPRESA":
            total_house += 1

    """

    #db.close()
    #return db.query(StatisticsView).filter(StatisticsView.visit_id == id).all()


@router.post("/{id}/workers")
def set_workers(id: int, body: VisitWorkers, db: Session = Depends(get_database)):
    """
    Actualiza la cantidad de trabajadores en visita

    - **id**: visit_id de la visita

    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")
    visit.company_workers = body.company_workers
    visit.outsourced_workers = body.outsourced_workers

    db.add(visit)
    db.commit()
    db.refresh(visit)

    db.close()
    return visit


@router.post("/{id}/attended-employees/export")
def create_report(id: int,  db: Session = Depends(get_database)):
    """
    Exporta los trabajadores por atender
    ---
    - **id**: id de asistencia/visita
    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")

    file_name = "Trabajadores-por-atender"
    headers = {
        'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
    }
    buffer_export = generate_to_attend_employees_excel(visit.id)

    db.close()
    return StreamingResponse(buffer_export, headers=headers)


@router.post("/{id}/report")
def create_report(req: Request, id: int, report_in: VisitReportSchema, db: Session = Depends(get_database)):
    """
    Crea el reporte de la visita
    ---
    - **id**: id de asistencia/visita
    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")
    
    print('||--- Iniciando Petici??n de Reporte ---||')

    generate_visit_report(db, id, report_in, req)

    db.close()
    return {"message": "Reporte creado"}


@router.put("/{id}/report")
def update_report(req: Request, id: int, report_in: VisitReportSchema, db: Session = Depends(get_database)):
    """
    Actualiza el reporte de la visita, deshabilita la version anterior y crea una nueva
    ---
    - **id**: id de asistencia/visita
    """
    visit = db.query(Visit).filter(Visit.id == id).first()

    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")
    if visit.status == "TERMINADA":
        raise HTTPException(
            status_code=400, detail="No se puede editar el reporte de esta visita completada")

    previous_reports = db.query(VisitReport).filter(
        VisitReport.visit_id == id).all()

    # if len(previous_reports) == 0:
    #     raise HTTPException(
    #         status_code=400, detail="Esta visita no tiene un reporte creado")

    for report in previous_reports:
        if report.is_active:
            report.is_active = False
            db.add(report)
            db.commit()
            db.flush(report)

    generate_visit_report(db, id, report_in, req)

    db.close()
    return {"message": "Reporte actualizado"}


@ router.post("")
def create_one(obj_in: VisitCreate, db: Session = Depends(get_database)):
    """
    Crea una nueva asistencia

    """
    visit_obj = jsonable_encoder(obj_in)
    visit_obj["is_close"] = False
    saved_event = Visit(**visit_obj)

    db.add(saved_event)
    db.commit()
    db.refresh(saved_event)
    db.close()
    return saved_event


@router.post("/export")
def export_visits(req: Request, body: VisitsExport, db: Session = Depends(get_database)):
    """
    Exporta las visitas a un archivo excel

    """
    file_name = "Visitas"
    headers = {
        'Content-Disposition': "attachment; filename=" + file_name + ".xlsx"
    }

    filters = []

    filters.append(Visit.start_date >= body.start_date)
    filters.append(Visit.end_date <= Visit.end_date)
    filters.append(Visit.assigned_id <= req.user_id)

    result = db.query(Visit).filter(
        *filters).order_by(Visit.start_date.desc()).all()
    formatted_visits = []
    for visit in result:
        formatted_visits.append(visit.__dict__)

    buffer_export = generate_visits_excel(
        req, formatted_visits, body.start_date, body.end_date)

    db.close()
    return StreamingResponse(buffer_export, headers=headers)


@router.put("/{id}")
def update_one(id: int, update_body: VisitCreate, db: Session = Depends(get_database)):
    """
    Actualiza un evento
    - **id**: id del evento

    """
    found_event = db.query(Visit).filter(
        Visit.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")
    if get_blocked_status(found_event):
        raise HTTPException(
            status_code=400, detail="No se puede editar esta visita")
    obj_data = jsonable_encoder(found_event)

    if isinstance(update_body, dict):
        update_data = update_body
    else:
        update_data = update_body.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(found_event, field, update_data[field])

    db.add(found_event)
    db.commit()
    db.refresh(found_event)
    db.close()
    return found_event


@ router.patch("/{id}")
def patch_one(id: int, patch_body: VisitPatchSchema, db: Session = Depends(get_database)):
    """
    Actualiza campos de un evento
    - **id**: id del evento

    """
    found_event = db.query(Visit).filter(
        Visit.id == id).first()
    if not found_event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

    obj_data = jsonable_encoder(found_event)

    if isinstance(patch_body, dict):
        update_data = patch_body
    else:
        update_data = patch_body.dict(exclude_unset=True)
    for field in obj_data:
        if field in update_data:
            setattr(found_event, field, update_data[field])

    db.add(found_event)
    db.commit()
    db.refresh(found_event)
    db.close()
    return found_event


@ router.delete("/{id}")
def delete_one(id: int,  db: Session = Depends(get_database)):
    """
    Elimina un evento

    - **id**: id del evento

    """
    event = db.query(Visit).filter(
        Visit.id == id).first()
    if not event:
        raise HTTPException(
            status_code=400, detail="Este evento no existe")

    db.delete(event)
    db.commit()
    db.close()
    return {"message": "Evento eliminado"}


@router.post("/{id}/request-close")
def request_close_visit(id: int, db: Session = Depends(get_database)):
    """
    Solicita cierre de una visita

    - **id**: id de la visita
    """
    visit = db.query(Visit).filter(
        Visit.id == id).first()
    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")

    if visit.is_close:
        raise HTTPException(
            status_code=400, detail="Esta visita ya fue cerrada")

    if visit.is_close_pending:
        raise HTTPException(
            status_code=400, detail="El cierre de esta visita ya fue solicitada")

    visit.is_close_pending = True
    visit.status = "TERMINADA"

    db.add(visit)
    db.commit()
    db.flush(visit)
    db.close()
    return {"message": "Cierre solicitado"}


@router.post("/{id}/close")
def close_one_visit(req: Request, id: int, body: VisitCloseSchema,  db: Session = Depends(get_database)):
    """
    Bloquea una visita

    - **id**: id de la visita

    """
    visit = db.query(Visit).filter(
        Visit.id == id).first()
    if not visit:
        raise HTTPException(
            status_code=400, detail="Esta visita no existe")

    if visit.is_close:
        raise HTTPException(
            status_code=400, detail="Esta visita ya fue cerrada")

    close_revision = jsonable_encoder(body)
    close_revision["created_by"] = req.user_id
    close_revision["type"] = "CLOSE"

    saved_revision = VisitRevision(**close_revision)

    db.add(saved_revision)
    db.commit()
    db.refresh(saved_revision)

    visit.status = "CERRADA"
    visit.is_close = True
    visit.is_close_pending = False
    visit.close_revision_id = saved_revision.id

    db.add(visit)
    db.commit()
    db.flush(visit)
    db.close()
    return {"message": "Visita cerrada"}

@router.post("/mail")
def send_report_mail(to: list, url: str, visit_id: int, business_name: str, construction_name: str, date: date, assistant_name: str, bccBoss: list):
    # create message object instance
    msg = MIMEMultipart('alternative')
    # setup the parameters of the message
    password = "u8m7&KNJ4"
    msg['From'] = "fundacionsocialcchc@fundacioncchc.cl"
    msg['To'] = ','.join(to)
    if(bccBoss and len(bccBoss) > 0):
        msg['Cc'] = ','.join(bccBoss)
    msg['Subject'] = f"Env??o cierre visita {visit_id}"
    html = f"""
    <html>
        <head></head>
        <body>
            <p>Estimado(a).</p>
            <p>La fundaci??n Social de la CChC informa a UD. que se ha finalizado exitosamente la visita de Servicio Social para la empresa <b>{business_name}</b> obra <b>{construction_name}</b> del d??a <b>{date.strftime('%d-%m-%Y')}</b>. Podr?? descargar el reporte de la visita con la informaci??n relevante en el siguiente link:<br/><br/>

            <p><a href={url}>Descargar Informe</a></p><br/>

            <div>Saludos cordiales,</div>
            <div>{assistant_name}</div>
            <div>Fundaci??n Social CChC</div>
        </body>
    </html>
    """
    part2 = MIMEText(html, 'html')
    msg.attach(part2)

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], to, msg.as_string())

    server.quit()
    
    print("successfully sent email to: ", msg['To'], msg["Cc"])
