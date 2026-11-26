import json
import os
import unittest

from emc_utils.print_designer.blocks import add_print_blocks

DIR = os.path.join(os.path.dirname(__file__), "print_designer")


def _load(name):
	with open(os.path.join(DIR, name), encoding="utf-8") as f:
		return json.load(f)


def _fields(layout):
	return {f.get("fieldname"): f for s in layout["sections"] for c in s["columns"] for f in c["fields"]}


class TestPrintBlocks(unittest.TestCase):
	def test_classic_layout_gets_all_blocks_with_toggles(self):
		fields = _fields(add_print_blocks(_load("quotation_sections.json")))
		self.assertEqual(fields["repeater"]["visible_if"], "not doc.print_without_vat")
		self.assertIn("doc.print_payment_terms", fields["payment_schedule"]["visible_if"])
		self.assertIn("doc.print_terms", fields["terms"]["visible_if"])
		self.assertIn("in_words", fields)

	def test_modern_layout_keeps_its_blocks_and_is_idempotent(self):
		once = add_print_blocks(_load("quotation_modern_sections.json"))
		twice = add_print_blocks(json.loads(json.dumps(once)))
		self.assertEqual(once, twice)
		names = [f.get("fieldname") for s in once["sections"] for c in s["columns"] for f in c["fields"]]
		for name in ("repeater", "in_words", "payment_schedule", "terms"):
			self.assertEqual(names.count(name), 1, name)
		self.assertLess(names.index("payment_schedule"), names.index("terms"))
