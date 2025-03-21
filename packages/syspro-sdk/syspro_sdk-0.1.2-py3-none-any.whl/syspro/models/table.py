import xml.etree.ElementTree as ET
from .base import SysproBaseModel
from ..utils import find_operator


class TableModel(SysproBaseModel):
    def list(self, table_name: str, columns: list = None ,
                  wheres: list = None, order_by: dict = None):

        columns_expr = [{"Column": col} for col in columns]
        where_expr = []
        
        for i, where in enumerate(wheres):
            where_expr.append({
                "Expression": {
                    "OpenBracket": "(",
                    "Column": where[0],
                    "Condition": find_operator(where[1]),
                    "Value": where[2],
                    "CloseBracket": ")"
                }
            })

        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "COMFND.XSD"
            },
            "TableName": table_name,
            "Columns": columns_expr,
            "Where": where_expr,
            "OrderBy": {
                "Column": order_by
            }
        }

        self.list_items(bo="COMFND", xmlin=xmlin)
        return self