from typing import List
from urllib.parse import urljoin
import stidapi.utils as u


class File:
    """Class for internal use. Copy of File as returned by document endpoint."""

    # "id": 0,
    # "instCode": "string",
    # "fileName": "string",
    # "objectType": "string",
    # "description": "string",
    # "fileOrder": 0,
    # "prodViewCode": "string",
    # "insertedDate": "2024-04-09T11:46:07.501Z",
    # "thumbnail": "string",
    # "fileSize": 0,
    # "blobId": "string"

    def __init__(self, data: dict):
        for prop in data.keys():
            self.__setattr__(prop, data[prop])

    def __str__(self):
        return f"InstCode: {self.instCode}, FileName: {self.fileName}, Description: {self.description}, ObjectType: {self.objectType}"


class Revision:
    """Class for internal use. Copy of Revision as returned by document endpoint."""

    # "revNo": "string",
    # "revStatus": "string",
    # "revStatusDescription": "string",
    # "revDate": "2024-04-09T11:46:07.501Z",
    # "isCurrent": true,
    # "projectCode": "string",
    # "projectCodeDescription": "string",
    # "reasonForIssue": "string",
    # "acceptanceCode": 0,
    # "acceptanceCodeDescription": "string",
    # "files": [File objects]

    def __init__(self, data: dict):
        self._data = data
        for prop in data.keys():
            if prop == "files":
                continue
            self.__setattr__(prop, data[prop])

    def get_files(self):
        return [File(x) for x in self._data["files"]]

    def __str__(self):
        return (
            f"RevNo: {self.revNo}, RevStatus: {self.revStatus}, RevDate: {self.revDate}"
        )


class Doc:
    def __init__(self, inst_code: str, doc_no: str):
        """
        Object initializer for Doc
        :param inst_code: STID installation code
        :param doc_no: Doc number as found in STID

        Initializes object and gets data from STID if available.
        """
        self.inst_code = ""
        self.no = ""
        self.title = ""

        self.category = ""
        self.discipline = ""
        self.type = ""

        self._data = Doc.get(inst_code=inst_code, doc_no=doc_no)

        common_prop = [
            ("instCode", "inst_code"),
            ("docNo", "no"),
            ("docTitle", "title"),
            ("docCategoryDescription", "category"),
            ("disciplineCodeDescription", "discipline"),
            ("docTypeDescription", "type"),
        ]
        for prop in common_prop:
            if prop[0] in self._data:
                self.__setattr__(prop[1], self._data[prop[0]])
            else:
                self.__setattr__(prop[1], "")

        self.docNo = self.no
        self.description = self.title

        optional_prop = []
        for prop in optional_prop:
            if prop[0] in self._data and self._data[prop[0]] is not None:
                self.__setattr__(prop[1], self._data[prop[0]])

    def get_current_revision(self) -> Revision:
        return Revision(self._data["currentRevision"])

    def get_files(self) -> List[File]:
        return self.get_current_revision().get_files()

    def __str__(self):
        return f"InstCode: {self.inst_code}, No: {self.no}, Title: {self.title}"

    # "instCode": "string", "instCodeDescription": "string",
    # "docNo": "string", "docTitle": "string",
    # "docCategory": "string", "docCategoryDescription": "string",
    # "docType": "string", "docTypeDescription": "string",
    # "projectCode": "string", "projectCodeDescription": "string",
    # "contrCode": "string", "contrCodeDescription": "string",
    # "disciplineCode": "string","disciplineCodeDescription": "string",
    # "locationCode": "string","locationCodeDescription": "string",
    # "docClass": "string","docClassName": "string",        "docClassDescription": "string",
    # "poNo": "string","poNoDescription": "string",
    # "system": "string","systemDescription": "string",
    # "remark": "string",
    # "supplDocNo": "string",
    # "companyCode": "string",
    # "source": "string",
    # "size": "string",
    # "priority": "string",        "priorityDescription": "string",
    # "weightBearing": "string",
    # "productCode": "string",
    # "insulationClass": "string",        "insulationClassDescription": "string",
    # "tagRefCount": 0,        "docRefCount": 0,
    # "currentRevision": { Revision object },
    # "projectRevisions": [ { Revision object }],
    # "additionalFields": [{"type": "string","typeDescription": "string","value": "string","description": "string"}],
    # "projects": [{"instCode": "string","projectCode": "string","description": "string","stidDeliveryCode": "string",
    #        "insertedDate": "2024-04-09T11:46:07.501Z","isPrimary": true,"isValid": true,}],
    # "purchaseOrders": [
    #    {"instCode": "string","poNo": "string","description": "string","insertedDate": "2024-04-09T11:46:07.501Z","isPrimary": true,"isValid": true}],
    # "apiResponseTime": "string",

    @staticmethod
    def get(inst_code: str, doc_no: str):
        """
        Get data from STID for a single doc.
        :param inst_code: STID installation code
        :param doc_no: STID doc number
        :return: Dictionary of data from STID for doc.
        """

        url = urljoin(
            u.get_api_url(), str(inst_code) + "/document?docNo=" + str(doc_no)
        )
        return u.get_json(url)
