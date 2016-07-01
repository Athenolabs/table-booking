from __future__ import unicode_literals
from frappe.model.document import Document


class OutletConfig(Document):
	def validate(self):
		for tc in self.tables:
			tc.validate()
