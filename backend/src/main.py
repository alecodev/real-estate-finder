import base64
import json
from http import HTTPStatus
from typing import Any

from src.db import DB
from src.router import APIRouter, Header

app = APIRouter()


@app.get('/real-estates')
def get_real_estates(
    status: list | None = None,
    year: list | None = None,
    city: list | None = None
) -> tuple[HTTPStatus, str | None]:

    conditions = ''
    data_conditions: list[Any] = []

    # Status
    status_allowed = ['pre_venta', 'en_venta', 'vendido']
    status_show = status_allowed

    if status is not None:
        status_show = list(
            filter(lambda item: item in status_allowed, set(status)))
        if len(status_show) == 0:
            return HTTPStatus.OK, json.dumps([])

    conditions += 's.name ' + DB.filter_by_number_of_elements(status_show)
    data_conditions += status_show

    # Construction Year
    if year is not None:
        construction_year_show = list(map(lambda item: int(item), filter(
            lambda item: item.isnumeric(), set(year))))
        if len(construction_year_show) == 0:
            return HTTPStatus.OK, json.dumps([])

        conditions += ' AND p.year ' + \
            DB.filter_by_number_of_elements(construction_year_show)
        data_conditions += construction_year_show

    # City
    if city is not None:
        city_show = list(set(city))
        if len(city_show) == 0:
            return HTTPStatus.OK, json.dumps([])

        conditions += ' AND p.city ' + \
            DB.filter_by_number_of_elements(city_show)
        data_conditions += city_show

    db = DB()
    db.execute(
        """
        SELECT p.address, p.city, s.name AS status, p.price, p.description
        FROM property p
        INNER JOIN (
        SELECT property_id, status_id
        FROM (
            SELECT
            a.property_id, a.status_id,
            @r := (
                CASE
                WHEN a.property_id = @prev_property_id THEN @r + 1
                WHEN (@prev_property_id := a.property_id) = NULL THEN NULL
                ELSE 1
                END
            ) AS row_number
            FROM (
            SELECT id, property_id, status_id
            FROM status_history
            ORDER BY property_id, id DESC
            LIMIT 18446744073709551615
            ) a,
            (SELECT @r := 0, @prev_property_id := NULL) X
            ORDER BY a.property_id, a.id DESC
        ) a
        WHERE a.row_number=1
        ) property_last_status ON p.id=property_last_status.property_id
        INNER JOIN status s ON property_last_status.status_id=s.id
        WHERE """ + conditions,
        data=data_conditions,
        fields=True
    )

    return HTTPStatus.OK, json.dumps(db.results)


@app.post('/real-estates/{id}/likes')
def post_real_estates_likes(
    id: int,
    headers: Header
) -> tuple[HTTPStatus, str | None]:

    _authorization = headers.Authorization
    if _authorization is None or (not _authorization.startswith('Basic ')):
        return HTTPStatus.UNAUTHORIZED, None

    try:
        authorization = base64.b64decode(
            (_authorization[6:]).encode('utf-8')).decode('utf-8').split(':')
    except Exception as e:
        return HTTPStatus.BAD_REQUEST, None
    else:
        if len(authorization) != 2:
            return HTTPStatus.UNAUTHORIZED, None

    _user, _pass = authorization

    db = DB()

    db.execute(
        "SELECT id FROM auth_user WHERE username = %s AND password = %s AND is_active = %s LIMIT 1",
        data=[_user, _pass, 1],
        fields=True
    )

    if len(db.results) == 0:
        return HTTPStatus.UNAUTHORIZED, None

    id_user = db.results[0]['id']

    db.execute(
        "SELECT id FROM property WHERE id = %s LIMIT 1",
        data=[id],
        fields=True
    )

    if len(db.results) == 0:
        return HTTPStatus.FORBIDDEN, None

    id_like = db.execute(
        "INSERT INTO property_likes SET property_id = %s, user_id = %s",
        data=[id, id_user],
        fields=False
    )
    if id_like is not None and id_like > 0:
        return HTTPStatus.OK, json.dumps([])
    else:
        return HTTPStatus.INTERNAL_SERVER_ERROR, json.dumps([])
