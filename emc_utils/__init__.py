__version__ = "1.2.7"

# Initialize monkey patches
try:
    from emc_utils.sections.sections import patch_all
    patch_all()
except Exception:
    pass
