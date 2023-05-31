import json
import unittest
from http import HTTPStatus

from src.main import get_real_estates


class RealEstate(unittest.TestCase):

    def test_response_code_status(self) -> None:
        try:
            code_status, _ = get_real_estates()
        except:
            self.fail("get_real_estates generated an unexpected error")
        else:
            self.assertIn(code_status, HTTPStatus)

    def test_response_data(self) -> None:
        try:
            _, response = get_real_estates()
            data_response = json.loads(response)
        except TypeError:
            self.fail("Unexpected error deserializing data")
        except:
            self.fail("get_real_estates generated an unexpected error")
        else:
            self.assertIs(type(data_response), list)
            if len(data_response) > 0:
                self.assertIs(type(data_response[0]), dict)
                self.assertCountEqual(list(data_response[0].keys()), [
                                      'address', 'city', 'status', 'price', 'description'])

    def test_response_data_status(self) -> None:
        _, response = get_real_estates()
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail("Error get_real_estates is not returning data")

        self.assertIs(type(data_response[0]), dict)
        self.assertCountEqual(list(data_response[0].keys()), [
                              'address', 'city', 'status', 'price', 'description'])
        status_data = list(
            set(map(lambda item: item['status'], data_response)))
        status_allowed = ['pre_venta', 'en_venta', 'vendido']
        for status in status_data:
            self.assertIn(status, status_allowed)

    def test_response_data_status_filter(self) -> None:
        _, response = get_real_estates(status=['comprado'])
        data_response = json.loads(response)
        if len(data_response) > 0:
            self.fail(
                "Error, get_real_estates is returning data when filtering for wrong status")

        _, response = get_real_estates(status=['pre_venta'])
        data_response = json.loads(response)

        status_data = list(
            set(map(lambda item: item['status'], data_response)))
        status_allowed = ['pre_venta']
        for status in status_data:
            self.assertIn(status, status_allowed)

    def test_response_data_construction_year_filter(self) -> None:
        _, response = get_real_estates(year=['2021'])
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail(
                "Error, get_real_estates is not returning data when filtering for construction year 2021")

        self.assertEqual(len(data_response), 7)

        _, response = get_real_estates(year=['2021', '2000'])
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail(
                "Error, get_real_estates is not returning data when filtering for construction year 2021 and 2000")

        self.assertEqual(len(data_response), 11)

    def test_response_data_construction_city_filter(self) -> None:
        _, response = get_real_estates(city=['bogota'])
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail(
                "Error, get_real_estates is not returning data when filtering for city bogota")

        self.assertEqual(len(data_response), 7)

        _, response = get_real_estates(city=['bogota', 'medellin'])
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail(
                "Error, get_real_estates is not returning data when filtering for city bogota and medellin")

        self.assertEqual(len(data_response), 12)

    def test_response_data_filter_multiple(self) -> None:
        _, response = get_real_estates(
            status=['pre_venta'],
            year=['2000', '2021'],
            city=['bogota']
        )
        data_response = json.loads(response)
        if len(data_response) == 0:
            self.fail(
                "Error, get_real_estates is not returning data when filtering for city bogota and status pre_venta and construction year between 2000 and 2021")

        self.assertEqual(len(data_response), 1)
