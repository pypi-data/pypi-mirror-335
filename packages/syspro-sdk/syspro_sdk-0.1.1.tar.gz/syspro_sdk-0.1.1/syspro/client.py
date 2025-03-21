import httpx
from .models.requisition import RequisitionModel
from .models.contract import ContractModel
from .models.stockcode import StockCodeModel
from .models.purchaseorder import PurchaseOrderModel
from .models.table import TableModel

class SysproClient:
    def __init__(self, base_url: str, operator: str, password: str, company: str, printer_url: str = "",):
        """
        SysproClient manages authentication and provides access to Syspro modules.
        """
        self.base_url = base_url
        self.printer_url = printer_url
        self.token = self.login(operator, password, company)
        self.printer_token = self.login_printer(operator, password, company)
        self.requisitions = RequisitionModel(self.base_url, self.token)
        self.contracts = ContractModel(self.base_url, self.token)
        self.stockcode = StockCodeModel(self.base_url, self.token)
        self.purchaseorders = PurchaseOrderModel(base_url=self.base_url, token=self.token, printer_url=self.printer_url,
                                                 printer_token=self.printer_token)
        self.tables = TableModel(base_url=self.base_url, token=self.token)

    def login(self, operator, pwd, company):
        try:
            params ={
                "Operator": operator,
                "OperatorPassword": pwd,
                "CompanyId": company
            }
            resp = httpx.get(f"{self.base_url}/Rest/logon", params=params)
            resp.raise_for_status()
        except Exception as e:
            raise Exception(f"Error trying to get token from Syspro: {e}")
        else:
            return resp.read().decode("utf-8")
    
    def login_printer(self, operator, pwd, company):
        if self.printer_url == "":
            return ""
        try:
            params = {
                "Username": operator,
                "Password": pwd,
                "Company": company
            }
            resp = httpx.post(f"{self.printer_url}/api/syspro/login", json=params)
            resp.raise_for_status()
        except Exception as e:
            raise Exception(f"Error trying to get token from Syspro Printer: {e}")
        else:
            result = resp.json()
            return result.get("token")
