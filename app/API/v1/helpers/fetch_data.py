import urllib3
import json
from fastapi import Request
from fastapi.exceptions import HTTPException
from app.settings import SERVICES

http = urllib3.PoolManager()


def handle_response(result, endpoint=None) -> object:
    print(result, '<<<--- Resultado de la consulta a AUTH')
    if(result.status == 200):
        print(result.status, '<<<--- Estatus de la respuesta.')
        print(result.data, '<<<--- Datos en la respuesta.')
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

    print(user_req, '<<<--- USUARIO OBTENIDO DE AUTH SERVICE')
    result = handle_response(user_req)

    print(result, "<<<--- Data sin parsear ni nada, en duro")
    print(result[0]["paternal_surname"], '<<<--- Apellido paterno resultante.')
    print(result["maternal_surname"], '<<<--- Apellido materno resultante.')
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


def handle_request(token: str, route: str, body, method: str = "GET",) -> str:
    user_req = http.request(
        method, route, headers={
            "Authorization": "Bearer %s" % token
        }, body=json.dumps(body))

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


def get_managment_data(token: str, id: str):
    managment_req = http.request(
        'GET', SERVICES["parameters"]+"/management/"+id, headers={
            "Authorization": "Bearer %s" % token
        })
    result = handle_response(managment_req)

    return result
