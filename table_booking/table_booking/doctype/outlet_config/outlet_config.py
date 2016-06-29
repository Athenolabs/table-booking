from __future__ import unicode_literals
from frappe.model.document import Document

from frappe.utils import flt, get_datetime, get_time
import frappe


class OutletConfig(Document):
	def validate(self):
		for tc in self.tables:
			tc.validate()

		for tbd in self.table_booking_days:
			tbd.validate()
