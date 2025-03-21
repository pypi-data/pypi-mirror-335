import xml.etree.ElementTree as ET
from .base import SysproBaseModel
from datetime import datetime


class RequisitionModel(SysproBaseModel):
    _primary_key = "Requisition"
    _default_doc_type = "Purchase orders - local"

    def get(self, user_name: str, id: str = None, user_password: str = None,
            line:str = None, with_approved: str = "N", with_notes: str = "N",
            with_comments: str = "N", type_of: str = "S"):
        
        """
        Type of requisition details to be returned (
        O = all requisitions originated by this user, 
        R = all requisitions routed to this user , 
        S = a single requisition originated by this user, using the values against the RequisitionNumber and RequisitionLine elements, 
        T = a single requisition routed to this user, using the values against the RequisitionNumber and RequisitionLine elements.)
        """
    
        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORQRQ.xsd"
            },
            "Key": {
                "RequisitionUser": user_name
            },
            "Option": {
                "TypeOfRequisition": type_of,
                "UserPassword": user_password,
                "RequisitionNumber": id,
                "RequisitionLine": line,
                "IncludeApproved": with_approved,
                "IncludeNotes": with_notes,
                "IncludePurchaseOrderComments": with_comments,
                "XslStylesheet": None
            }
        }

        self.get_items(bo="PORQRQ", id=id, xmlin=xmlin)
        self.user_name = user_name
        self.user_password = user_password
        return self

    def update(self, json: dict, action_type: str = "C", allow_nonstocked: str = "N",):
        '''
        Args: 
        action_type : Add or Change action type A - Add a requisition, C - Change a requisition
        The ADD action type will automatically generate a new requisition number
        (assuming requisition auto numbering) for each new requisition. 
        Requisition lines can be added to an existing requisition.
        '''
        
        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRQDOC.xsd"
            },
            "Item": {}
        }

        xmlin["Item"]["RequisitionNumber"] = self.id
        xmlin["Item"]["User"] = self.user_name
        xmlin["Item"]["UserPassword"] = self.user_password
        xmlin["Item"].update(json)

        xmlparams = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRQ.XSD"
            },
            "Parameters": {
                "AllowNonStockedItems": allow_nonstocked,
                "AcceptGLCodeforStocked": "N",
                "IgnoreWarnings": "Y",
                "ActionType": action_type,
                "GiveErrorWhenDuplicateFound": "N",
                "ApplyIfEntireDocumentValid": "Y",
                "ValidateOnly": "N"
            }
        }
        self.post(bo="PORTRQ", xmlin=xmlin, xmlparams=xmlparams,
                   root_tag="PostRequisition",endpoint="/Rest/Transaction/Post")

        return self

    def update_route(self, req_line: str, to_user: str, notation: str):
        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRRDOC.xsd"
            },
            "Item": {}
        }

        xmlin["Item"]["RequisitionNumber"] = self.id
        xmlin["Item"].update({
            "User": self.user_name,
            "UserPassword": self.user_password,
            "RequisitionLine": req_line,
            "RouteToUser": to_user,
            "RouteNotation": notation
        })

        xmlparams = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRR.XSD"
            },
            "Parameters": None
        }

        self.post(bo="PORTRR", xmlin=xmlin, root_tag="PostReqRoute",
                  xmlparams=xmlparams, endpoint="/Rest/Transaction/Post")
        return self
    
    def update_status(self, req_line: str = None, action_type: str = "A",
                      ignore_cancel: str = "Y"):
        
        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRADOC.xsd"
            },
            "Item": {
                "User": self.user_name,
                "UserPassword": self.user_password,
                "RequisitionNumber": self.id,
                "RequisitionLine": req_line,
            }
        }

        xmlparams = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTRA.XSD"
            },
            "Parameters": {
                "ActionType": action_type,
                "IgnoreCancelledLines": ignore_cancel,
                "IgnoreWarnings": "Y",
                "ApplyIfEntireDocumentValid": "Y",
                "ValidateOnly": "N"
            }
        }

        self.post(bo="PORTRA", xmlin=xmlin, xmlparams=xmlparams,
                   root_tag="PostReqApprove", endpoint="/Rest/Transaction/Post")
        return self
    
    def create_po(self, req_lines: list, due_date: str = None,
                  apply_duedate_to_lines: str = "A", include_in_mrp: str = "Y",
                  delivery_address: dict = {}, extra_json: dict = {}):
        
        # Create the XML structure for the Order Header
        order_header = {}
        order_header.update({
            "OrderActionType": "A",
            "PurchaseOrder": None,
        })

        order_header.update({
            "OrderDate": datetime.now().strftime("%Y-%m-%d"),
            "DueDate": due_date,
            "MemoDate": due_date,
            "ApplyDueDateToLines": apply_duedate_to_lines,
            "DeliveryName": delivery_address.get("name", None),
            "DeliveryAddr1": delivery_address.get("building", None),
            "DeliveryAddr2": delivery_address.get("address", None),
            "DeliveryAddr3": delivery_address.get("city", None),
            "DeliveryAddrLoc": delivery_address.get("localty", None),
            "DeliveryAddr4": delivery_address.get("state", None),
            "DeliveryAddr5": delivery_address.get("country", None),
            "PostalCode": delivery_address.get("postal_code", None),
            "IncludeInMrp": include_in_mrp,
        })

        ##
        #  FOR EXTRA JSON
        #
        # {
        #     "ExchRateFixed": None,
        #     "ExchangeRate": None,
        #     "Customer": None,
        #     "TaxStatus": "N",
        #     "PaymentTerms": None,
        #     "InvoiceTerms": None,
        #     "CustomerPoNumber": None,
        #     "ShippingInstrs": None,
        #     "MemoCode": None,
        #     "Buyer": None,
        #     "DeliveryGpsLat": '00.000000',
        #     "DeliveryGpsLong": '000.000000',
        #     "DeliveryTerms": None,
        #     "ShippingLocation": None,
        #     "AutoVoucher": None,
        #     "LanguageCode": None,
        #     "DiscountLessPlus": None,
        #     "DiscPercent1": None,
        #     "DiscPercent2": None,
        #     "DiscPercent3": None,
        #     "ChgPOStatToReadyToPrint": None,
        #     "PortofArrival": None,
        #     "RegimeCode": None,
        #     "eSignature": None
        # }

        order_header.update(extra_json)

        req_details = []
       
        for req_line in req_lines:
            req_details.append({
                "Requisition": self.id,
                "RequisitionLine": req_line,
                "PreferredSupplier": None,
                "SuggestedReqn": None
            })

        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTTPDOC.xsd"
            },
            "Item": {
                "User": self.user_name,
                "UserPassword": self.user_password,
                "RequisitionNumber": self.id,
                "OrderHeader": order_header,
                "OrderDetails": {
                    "RequisitionDetail": req_details
                }
            }
        }

        xmlparams = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORTTP.XSD"
            },
            "Parameters": {
                "TransactionDate": datetime.now().strftime("%Y-%m-%d"),
                "ApplyIfEntireDocumentValid": "Y",
                "WarehouseForNonStk": None,
                "IncludeCustomerInValidationCriteria": "Y",
                "IncludeCustomerPOInValidationCriteria": "Y",
                "IncludeApprovedMRPOnly": "Y",
                "DefaultDeliveryAddress": "",
                "IgnoreSupplierMinimums": "Y",
                "CopyCustomForms": "N",
                "ConvertQtyToAltUm": "N",
                "IgnoreWarnings": "Y",
                "ValidateOnly": "N"
            }
        }

        self.post(bo="PORTTP", xmlin=xmlin, xmlparams=xmlparams,
                   root_tag="PostRequisitionCreatePo")
        return self
