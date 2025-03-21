from .base import BaseAPIModelStub

from .lot_questions_response import LotQuestionsResponseStub
from .supplier import CENTRAL_DIGITAL_PLATFORM_DATA


class SupplierFrameworkStub(BaseAPIModelStub):
    resource_name = "frameworkInterest"
    default_data = {
        "agreementId": None,
        "agreementPath": None,
        "agreementReturned": False,
        "agreementReturnedAt": None,
        "agreementStatus": None,
        "allowDeclarationReuse": True,
        "applicationCompanyDetailsConfirmed": None,
        "countersigned": False,
        "countersignedAt": None,
        "countersignedDetails": None,
        "countersignedPath": None,
        "frameworkFamily": "g-cloud",
        "frameworkFramework": "g-cloud",
        "frameworkSlug": "g-cloud-13",
        "onFramework": False,
        "prefillDeclarationFromFrameworkSlug": None,
        "supplierId": 886665,
        "supplierName": "Kev's Pies",
        "lotQuestionsResponsesStatus": "not_required",
        "agreementVersion": "standard",
        "centralDigitalPlatformShareCode": None,
    }
    optional_keys = [
        ("supplierId", "supplier_id"),
        ("frameworkSlug", "framework_slug"),
        ("onFramework", "on_framework"),
        ("prefillDeclarationFromFrameworkSlug", "prefill_declaration_from_slug"),
        ("applicationCompanyDetailsConfirmed", "application_company_details_confirmed"),
        ("lotQuestionsResponsesStatus", "lot_questions_responses_status"),
        ("agreementVersion", "agreement_version"),
        ("centralDigitalPlatformShareCode", "central_digital_platform_share_code"),
        ("centralDigitalPlatformData", "central_digital_platform_data"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get("agreed_variations"):
            self.response_data["agreedVariations"] = {
                "1": {
                    "agreedAt": "2018-05-04T16:58:52.362855Z",
                    "agreedUserEmail": "stub@example.com",
                    "agreedUserId": 123,
                    "agreedUserName": "Test user",
                }
            }
        else:
            self.response_data["agreedVariations"] = {}

        if kwargs.get("with_declaration"):
            self.response_data["declaration"] = {
                "nameOfOrganisation": "My Little Company",
                "organisationSize": "micro",
                "primaryContactEmail": "supplier@example.com",
                "status": kwargs.get("declaration_status", "unstarted"),
            }
        else:
            self.response_data["declaration"] = {}

        if kwargs.get("with_lot_responses"):
            self.response_data["lotQuestionsResponses"] = [
                LotQuestionsResponseStub(
                    framework_family=self.response_data["frameworkFamily"],
                    framework_framework=self.response_data["frameworkFramework"],
                    framework_slug=self.response_data["frameworkSlug"],
                    supplier_id=self.response_data["supplierId"],
                    supplier_name=self.response_data["supplierName"],
                ).response()
            ]
            self.response_data["lotQuestionsResponsesStatus"] = kwargs.get(
                "lot_questions_responses_status", "in_progress"
            )
        else:
            self.response_data["lotQuestionsResponses"] = []

        if kwargs.get("with_fvra"):
            self.response_data["fvraFrozenResult"] = kwargs.get(
                "fvra_frozen_result",
                {
                    "fvraRoute": "fvra_default",
                    "fvraResults": [
                        {
                            "CheckDate": "2025-03-20T04:00:00",
                            "DUNS": "123456789",
                            "FVRAStatus": "Pass",
                        },
                    ],
                },
            )
            self.response_data["fvra"] = {
                "nameOfOrganisation": "My Little Company",
                "status": kwargs.get("fvra_status", "in_progress"),
            }
            self.response_data["fvraExpectedResult"] = kwargs.get(
                "fvra_expected_result",
                {
                    "route": "fvra_default",
                    "duns_numbers": ["123456789"],
                },
            )
            self.response_data["fvraCurrentResult"] = {
                "route": self.response_data["fvraFrozenResult"]["fvraRoute"],
                "duns_numbers": sorted(
                    [fvra_result["DUNS"] for fvra_result in self.response_data["fvraFrozenResult"]["fvraResults"]]
                ),
            }
        else:
            self.response_data["fvra"] = {}
            self.response_data["fvraFrozenResult"] = {}
            self.response_data["fvraExpectedResult"] = {
                "route": "not_required",
                "duns_numbers": ["123456789"],
            }
            self.response_data["fvraCurrentResult"] = None

        self.response_data["hasExpectedFvraResult"] = (
            self.response_data["fvraExpectedResult"] == self.response_data["fvraCurrentResult"]
        )

        if kwargs.get("with_agreement"):
            agreement_data = {
                "agreementId": 9876,
                "agreementReturned": True,
                "agreementReturnedAt": "2017-05-17T14:31:27.118905Z",
                "agreementDetails": {
                    "frameworkAgreementVersion": "RM1557ix",
                    "signerName": "A. Nonymous",
                    "signerRole": "The Boss",
                    "uploaderUserId": 443333,
                    "uploaderUserName": "Test user",
                    "uploaderUserEmail": "supplier@example.com",
                },
                "agreementPath": "not/the/real/path.pdf",
                "countersigned": True,
                "countersignedAt": "2017-06-15T08:41:46.390992Z",
                "countersignedDetails": {
                    "approvedByUserId": 123,
                },
                "agreementStatus": "countersigned",
            }
            if kwargs.get("with_users"):
                agreement_data["agreementDetails"].update(
                    {
                        "uploaderUserEmail": "stub@example.com",
                        "uploaderUserName": "Test user",
                    }
                )
                agreement_data["countersignedDetails"].update(
                    {
                        "approvedByUserEmail": "stub@example.com",
                        "approvedByUserName": "Test user",
                    }
                )
            self.response_data.update(agreement_data)
        else:
            self.response_data["agreementDetails"] = {}

        if kwargs.get("with_cdp_data"):
            self.response_data["centralDigitalPlatformShareCode"] = CENTRAL_DIGITAL_PLATFORM_DATA[
                "supplierInformationData"
            ]["form"]["shareCode"]
            self.response_data["supplierInformationData"] = CENTRAL_DIGITAL_PLATFORM_DATA["supplierInformationData"]

        for snakecase_key in [
            "agreed_variations",
            "with_declaration",
            "with_lot_responses",
            "with_fvra",
            "with_agreement",
            "with_users",
            "declaration_status",
            "fvra_status",
            "fvra_frozen_result",
            "fvra_expected_result",
            "with_cdp_data",
        ]:
            if kwargs.get(snakecase_key):
                del self.response_data[snakecase_key]
