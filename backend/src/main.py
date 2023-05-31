import json
from http import HTTPStatus
from typing import Any, Literal

from src.db import DB
from src.router import APIRouter

app = APIRouter()


@app.get('/real-estates')
def get_real_estates(
    status: list | None = None,
    year: list | None = None,
    city: list | None = None
) -> tuple[Literal[HTTPStatus.OK], str]:

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
