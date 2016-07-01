from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe.utils import cstr, getdate, get_time
import json
from datetime import datetime as dt, date as dt_date, timedelta


class TableBooking(Document):
	def validate(self):
		if get_time(self.reservation_start_time) > get_time(self.reservation_end_time):
			frappe.throw("Reservation Start Time cannot be greater than Reservation End Time")

		start_time = get_time(self.reservation_start_time).replace(second=0)
		end_time = get_time(self.reservation_end_time).replace(second=0)

		if start_time.minute % 30 or end_time.minute % 30:
			frappe.throw("Reservation Start Time and Reservation End Time of Table Booking Days should be a multiple of 30 minutes")

		self.reservation_start_time = cstr(start_time)
		self.reservation_end_time = cstr(end_time)

		if self.booked_table:
			self.booked_table_name = frappe.db.get_value("Table Config", self.booked_table, "table_name")
			self.preferred_area = frappe.db.get_value("Table Config", self.booked_table, "preferred_area")

	def approve(self):
		frappe.db.set_value("Table Booking", self.name, "booked_table", self.booked_table)
		if self.booked_table:
			booked_table_name = frappe.db.get_value("Table Config", self.booked_table, "table_name")
			frappe.db.set_value("Table Booking", self.name, "booked_table_name", booked_table_name)

			preferred_area = frappe.db.get_value("Table Config", self.booked_table, "preferred_area")
			frappe.db.set_value("Table Booking", self.name, "preferred_area", preferred_area)

		frappe.db.set_value("Table Booking", self.name, "status", "Approved")
		frappe.clear_cache(doctype='Table Booking')
		return frappe.db.get("Table Config", self.booked_table)

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
def get_vacant_table(table_booking):
	tb_doc = frappe.get_doc("Table Booking", table_booking)
	start_time = get_time(cstr(tb_doc.reservation_start_time))
	end_time = get_time(cstr(tb_doc.reservation_end_time))
	weekday = tb_doc.booking_date.isoweekday()
	if tb_doc.preferred_area:
		tables = frappe.db.sql("""select name, table_name, capacity, days_of_week, start_time, end_time, day_off, day_off_date
			from `tabTable Config` where parent="{parent}" and capacity>={capacity} and preferred_area="{preferred_area}" and days_of_week like "%{weekday}%"
			order by capacity asc""".format(parent=tb_doc.outlet, capacity=tb_doc.no_of_people, preferred_area=tb_doc.preferred_area, weekday=cstr(weekday)), as_dict=1)
	else:
		tables = frappe.db.sql("""select name, table_name, capacity, days_of_week, start_time, end_time, day_off, day_off_date
		from `tabTable Config` where parent="{parent}" and capacity>={capacity} and days_of_week like "%{weekday}%"
		order by capacity asc""".format(parent=tb_doc.outlet, capacity=tb_doc.no_of_people, weekday=cstr(weekday)), as_dict=1)

	found_table = ""
	for t in tables:
		if found_table:
			break

		t_start_time = get_time(cstr(t.start_time))
		t_end_time = get_time(cstr(t.end_time))
		if (start_time < t_start_time or
			start_time > t_end_time or
			end_time > t_end_time or
			(t.day_off and getdate(cstr(t.day_off_date)) == getdate(cstr(tb_doc.booking_date)))):
			continue

		table_bookings = frappe.db.sql("""select name, reservation_start_time, reservation_end_time
			from `tabTable Booking` where docstatus=1 and status="Approved" and booking_date=%s and outlet=%s and booked_table=%s
			order by name asc""", (tb_doc.booking_date, tb_doc.outlet, t.name), as_dict=1)
		for tb in table_bookings:
			tb_start_time = get_time(cstr(tb.reservation_start_time))
			tb_end_time = get_time(cstr(tb.reservation_end_time))
			if ((start_time > tb_start_time and start_time < tb_end_time) or
				(end_time > tb_start_time and end_time < tb_end_time) or
				(start_time == tb_start_time and end_time == tb_end_time)):
				break
		else:
			found_table = t.name
	return found_table


@frappe.whitelist()
def get_events(start, end, filters=None):
	table = None
	if filters:
		filters = json.loads(filters)
		if "table" in filters:
			table = filters.get("table")
			del filters["table"]
		filters = json.dumps(filters)

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Table Booking", filters)
	data = frappe.db.sql("""select name, customer_name, booking_date, status
		from `tabTable Booking`
		where (ifnull(booking_date, '0000-00-00')!= '0000-00-00')
				and (booking_date between %(start)s and %(end)s)
				and docstatus <= 2
				{conditions}
		""".format(conditions=conditions), {"start": start, "end": end}, as_dict=True)
	return data


def error_response(msg):
	return {
		"success": False,
		"error": msg
	}


@frappe.whitelist(allow_guest=True)
def vacant_time_slots():
	request = frappe.local.request

	response_data = {
		"success": True,
		"tables": []
	}

	tables_data = []
	if request.method == "GET":
		frappe.set_user("Administrator")
		import urlparse
		data = frappe._dict(urlparse.parse_qsl(cstr(request.query_string)))

		response_data["booking_date"] = data.booking_date

		weekday = getdate(cstr(data.booking_date)).isoweekday()
		tables = frappe.db.sql("""select name, table_name, capacity, preferred_area, days_of_week, start_time, end_time, day_off, day_off_date
			from `tabTable Config` where parent="{parent}" and capacity>={capacity} and days_of_week like "%{weekday}%"
			order by capacity asc""".format(parent=data.outlet, capacity=data.no_of_people, weekday=cstr(weekday)), as_dict=1)

		for t in tables:
			t_start_time = get_time(cstr(t.start_time))
			t_end_time = get_time(cstr(t.end_time))
			if (t.day_off and getdate(cstr(t.day_off_date)) == getdate(cstr(data.booking_date))):
				continue

			table_bookings = frappe.db.sql("""select name, reservation_start_time, reservation_end_time
				from `tabTable Booking` where docstatus=1 and status="Approved" and booking_date=%s and outlet=%s and booked_table=%s
				order by name asc""", (data.booking_date, data.outlet, t.name), as_dict=1)

			vacant_time_slots = []
			cur_t_start_time = t_start_time
			while cur_t_start_time <= t_end_time:
				next_t_start_time = (dt.combine(dt_date.today(), cur_t_start_time) + timedelta(minutes=30)).time()
				vacant_time_slots.append([cur_t_start_time, next_t_start_time])
				cur_t_start_time = next_t_start_time

			def is_slot_vacant(start_t, end_t, tb_list):
				for tb in tb_list:
					tb_start_time = get_time(cstr(tb.reservation_start_time))
					tb_end_time = get_time(cstr(tb.reservation_end_time))
					if ((start_t >= tb_start_time and start_t < tb_end_time) or
						(end_t > tb_start_time and end_t <= tb_end_time) or
						(start_t == tb_start_time and end_t == tb_end_time)):
						return False
				return True

			vacant_time_slots = [[cstr(v1), cstr(v2)] for v1, v2 in vacant_time_slots if is_slot_vacant(v1, v2, table_bookings)]
			table_data = {
				"name": t.name,
				"table_name": t.table_name,
				"capacity": t.capacity,
				"preferred_area": t.preferred_area,
				"vacant_time_slots": vacant_time_slots
			}
			tables_data.append(table_data)
			continue
	else:
		return error_response("Unsupported HTTP method. Only GET method is supported.")
	response_data["tables"] = tables_data
	return response_data
