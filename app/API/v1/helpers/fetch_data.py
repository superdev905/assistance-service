from fastapi import Request
import urllib3
import json
from fastapi.exceptions import HTTPException
from app.settings import SERVICES

http = urllib3.PoolManager()


def handle_response(result, endpoint=None) -> object:
    if(result.status == 200):
        return json.loads(result.data)
    raise HTTPException(status_code=400, detail="Error al obtener datos")


def fetch_parameter_data(token, endpoint: str, id: int) -> object:
    response = http.request(
        'GET', SERVICES["parameters"]+'/'+endpoint+'/'+str(id), headers={
            "Authorization": "Bearer %s" % token
        })

    return handle_response(response, endpoint)


def fetch_users_service(token: str, user_id: int) -> str:
    user_req = http.request(
        'GET', SERVICES["users"]+'/users/' + str(user_id), headers={
            "Authorization": "Bearer %s" % token
        })

    result = handle_response(user_req)

    return {**result,
            "paternalSurname": result["paternal_surname"],
            "maternalSurname": result["maternal_surname"]}


def fetch_service(token: str, route: str) -> str:
    user_req = http.request(
        'GET', route, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(user_req)

    return result


def get_employee_data(request: Request, id: int):
    return fetch_service(request.token, SERVICES["employees"] + "/employees/"+str(id))


def get_business_data(token: str, prefix: str, id: int):
    return fetch_service(token, SERVICES["business"] + "/"+prefix+"/"+str(id))


def delete_file_from_store(token: str, file_key: str):
    user_req = http.request(
        'DELETE', SERVICES["parameters"]+"/file/delete/"+file_key, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(user_req)

    return result
