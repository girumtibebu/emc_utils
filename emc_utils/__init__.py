__version__ = "1.2.3"

# Initialize monkey patches
try:
    from emc_utils.sections.sections import patch_all
    patch_all()
except Exception:
    pass
