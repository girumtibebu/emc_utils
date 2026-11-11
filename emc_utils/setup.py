import frappe
from emc_utils.sections.setup import (
    setup_custom_fields as setup_section_fields,
    setup_property_setters as setup_section_setters,
)
from emc_utils.company_switcher.setup import (
    setup_custom_fields as setup_company_fields,
    get_company_custom_fields,
)
from emc_utils.print_designer.setup import setup_sample_print_formats

def after_install():
    setup_section_fields()
    setup_section_setters()
    setup_company_fields()
    setup_sample_print_formats()

def after_migrate():
    setup_section_fields()
    setup_section_setters()
    setup_company_fields()
    setup_sample_print_formats()

# Re-export functions for backward compatibility
def setup_custom_fields():
    setup_section_fields()
    setup_company_fields()

def setup_property_setters():
    setup_section_setters()
