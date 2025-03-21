import xml.etree.ElementTree as ET
from .base import SysproBaseModel
from datetime import datetime

class PurchaseOrderModel(SysproBaseModel):
    _primary_key = "PurchaseOrder"
    _default_doc_type = "Purchase orders - local"

    def get(self, id: str):

        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORQ60.XSD"
            },
            "Option": {
                "DateSelection": "N",
                "ReportType": "D",
                "OrderStatus": "A",
                "PrintLineDueDate": "N",
                "PrintCatalogue": "N",
                "IncludeLocalPurchaseOrders": "Y",
                "IncludeImportPurchaseOrders": "Y",
                "IncludeOtherPurchaseOrders": "Y",
                "IncludeZeroQtyOutstandingOrder": "N",
                "RevisionRelease": None,
            },
            "Filter": {
                "PurchaseOrder": {
                    "@attributes": {
                        "FilterType": "S",
                        "FilterValue": id
                    }
                }
            }
        }
        self.get_items(bo="PORQ60", id=id, xmlin=xmlin)
        self.status = self.obj.get("PurchaseOrdersByOrderNumber").get("PurchaseOrders").get("PurchaseOrder").get("OrderHeader").get("Status")
        return self
    
    def print(self, doc_local: str = "L", doc_print: str = "True", doc_format: str = "0",
              reprint: str="N"):
        doc_local = "F" if self.obj.get("PurchaseOrdersByOrderNumber").get("PurchaseOrders").get("PurchaseOrder").get("OrderHeader").get("OrderType") == "I" else "L"
        reprint = "Y" if self.obj.get("PurchaseOrdersByOrderNumber").get("PurchaseOrders").get("PurchaseOrder").get("OrderHeader").get("Status") == "4" else "N"

        return super().print(doc_local=doc_local, doc_print=doc_print, doc_format=doc_format, reprint=reprint)
