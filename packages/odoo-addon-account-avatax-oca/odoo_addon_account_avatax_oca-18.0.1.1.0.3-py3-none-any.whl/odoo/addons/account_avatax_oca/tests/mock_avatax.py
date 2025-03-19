def _mock_line(product_data):
    subtotal = product_data.get("price_unit", 0.0) * product_data.get(
        "quantity"
    ) - product_data.get("discount_amount")
    tax_amount = subtotal * product_data.get("rate_expected", 0.0)
    res = {
        "boundaryOverrideId": 0,
        "businessIdentificationNo": "",
        "costInsuranceFreight": 0.0,
        "customerUsageType": "",
        "description": product_data.get("product")
        and product_data.get("product").display_name
        or "No Name",
        "destinationAddressId": 85600959974166,
        "details": [
            {
                "addressId": 85600959974167,
                "chargedTo": "Buyer",
                "country": "US",
                "countyFIPS": "",
                "exemptAmount": product_data.get("exemption_amount", 0.0),
                "exemptReasonId": 3,
                "exemptRuleId": 7455340,
                "exemptUnits": product_data.get("exemption_amount", 0.0),
                "id": 85600959974176,
                "inState": True,
                "isFee": False,
                "isNonPassThru": False,
                "jurisCode": "29",
                "jurisName": "MISSOURI",
                "jurisType": "STA",
                "jurisdictionId": 2000001420,
                "jurisdictionType": "State",
                "liabilityType": "Seller",
                "nonTaxableAmount": 0.0,
                "nonTaxableRuleId": 0,
                "nonTaxableType": "RateRule",
                "nonTaxableUnits": 0.0,
                "rate": product_data.get("rate_expected", 0.0),
                "rateRuleId": 1065438,
                "rateSourceId": 3,
                "rateType": "General",
                "rateTypeCode": "G",
                "region": "MO",
                "reportingExemptUnits": product_data.get("exemption_amount", 0.0),
                "reportingNonTaxableUnits": 0.0,
                "reportingTax": 0.0,
                "reportingTaxCalculated": 0.0,
                "reportingTaxableUnits": 0.0,
                "serCode": "",
                "signatureCode": "AXYM",
                "sourcing": "Origin",
                "stateAssignedNo": "",
                "stateFIPS": "29",
                "tax": tax_amount,
                "taxAuthorityTypeId": 45,
                "taxCalculated": tax_amount,
                "taxName": "MO STATE TAX",
                "taxOverride": 0.0,
                "taxRegionId": 2078034,
                "taxSubTypeId": "S",
                "taxType": "Sales",
                "taxTypeGroupId": "SalesAndUse",
                "taxableAmount": subtotal,
                "taxableUnits": subtotal,
                "transactionId": 85600959974165,
                "transactionLineId": 85600959974171,
                "unitOfBasis": "PerCurrencyUnit",
            },
            {
                "addressId": 85600959974167,
                "chargedTo": "Buyer",
                "country": "US",
                "countyFIPS": "",
                "exemptAmount": product_data.get("exemption_amount", 0.0),
                "exemptReasonId": 3,
                "exemptRuleId": 7455340,
                "exemptUnits": product_data.get("exemption_amount", 0.0),
                "id": 85600959974177,
                "inState": True,
                "isFee": False,
                "isNonPassThru": False,
                "jurisCode": "037",
                "jurisName": "CASS",
                "jurisType": "CTY",
                "jurisdictionId": 1527,
                "jurisdictionType": "County",
                "liabilityType": "Seller",
                "nonTaxableAmount": 0.0,
                "nonTaxableRuleId": 0,
                "nonTaxableType": "RateRule",
                "nonTaxableUnits": 0.0,
                "rate": product_data.get("rate_expected", 0.0),
                "rateRuleId": 1654198,
                "rateSourceId": 3,
                "rateType": "General",
                "rateTypeCode": "G",
                "region": "MO",
                "reportingExemptUnits": product_data.get("exemption_amount", 0.0),
                "reportingNonTaxableUnits": 0.0,
                "reportingTax": 0.0,
                "reportingTaxCalculated": 0.0,
                "reportingTaxableUnits": 0.0,
                "serCode": "",
                "signatureCode": "AYFX",
                "sourcing": "Origin",
                "stateAssignedNo": "56756-037-000",
                "stateFIPS": "29",
                "tax": tax_amount,
                "taxAuthorityTypeId": 45,
                "taxCalculated": tax_amount,
                "taxName": "MO COUNTY TAX",
                "taxOverride": 0.0,
                "taxRegionId": 2078034,
                "taxSubTypeId": "S",
                "taxType": "Sales",
                "taxTypeGroupId": "SalesAndUse",
                "taxableAmount": subtotal,
                "taxableUnits": subtotal,
                "transactionId": 85600959974165,
                "transactionLineId": 85600959974171,
                "unitOfBasis": "PerCurrencyUnit",
            },
            {
                "addressId": 85600959974167,
                "chargedTo": "Buyer",
                "country": "US",
                "countyFIPS": "",
                "exemptAmount": product_data.get("exemption_amount", 0.0),
                "exemptReasonId": 3,
                "exemptRuleId": 7455340,
                "exemptUnits": product_data.get("exemption_amount", 0.0),
                "id": 85600959974178,
                "inState": True,
                "isFee": False,
                "isNonPassThru": False,
                "jurisCode": "56756",
                "jurisName": "PECULIAR",
                "jurisType": "CIT",
                "jurisdictionId": 85774,
                "jurisdictionType": "City",
                "liabilityType": "Seller",
                "nonTaxableAmount": 0.0,
                "nonTaxableRuleId": 0,
                "nonTaxableType": "RateRule",
                "nonTaxableUnits": 0.0,
                "rate": product_data.get("rate_expected"),
                "rateRuleId": 1391040,
                "rateSourceId": 3,
                "rateType": "General",
                "rateTypeCode": "G",
                "region": "MO",
                "reportingExemptUnits": product_data.get("exemption_amount", 0.0),
                "reportingNonTaxableUnits": 0.0,
                "reportingTax": 0.0,
                "reportingTaxCalculated": 0.0,
                "reportingTaxableUnits": 0.0,
                "serCode": "",
                "signatureCode": "AYGM",
                "sourcing": "Origin",
                "stateAssignedNo": "56756-037-000",
                "stateFIPS": "29",
                "tax": tax_amount,
                "taxAuthorityTypeId": 45,
                "taxCalculated": tax_amount,
                "taxName": "MO CITY TAX",
                "taxOverride": 0.0,
                "taxRegionId": 2078034,
                "taxSubTypeId": "S",
                "taxType": "Sales",
                "taxTypeGroupId": "SalesAndUse",
                "taxableAmount": subtotal,
                "taxableUnits": subtotal,
                "transactionId": 85600959974165,
                "transactionLineId": 85600959974171,
                "unitOfBasis": "PerCurrencyUnit",
            },
        ],
        "discountAmount": product_data.get("discount_amount"),
        "discountTypeId": 0,
        "entityUseCode": "",
        "exemptAmount": product_data.get("exemption_amount", 0.0),
        "exemptCertId": 90867213,
        "exemptNo": "",
        "hsCode": "",
        "id": 85600959974171,
        "isItemTaxable": False,
        "isSSTP": False,
        "itemCode": "MPC",
        "lineAmount": subtotal,
        "lineLocationTypes": [
            {
                "documentAddressId": 85600959974167,
                "documentLineId": 85600959974171,
                "documentLineLocationTypeId": 85600959974174,
                "locationTypeCode": "ShipFrom",
            },
            {
                "documentAddressId": 85600959974166,
                "documentLineId": 85600959974171,
                "documentLineLocationTypeId": 85600959974175,
                "locationTypeCode": "ShipTo",
            },
        ],
        "lineNumber": f"{product_data.get('line_id')}",
        "nonPassthroughDetails": [],
        "originAddressId": 85600959974167,
        "quantity": product_data.get("quantity"),
        "ref1": "",
        "ref2": "",
        "reportingDate": "2024-09-17",
        "revAccount": "",
        "sourcing": "Origin",
        "tax": tax_amount,
        "taxCalculated": tax_amount,
        "taxCode": "PA020122",
        "taxCodeId": 71096,
        "taxDate": "2024-09-17",
        "taxEngine": "",
        "taxIncluded": False,
        "taxOverrideAmount": 0.0,
        "taxOverrideReason": "",
        "taxOverrideType": "None",
        "taxableAmount": subtotal,
        "transactionId": 85600959974165,
        "vatCode": "",
        "vatNumberTypeId": 0,
    }
    return subtotal, tax_amount, res


def mock_response(product_data_list):
    """
    Mock to simulate avalara answer, it's only a standard compute
    Keyword arguments:
        product_data_list -- List of dict with:
            - product (browse record)
            - quantity
            - price_unit
            - discount_amount
            - exemption_amount
            - rate_expected
            - line_id (invoice line id)
    Return:
        Dict with mocked response
    """
    lines_data = [_mock_line(product_data) for product_data in product_data_list]
    subtotal = sum(line[0] for line in lines_data)
    tax_amount = sum(line[1] for line in lines_data)
    lines_data = [line[2] for line in lines_data]
    res = {
        "addresses": [
            {
                "boundaryLevel": "Zip5",
                "city": "Hale",
                "country": "US",
                "id": 85600941773548,
                "line1": "0000 E State Rd",
                "line2": "",
                "line3": "",
                "postalCode": "00000-0000",
                "region": "MI",
                "taxRegionId": 1056912,
                "transactionId": 85600941773547,
            },
            {
                "boundaryLevel": "Address",
                "city": "Blairsville",
                "country": "US",
                "id": 85600941773549,
                "latitude": "0.000000",
                "line1": "000 Kendall Rd",
                "line2": "",
                "line3": "",
                "longitude": "0.000000",
                "postalCode": "00000-0000",
                "region": "PA",
                "taxRegionId": 4012044,
                "transactionId": 85600941773547,
            },
        ],
        "adjustmentDescription": "",
        "adjustmentReason": "NotAdjusted",
        "apStatus": None,
        "apStatusCode": None,
        "batchCode": "",
        "businessIdentificationNo": "",
        "code": "INV/2024/09/1482",
        "companyId": 951445,
        "country": "US",
        "currencyCode": "USD",
        "customerCode": "CC-000000:0",
        "customerUsageType": "",
        "customerVendorCode": "CC-000000:0",
        "date": "2024-09-17",
        "description": "INV/2024/09/1482",
        "destinationAddressId": 85600941773548,
        "email": "",
        "entityUseCode": "",
        "exchangeRate": 1.0,
        "exchangeRateCurrencyCode": "USD",
        "exchangeRateEffectiveDate": "2024-09-17",
        "exemptNo": "",
        "id": 85600941773547,
        "lines": lines_data,
        "locationCode": "",
        "locationTypes": [
            {
                "documentAddressId": 85600941773549,
                "documentId": 85600941773547,
                "documentLocationTypeId": 85600941773551,
                "locationTypeCode": "ShipFrom",
            },
            {
                "documentAddressId": 85600941773548,
                "documentId": 85600941773547,
                "documentLocationTypeId": 85600941773552,
                "locationTypeCode": "ShipTo",
            },
        ],
        "locked": False,
        "modifiedDate": "2024-09-17T20:56:39.7321524Z",
        "modifiedUserId": 1094294,
        "originAddressId": 85600941773549,
        "purchaseOrderNo": "",
        "reconciled": False,
        "referenceCode": "",
        "region": "MI",
        "reportingLocationCode": "",
        "salespersonCode": "Jimmy Dunmire",
        "softwareVersion": "24.8.0.0",
        "status": "Committed",
        "summary": [
            {
                "country": "US",
                "exemption": 0.0,
                "jurisCode": "26",
                "jurisName": "MICHIGAN",
                "jurisType": "State",
                "nonTaxable": 0.0,
                "rate": 0.06,
                "rateType": "General",
                "region": "MI",
                "stateAssignedNo": "",
                "tax": tax_amount,
                "taxAuthorityType": 45,
                "taxCalculated": tax_amount,
                "taxName": "MI STATE TAX",
                "taxSubType": "S",
                "taxType": "Sales",
                "taxable": subtotal,
            }
        ],
        "taxDate": "2024-09-17",
        "taxOverrideAmount": 0.0,
        "taxOverrideReason": "",
        "taxOverrideType": "None",
        "totalAmount": subtotal,
        "totalDiscount": 0.0,
        "totalExempt": 0.0,
        "totalTax": tax_amount,
        "totalTaxCalculated": tax_amount,
        "totalTaxable": subtotal,
        "type": "SalesInvoice",
        "version": 1,
    }
    return res
