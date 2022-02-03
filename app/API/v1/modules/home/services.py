from fastapi import Request
from app.settings import SERVICES
from ...helpers.fetch_data import fetch_service


def get_delivered_benefit(req: Request, id: int):
    return fetch_service(req.token, SERVICES["benefits"]+"/activities/search-by-assistance/"+str(id))
