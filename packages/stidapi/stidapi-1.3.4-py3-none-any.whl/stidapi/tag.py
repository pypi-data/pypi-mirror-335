from typing import List, Tuple, Union
from urllib.parse import urljoin

from stidapi import Doc
import stidapi.utils as u


class Tag:

    def __init__(self, inst_code: str, tag_no: str, data: dict = None):
        """
        Object initializer for Tag
        :param inst_code: STID installation code
        :param tag_no: Tag number as found in STID
        :param data: (Optional) dictionary of data as returned from Tag.get or Tag.search

        Initializes object and gets data from STID if available.
        """

        self.inst_code = ""
        self.no = ""
        self.description = ""
        self.category = ""
        self.discipline = ""
        self.is_function = False
        self.is_signal = False
        self.status = ""

        if not data:
            self._data = Tag.get(inst_code=inst_code, tag_no=tag_no)
        else:
            self._data = data

        common_prop = [
            ("instCode", "inst_code"),
            ("tagNo", "no"),
            ("description", "description"),
            ("tagCategoryDescription", "category"),
            ("disciplineCodeDescription", "discipline"),
            ("tagStatus", "status"),
        ]
        for prop in common_prop:
            if prop[0] in self._data:
                self.__setattr__(prop[1], self._data[prop[0]])
            else:
                self.__setattr__(prop[1], "")

        self.tag_no = self.no

        if "isFunction" in self._data and self._data["isFunction"]:
            self.is_function = True
            function_prop = [("functionBlock", "FB")]
            for prop in function_prop:
                if prop[0] in self._data:
                    self.__setattr__(prop[1], self._data[prop[0]])
        elif (
            "tagCategoryDescription" in self._data
            and self._data["tagCategoryDescription"].upper() == "FUNCTION"
        ):
            self.is_function = True

        if "isSignal" in self._data and self._data["isSignal"]:
            self.is_signal = True
            signal_prop = [("signalType", "signalType")]
            for prop in signal_prop:
                if prop[0] in self._data:
                    self.__setattr__(prop[1], self._data[prop[0]])
        elif (
            "tagCategoryDescription" in self._data
            and self._data["tagCategoryDescription"].upper() == "SIGNAL"
        ):
            self.is_signal = True

        optional_prop = [
            ("setpointL", "L"),
            ("setpointLl", "LL"),
            ("setpointH", "H"),
            ("setpointHh", "HH"),
        ]
        for prop in optional_prop:
            if prop[0] in self._data and self._data[prop[0]] is not None:
                self.__setattr__(prop[1], self._data[prop[0]])

    def get_addition_field(self, field: str = "") -> List[dict]:
        """Get list of additional fields. Optionally filter by type.

        Args:
            field (str, optional): Filter by field type. Defaults to "" which returns all.

        Returns:
            List[dict]: List of additional fields.
        """
        return self.get_additional_field(field=field)

    def get_additional_field(self, field: str = "") -> List[dict]:
        """Get list of additional fields. Optionally filter by type.

        Args:
            field (str, optional): Filter by field type. Defaults to "" which returns all.

        Returns:
            List[dict]: List of additional fields.
        """
        if field is None or len(field) == 0:
            return self._data["additionalFields"]

        return [x for x in self._data["additionalFields"] if x["type"] == field]

    def get_additional_field_value(self, field: str) -> List[Tuple[str, str]]:
        """Get list of tuples of value and description for additional field of a given type

        Args:
            field (str): Name of additional field to get

        Returns:
            List[Tuple[str, str]]: List of tuples. First value in each tuple is value, second is description.
        """
        f = self.get_additional_field(field=field)
        if len(f) > 0:
            return [(x["value"], x["description"]) for x in f]

        return []

    def get_doc(self) -> List["Doc"]:
        """Get list of documents that tag refers to.

        Returns:
            List[Doc]: List of referred Documents
        """

        return [Doc(x["instCode"], x["docNo"]) for x in self.get_doc_references()]

    def get_doc_references(self) -> List[dict]:
        """Get doc references of tag from stidapi as dicts.

        Returns:
            List[dict]: List of dicts describing document references.
        """
        url = urljoin(
            u.get_api_url(),
            f"{str(self.inst_code)}/tag/document-refs?tagNo={str(self.tag_no)}&noContentAs200=true",
        )
        json = u.get_json(url)
        return json

    def get_functional_location(self) -> str:
        """Get functional location of Tagged item or empty string if it does not have a functional location.

        Returns:
            str: Functional location or empty string if tagged item does not have a functional location.
        """

        url = urljoin(
            u.get_api_url(),
            f"portal/{self.inst_code}/tag/sap-tag?tagNo={self.tag_no}",
        )
        json = u.get_json(url)

        if isinstance(json, dict) and "functionalLocation" in json.keys():
            return json["functionalLocation"]
        else:
            return ""

    def __str__(self):
        """
        Overload string representation of object.
        :return: Pretty-print string describing Tag object
        """
        if isinstance(self._data, dict) and len(self._data) > 0:
            return str(self.tag_no) + "@" + str(self.inst_code) + " with data"
        else:
            return str(self.tag_no) + "@" + str(self.inst_code) + " with no data"

    def prune_empty_data(self):
        """
        Remove all empty, i.e., containing None, entries in data dictionary.
        """
        if isinstance(self._data, dict) and len(self._data) > 0:
            self._data = {k: v for k, v in self._data.items() if v is not None}

    @staticmethod
    def get(inst_code: str, tag_no: str):
        """
        Get tag data from STID for a single tag.
        :param inst_code: STID installation code
        :param tag_no: STID tag number
        :return: Dictionary of data from STID for tag.
        """

        url = urljoin(u.get_api_url(), str(inst_code) + "/tag?tagNo=" + str(tag_no))
        return u.get_json(url)

    @staticmethod
    def search(
        inst_code: str,
        tag_no: str = "",
        description: str = "",
        tag_status: str = "",
        tag_category: int = -1,
        tag_type: str = "",
        system: str = "",
        discipline_code: str = "",
        skip: int = 0,
        take: int = 50,
    ) -> List["Tag"]:
        """Search and get Tags with additional field.

        Args:
            inst_code (str): STID plant code
            tag_no (str, optional) Full or partial tag number to filter for. Defaults to "".
            description (str, optional) Full or partial tag number to filter for. Defaults to "".
            tag_status (str, optional) Tag Defaults to "".
            tag_category (int, optional) Negative numbers will return all. Defaults to -1.
            tag_type (str, optional) Defaults to "".
            system (str, optional) Defaults to "".
            discipline_code (str, optional) Defaults to "".
            skip (int, optional) Used for pagination. Number of search results to skip. Defaults to 0.
            take (int, optional) Used for pagination. Number of results to get. Defaults to 50.

        Returns:
            List[Tag]: List of Tag objects with a bit less data than when getting
        """

        # string subSystem, string mainSystem, string projectCode, string poNo,
        # string contrCode, string locationCode, string plantId,
        if len(tag_no) > 0:
            tag_no = "tagNo=" + tag_no + "&"

        if len(description) > 0:
            description = "description=" + description + "&"

        if len(tag_status) > 0:
            tag_status = "tagStatus=" + tag_status + "&"

        if tag_category > 0:
            tag_category_string = "tagCategory=" + str(tag_category) + "&"
        else:
            tag_category_string = ""

        if len(tag_type) > 0:
            tag_type = "tagType=" + tag_type + "&"

        if len(system) > 0:
            system = "system=" + system + "&"

        if len(discipline_code) > 0:
            discipline_code = "disciplineCode=" + discipline_code + "&"

        skip_string = "skip=" + str(skip) + "&"

        # take shall be last, thus no trailing &
        take_string = "take=" + str(take)

        url = urljoin(
            u.get_api_url(),
            f"/{inst_code}/tags"
            + "?"
            + str(tag_no)
            + str(description)
            + str(tag_status)
            + str(tag_category_string)
            + str(tag_type)
            + str(system)
            + str(skip_string)
            + str(take_string),
        )

        return [Tag(x["instCode"], x["tagNo"], x) for x in u.get_json(url)]

    @staticmethod
    def search_additional_field(
        inst_code: str, field_name: str, value: str = ""
    ) -> List["Tag"]:
        """Search and get Tags with additional field.

        Args:
            inst_code (str): STID plant code
            field_name (str): Name of additional field
            value (str, optional): Exact value. Defaults to empty which results all.

        Returns:
            List[Tag]: List of Tag objects
        """
        url = urljoin(
            u.get_api_url(),
            f"/{inst_code}/tag-additional-field/{field_name}?searchValue={value}&noContentAs200=true",
        )
        res = u.get_json(url)

        return [Tag(inst_code=inst_code, tag_no=x["tagNo"]) for x in res]

    @staticmethod
    def get_from_additional_field(
        field_name: str,
        value: str = "",
        inst_code: Union[str, List[str]] = None,
        stop_first=True,
    ) -> List["Tag"]:
        """Get List of Tag objects by searching for additional fields

        Args:
            field_name (str): Name of additional field
            value (str, optional): Value of additional field
            inst_code: STID plant code, or list of codes, to limit search to.
                Defaults to empty which will search all.
            stop_first (boolean): Set to False to get matches from all provided inst_code,
                else will stop at first match. Defaults to False.

        Returns:
            List[Tag): List of Tag objects
        """

        if inst_code is None or (isinstance(inst_code, str) and len(inst_code) == 0):
            from stidapi.plant import get_all_inst_code

            inst_code = get_all_inst_code()

        if isinstance(inst_code, str):
            inst_code = [inst_code]

        res = []
        for code in inst_code:
            res_code = Tag.search_additional_field(
                inst_code=code, field_name=field_name, value=value
            )
            if len(res_code) > 0:
                res.extend(res_code)

                if stop_first:
                    break

        return res
