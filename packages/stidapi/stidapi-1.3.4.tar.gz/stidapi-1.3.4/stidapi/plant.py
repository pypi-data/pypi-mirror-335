from typing import List, Union
from urllib.parse import urljoin

import stidapi.utils as u
import logging

logger = logging.getLogger(__name__)


class Plant:
    _plant_list = []

    def __init__(self, code: Union[str, int] = "", data=None):
        self.inst_code = ""
        self.sap_id = ""
        self.description = ""
        self.business_area = ""
        self.ims = ""

        if isinstance(code, int):
            code = str(code)

        if isinstance(code, str) and len(code) > 0:
            self.inst_code = code
            if data is None:
                data = Plant._get_data(code)

        if isinstance(data, dict) and len(data) > 0:
            self._data = data
            self.inst_code = data["instCode"]
            self.sap_id = data["sapPlantId"]
            self.description = data["description"]
            self.business_area = data["businessArea"]
            self.ims = data["imsPlant"]
        else:
            self._data = {}

        self.plant_code = self.inst_code

    def __str__(self):
        if not isinstance(self.inst_code, str) or len(self.inst_code) == 0:
            return "Empty plant object"

        if len(self._data) > 0:
            return (
                "Plant "
                + str(self.inst_code)
                + " - "
                + str(self.description)
                + " with data"
            )
        else:
            return (
                "Plant "
                + str(self.inst_code)
                + " - "
                + str(self.description)
                + " with no data"
            )

    def get_tag(self, tag_no: str):
        """Get Tag from Plant

        Args:
            tag_no (str): Tag number

        Returns:
            Tag: Tag object
        """
        from stidapi import Tag

        return Tag(self.inst_code, tag_no=tag_no)

    def search_tag(self, tag_no: str = "", description: str = "", take: int = 50):
        from stidapi import Tag

        return Tag.search(self.inst_code, tag_no, description, take=take)

    def get_doc(self, doc_no: str):
        """Get Doc from Plant

        Args:
            doc_no (str): Document number

        Returns:
            Doc: Doc object
        """
        from stidapi import Doc

        return Doc(self.inst_code, doc_no)

    @classmethod
    def get_all_data(cls):
        if len(cls._plant_list) == 0:
            url = urljoin(u.get_api_url(), "plants")
            parsed_json = u.get_json(url)

            if isinstance(parsed_json, list):
                cls._plant_list = [x for x in parsed_json if "instCode" in x]

        return cls._plant_list

    @staticmethod
    def _get_data(code: Union[str, int]):
        if (
            code is None
            or (isinstance(code, str) and len(code) == 0)
            or (isinstance(code, int) and code < 1000)
        ):
            return None

        plant_data_list = Plant.get_all_data()

        if len(plant_data_list) == 0:
            return None

        if isinstance(code, str):
            plant_data_list = [
                x
                for x in plant_data_list
                if x["instCode"].lower() == code.lower() or x["sapPlantId"] == code
            ]
        elif isinstance(code, int):
            plant_data_list = [x for x in plant_data_list if x["sapPlantId"] == code]
        else:
            return ValueError("Input code must be string or int.")

        if len(plant_data_list) > 0:
            return plant_data_list[0]
        else:
            logger.info("Warning: did not get data for Plant " + str(code))
            return None

    @classmethod
    def get_plant(cls, inst_code: Union[str, int]) -> "Plant":
        plant_data = Plant._get_data(inst_code)
        return Plant(inst_code, plant_data)

    @classmethod
    def get_plants(cls) -> List["Plant"]:
        plant_data_list = Plant.get_all_data()

        return [Plant(x["instCode"], x) for x in plant_data_list]


def get_all_inst_code() -> List[str]:
    """Get list of all STID plant installation codes

    Returns:
        List[str]: List of all installation codes.
    """

    return [x["instCode"] for x in Plant.get_all_data()]
