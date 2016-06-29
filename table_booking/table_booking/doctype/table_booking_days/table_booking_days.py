from __future__ import unicode_literals
from frappe.model.document import Document

from frappe.utils import cstr, cint, flt, get_datetime, get_time
import frappe


class TableBookingDays(Document):
	def validate(self):
		for c in cstr(self.days_of_week):
			if c not in " ,1234567":
				frappe.throw("Days of week can be in range between 1 and 7")

		start_time = get_time(self.start_time).replace(second=0)
		end_time = get_time(self.end_time).replace(second=0)

		if start_time.minute % 30 or end_time.minute % 30:
			frappe.throw("Start Time and End Time of Table Booking Days should be a multiple of 30 minutes")

		self.start_time = cstr(start_time)
		self.end_time = cstr(end_time)
