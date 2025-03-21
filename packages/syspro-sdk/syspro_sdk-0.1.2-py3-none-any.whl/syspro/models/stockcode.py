import xml.etree.ElementTree as ET
from .base import SysproBaseModel

class StockCodeModel(SysproBaseModel):

    def get(self, id, columns: list = ["StockCode"]):

        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "COMFND.XSD"
            },
            "TableName": "InvMaster",
            "Columns": {
                "Column": columns
            },
            "Where": {
                "Expression": {
                    "OpenBracket": "(",
                    "Column": "StockCode",
                    "Condition": "EQ",
                    "Value": id,
                    "CloseBracket": ")"
                }
            },
            "OrderBy": {
                "Column": "StockCode"
            }
        }
        self.get_items(id=id, bo="COMFND", xmlin=xmlin)
        return self