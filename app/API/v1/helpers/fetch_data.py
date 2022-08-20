import urllib3
import json
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from app.settings import SERVICES

http = urllib3.PoolManager()


def handle_response(result, endpoint=None) -> object:
    if(result.status == 200):
        return json.loads(result.data)
    raise HTTPException(status_code=400, detail="Error al obtener datos")


def fetch_list_parameters(token, endpoint: str) -> object:
    response = http.request(
        'GET', SERVICES["parameters"]+'/'+endpoint, headers={
            "Authorization": "Bearer %s" % token
        })

    return handle_response(response, endpoint)


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

    return {**result[0],
            "paternalSurname": result[0]["paternal_surname"],
            "maternalSurname": result[0]["maternal_surname"]}


def fetch_service(token: str, route: str) -> str:
    user_req = http.request(
        'GET', route, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(user_req)

    return result

def fetch_current_job_service(token: str, route: str, ids: list) -> str:
    encoded_data = json.dumps({"employee_id":ids})
    user_req = http.request(
        'POST', route, headers={
            "Authorization": "Bearer %s" % token,
            'Content-Type': 'application/json'
        }, body=encoded_data)
    
    result = handle_response(user_req)

    return result


def handle_request(token: str, route: str, body, method: str = "GET",) -> str:
    user_req = http.request(
        method, route, headers={
            "Authorization": "Bearer %s" % token
        }, body=json.dumps(body))

    result = handle_response(user_req)
    return result


def get_employee_data(request: Request, id: int):
    return fetch_service(request.token, SERVICES["employees"] + "/employees/"+str(id))

def get_employee_current_job(request: Request, id: list):
    return fetch_current_job_service(request.token, SERVICES["employees"] + "/employees/current-job", id)


def get_business_data(token: str, prefix: str, id: int):
    return fetch_service(token, SERVICES["business"] + "/"+prefix+"/"+str(id))


def delete_file_from_store(token: str, file_key: str):
    user_req = http.request(
        'DELETE', SERVICES["parameters"]+"/file/delete/"+file_key, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(user_req)

    return result


def get_managment_data(token: str, id: str):
    managment_req = http.request(
        'GET', SERVICES["parameters"]+"/management/"+id, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(managment_req)

    return result
