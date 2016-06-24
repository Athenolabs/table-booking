from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe.utils import flt, get_datetime, get_time


class TableBooking(Document):
	def validate(self):
		if get_time(self.reservation_start_time) > get_time(self.reservation_end_time):
			frappe.throw("Reservation Start Time cannot be greater than Reservation End Time")

	def approve(self):
		frappe.db.set_value("Table Booking", self.name, "table_number", self.table_number)
		frappe.db.set_value("Table Booking", self.name, "status", "Approved")
		frappe.clear_cache(doctype='Table Booking')

	def decline(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Not Approved")
		frappe.clear_cache(doctype='Table Booking')

	def on_cancel(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Cancelled")
		frappe.clear_cache(doctype='Table Booking')

	def on_submit(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Submitted")
		frappe.clear_cache(doctype='Table Booking')


@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Table Booking", filters)

	data = frappe.db.sql("""select name, customer_name, booking_date, status
		from `tabTable Booking`
		where (ifnull(booking_date, '0000-00-00')!= '0000-00-00')
				and (booking_date between %(start)s and %(end)s)
				and docstatus <= 2
				{conditions}
		""".format(conditions=conditions), {
			"start": start,
			"end": end
		}, as_dict=True, update={"allDay": 0})
	return data
