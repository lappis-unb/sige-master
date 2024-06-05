import logging

import httpx

logger = logging.getLogger("apps")

url_states = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"


def send_request(method, url, data=None):
    if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
        raise ValueError(f"Unsupported HTTP method: {method}")

    try:
        response = httpx.request(method, url, data=data)
        response.raise_for_status()
    except httpx.RequestError as e:
        return {"error": f"Error connecting to IBGE API: {str(e)}"}
    except httpx.HTTPStatusError as e:
        return {"error": f"Unexpected response from IBGE API: {str(e)}"}

    return response.json()


def list_states():
    data = send_request(method="GET", url=url_states)

    states = [state["nome"] for state in data]
    return states


def cities_by_state(state_code):
    url_cities = f"{url_states}/{state_code}/municipios"
    data = send_request(method="GET", url=url_cities)

    cities = [city["nome"] for city in data]
    return cities
