from __future__ import unicode_literals
from frappe.model.document import Document
import frappe


class ApplicableTableConfig(Document):
	def validate(self):
		tc = frappe.db.get("Table Config", self.table_config)
		self.table_name = tc.table_name
		self.capacity = tc.capacity
		self.preferred_area = tc.preferred_area
