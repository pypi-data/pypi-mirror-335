import httpx
import xmltodict
import xml.etree.ElementTree as ET
import json
from ..utils import serialize_to_xml
from ..utils import filter_json
from ..utils import flatten_json, get_nested
from ..utils import clean_values
from ..errors import validate_attributes, validate_syspro_response


class SysproBaseModel:
    _default_doc_type = None
    _primary_key = "id"
    _default_values = {}

    def __init__(self, base_url, token, printer_url: str = None, printer_token: str = None):
        self.base_url = base_url
        self.printer_url = printer_url
        self.token = token
        self.printer_token = printer_token
        self.id = None
        self.status = None
        self.bo = None
        self.xmlin = {}
        self.xmlparams = {}
        self.xmlout = None
        self.root_tag = ""
        self.endpoint = ""
        self.request_params = None
        self.request_status = None
        self.obj = None
        self.data = []
    
    def print(self, doc_local: str = "L", doc_print: str = "True", doc_format: str = "0",
              reprint: str="N"):
        """
        Prints a document using the Syspro API.
        :param doc_type: The type of document to print.
        :param doc_local: The local of the document to print.
        :param doc_print: The print flag of the document to print.
        :param doc_format: The format of the document to print.
        :param reprint: The reprint flag of the document to print.
        """
        url = f"{self.printer_url}/api/syspro/print"
        doc_type = self._default_doc_type
        id = self.id

        header = {
            "Authorization": f"{self.printer_token}"
        }

        payload = {
            "DocumentType" : doc_type,
            "DocumentId" : id, 
            "DocumentFormat" : doc_format,
            "DocumentLocal" : doc_local,
            "DocumentPrint" : doc_print,
            "DocumentReprint" : reprint
        }

        try:
            validate_attributes(payload)
            resp = httpx.post(url, headers=header, json=payload, timeout=30.0)
            resp.raise_for_status()
            return resp
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error while sending POST to printer: {e}") from e
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP status error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"Error while sending POST to printer: {e}") from e

    def query(self, bo, xmlin: dict, xmlparams: dict = None,
              root_tag: str = "Query", endpoint: str = "/Rest/Query/Query"):
        try:
            xmlin = serialize_to_xml(data=xmlin, root_tag=root_tag)
            if xmlparams:
                xmlparams = serialize_to_xml(data=xmlparams, root_tag=root_tag)

            params = {
                "UserId": self.token,
                "BusinessObject": bo,
                "XmlIn": xmlin.replace("\n", "") if xmlin else "",
                "XmlParameters": xmlparams.replace("\n", "") if xmlparams else ""
            }
            url = f"{self.base_url}{endpoint}"
            self.request(url, params)
        except Exception as e:
            raise RuntimeError(f"Error trying to query Syspro with params : {e}")
        else:
            self.bo = bo
            self.xmlin = xmlin
            self.xmlparams = xmlparams
            self.endpoint = endpoint
            self.root_tag = root_tag
            self.obj = self.data
            return self

    def request(self, url, params, encoder: str = "latin1"):
        """
        Sends a GET request to the Syspro API.

        :param url: The URL to send the request to.
        :param params: The parameters to include in the request.
        """
        try:
            resp = httpx.get(url, params=params)
            resp.raise_for_status()
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error while request: {e}") from e
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP status error: {e.response.status_code} - {e.response.text}") from e
        else:
            self._process_response(resp, params)
            self.request_status = resp.status_code
            self.request_params = params
            return self

    def _process_response(self, resp: httpx.Response, params: dict) -> None:
        """
        Processes the HTTP response, decoding and parsing the data.

        :param resp: The HTTP response object.
        :param encoder: The encoding to decode the response.
        :param params: The original request parameters.
        """
        # Decode response
        response_text = resp.content.decode("utf-8")
        
        try:
            validate_syspro_response(resp)
        except ValueError as e:
            self.data = {f"ValueError in response : {e}"}
            self.request_status = 404
        else:
            # Parse XML to dictionary
            self.xmlout = response_text
            self.data = xmltodict.parse(response_text)

    def get_items(self, bo: str, xmlin: dict, id: str = None, xmlparams: dict = None,
                 root_tag: str = "Query", endpoint: str = "/Rest/Query/Query"):
        try:
            self.query(bo=bo, xmlin=xmlin, xmlparams=xmlparams,
                       root_tag=root_tag, endpoint=endpoint)
        except Exception as e:
            raise RuntimeError(f"Error trying to get item with id {id} : {e}")
        else:
            self.id = id
            return self

    def post(self, bo, xmlin: dict, root_tag: str, xmlparams: dict = None, 
             endpoint: str = "/Rest/Transaction/Post"):
        try:
            xmlin = serialize_to_xml(data=xmlin, root_tag=root_tag)
            if xmlparams:
                xmlparams = serialize_to_xml(data=xmlparams, root_tag=root_tag)
            
            params = {
                "UserId": self.token,
                "BusinessObject": bo,
                "XmlIn": xmlin.replace("\n", "") if xmlin else "",
                "XmlParameters": xmlparams.replace("\n", "") if xmlparams else ""
            }
            url = f"{self.base_url}{endpoint}"
            self.request(url, params)
        except Exception as e:
            raise RuntimeError(f"Error trying to post to Syspro with params : {e}")
        else:
            return self

    def fetch(self, dotted_key: str):
        """
        Extracts data from self.data based on a dotted selector and updates self.data.
        """
        fetched_json = None

        if self.obj:
            fetched_json = get_nested(self.obj, dotted_key.split("."))

        if fetched_json and (isinstance(fetched_json, dict) or isinstance(fetched_json, list)):
            self.data = fetched_json
        else:
            self.data = None

        return self

    def filter(self, filters):
        """
        Filters data based on a list of conditions using the jsonpath-ng library.
        """
        if self.data and isinstance(self.data, dict):
            self.data = [self.data]
            self.data = filter_json(self.data, filters)
        elif self.data and isinstance(self.data, list):
            self.data = filter_json(self.data, filters)
        return self
    
    def flatten(self, parent_key, nested_key):
        if self.data and (isinstance(self.data, dict) or isinstance(self.data, list)):
            self.data = flatten_json(self.data, parent_key, nested_key)
        return self

    def json(self):
        try:
            return json.dumps(self.data, indent=4)
        except (TypeError, ValueError) as e:
            return f"Error converting to JSON:{e}"
