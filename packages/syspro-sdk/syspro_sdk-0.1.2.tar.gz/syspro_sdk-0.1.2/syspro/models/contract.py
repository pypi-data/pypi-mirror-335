import xml.etree.ElementTree as ET
from .base import SysproBaseModel
from ..utils import clean_field


class ContractModel(SysproBaseModel):

    def list(self, filter: dict = None, with_price_details: str = "N",
             with_extra_info: str = "N"):
        """
        :param filter: dict 
            Example of filter :
            
            {
                "Catalogue": catalogue,
                "Supplier": supplier,
                "StockCode": stockcode,
                "Reference": reference
            }
        
        :param with_price_details: str
        :param with_extra_info: str

        :return: list of contracts
        """
        xmlin = {
            "@attributes": {
                "xmlns:xsd": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd:noNamespaceSchemaLocation": "PORQCL.xsd"
            },
            "Option": {
                "IncludePriceDetails": with_price_details,
                "IncludeExtraPriceInformation": with_extra_info,
                "NewPagePerSupplier": "N"
            },
            "Filter": []
        }

        

        ## TODO: Put this in utils for better coding structure and keep DRY
        for key, value in filter.items():
            if value is not None:
                xmlin["Filter"].append({
                    key: {"@attributes": {"FilterType": "S", "FilterValue": value}}
                })
            else:
                xmlin["Filter"].append({
                    key: {"@attributes": {"FilterType": "A", "FilterValue": ""}}
                })

        self.query(bo="PORQCL", xmlin=xmlin)
        self.data = clean_field(data=self.data, field_name="PriceValidFrom", default_value="1900-01-01")
        self.data = clean_field(data=self.data, field_name="PriceValidTo", default_value="2999-01-01")
        self.fetch("SupplierStockCodeContractPrice.DetailsOfContracts.ContractDetail").flatten("ContractPriceHeader", "ContractLines.ContractLine")
        return self
