from emc_utils.constants import SCOPED_DOCTYPES

app_name = "emc_utils"
app_title = "EMC Utilities"
app_publisher = "emc"
app_description = "Company switcher, child table sections, print enhancements, and desk tools"
app_email = "girum@eternal-media.com"
app_license = "mit"

required_apps = ["erpnext"]

app_include_js = [
    "/assets/emc_utils/js/emc_utils.js",
    "/assets/emc_utils/js/company_switcher.js",
]
app_include_css = "/assets/emc_utils/css/emc_utils.css"

doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Order": "public/js/sales_order.js",
}

boot_session = "emc_utils.sections.boot_session"

# Company scope list query conditions
_condition = "emc_utils.company_scope.get_permission_query_conditions"
permission_query_conditions = {doctype: _condition for doctype in SCOPED_DOCTYPES}
permission_query_conditions["*"] = _condition

after_install = "emc_utils.setup.after_install"
after_migrate = "emc_utils.setup.after_migrate"

doc_events = {
    "*": {
        "before_validate": "emc_utils.sections.before_validate_sections",
    }
}

jinja = {
    "methods": [
        "emc_utils.sections.is_section_row",
    ]
}
