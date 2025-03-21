from urllib.parse import urljoin

import stidapi.utils as u


class System:
    def __init__(self, inst_code: str = "", data=None):
        if isinstance(inst_code, str) and len(inst_code) > 0:
            self.inst_code = inst_code

        self._data = {}
        self.no = ""
        self.description = ""
        self.inst_code = ""
        self.valid = None

        if isinstance(data, dict) and len(data) > 0:
            self._data = data
            self.inst_code = data["instCode"]
            self.no = data["system"]
            self.description = data["description"]
            self.valid = data["validFlg"]

    @staticmethod
    def get_all_data(inst_code, is_valid: bool = False):
        """

        :param get_statistics:
        :return:
        """

        url = urljoin(u.get_api_url(), f"{inst_code}/system?isValid={is_valid}")
        parsed_json = u.get_json(url)

        return parsed_json

    @staticmethod
    def get_system(inst_code: str, get_statistics: bool = False):
        plant_data = System.get_all_data(inst_code, get_statistics)
        return [System(inst_code, x) for x in plant_data]
