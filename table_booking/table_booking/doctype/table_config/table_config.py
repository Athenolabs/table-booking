from __future__ import unicode_literals
from frappe.model.document import Document

from frappe.utils import cstr, cint, flt, get_datetime, get_time
import frappe


class TableConfig(Document):
	def validate(self):
		self.table_name = cstr(self.table_name).strip()
		if cint(self.capacity) < 0:
			frappe.msgprint("Table capacity cannot be less than zero")
			self.capacity = 0
