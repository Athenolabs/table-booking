from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe.utils import cint, cstr, getdate, get_time
import json
from datetime import datetime as dt, date as dt_date, timedelta


class TableBooking(Document):
	def validate(self):
		if not self.booked_tables:
			for bt in get_vacant_tables(self):
				self.append("booked_tables", {
					"doctype": "Applicable Table Config",
					"table_config": bt.name,
					"table_name": bt.table_name,
					"capacity": bt.capacity,
					"preferred_area": bt.preferred_area
				})
		for bt in self.booked_tables:
			bt.validate()

		if get_time(self.reservation_start_time) > get_time(self.reservation_end_time):
			frappe.throw("Reservation Start Time cannot be greater than Reservation End Time")

		start_time = get_time(self.reservation_start_time).replace(second=0)
		end_time = get_time(self.reservation_end_time).replace(second=0)

		if start_time.minute % 30 or end_time.minute % 30:
			frappe.throw("Reservation Start Time and Reservation End Time of Table Booking Days should be a multiple of 30 minutes")

		self.reservation_start_time = cstr(start_time)
		self.reservation_end_time = cstr(end_time)

	def approve(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Approved")
		frappe.clear_cache(doctype='Table Booking')
		return {
			"success": True,
			"error": ""
		}

	def decline(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Not Approved")
		frappe.clear_cache(doctype='Table Booking')

	def on_cancel(self):
		frappe.db.set_value("Table Booking", self.name, "status", "Cancelled")
		frappe.clear_cache(doctype='Table Booking')

	def on_submit(self):
		total_capacity = 0
		for bt in self.booked_tables:
			total_capacity += cint(bt.capacity)
		if total_capacity < cint(self.no_of_people):
			frappe.throw("Total capacity of booked tables is less than the requested No Of People")

		frappe.db.set_value("Table Booking", self.name, "status", "Awaiting Approval")
		frappe.clear_cache(doctype='Table Booking')


@frappe.whitelist()
def get_vacant_tables(table_booking, book_area=False):
	if isinstance(table_booking, basestring):
		table_booking = frappe.get_doc("Table Booking", table_booking)
	start_time = get_time(cstr(table_booking.reservation_start_time))
	end_time = get_time(cstr(table_booking.reservation_end_time))
	weekday = getdate(cstr(table_booking.booking_date)).isoweekday()

	holiday_dates = []
	holiday_lists = [hl.holiday_list for hl in frappe.db.get_all("Applicable Holiday List", fields=["holiday_list"], filters={"parent": table_booking.outlet})]
	for hl in holiday_lists:
		holiday_dates += [getdate(cstr(h.holiday_date)) for h in frappe.db.get_all("Holiday", fields=["holiday_date"], filters={"parent": hl})]

	if table_booking.preferred_area:
		tables = frappe.db.sql("""select name, table_name, capacity, days_of_week, start_time, end_time
			from `tabTable Config` where parent="{parent}" and preferred_area="{preferred_area}" and days_of_week like "%{weekday}%"
			order by capacity desc""".format(parent=table_booking.outlet, preferred_area=table_booking.preferred_area, weekday=cstr(weekday)), as_dict=1)
	else:
		tables = frappe.db.sql("""select name, table_name, capacity, days_of_week, start_time, end_time
			from `tabTable Config` where parent="{parent}" and days_of_week like "%{weekday}%"
			order by capacity desc""".format(parent=table_booking.outlet, weekday=cstr(weekday)), as_dict=1)

	no_of_people = cint(table_booking.no_of_people)
	found_tables = []
	for t in tables:
		t_start_time = get_time(cstr(t.start_time))
		t_end_time = get_time(cstr(t.end_time))
		if (start_time < t_start_time or
			start_time > t_end_time or
			end_time > t_end_time or
			getdate(cstr(table_booking.booking_date)) in holiday_dates):
			continue

		table_bookings = frappe.db.sql("""select name, reservation_start_time, reservation_end_time
			from `tabTable Booking` where docstatus=1 and status="Approved" and booking_date=%s and outlet=%s
			order by name asc""", (table_booking.booking_date, table_booking.outlet), as_dict=1)
		table_bookings = [i for i in table_bookings if frappe.db.get_all("Applicable Table Config", filters={"parent": i.name, "table_config": t.name})]
		for tb in table_bookings:
			tb_start_time = get_time(cstr(tb.reservation_start_time))
			tb_end_time = get_time(cstr(tb.reservation_end_time))
			if ((start_time > tb_start_time and start_time < tb_end_time) or
				(end_time > tb_start_time and end_time < tb_end_time) or
				(start_time == tb_start_time and end_time == tb_end_time)):
				break
		else:
			found_tables.append(t)
			if book_area:
				continue
			no_of_people -= cint(t.capacity)
			if no_of_people <= 0:
				break
	return found_tables


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
	# if table:
	# 	pass

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

		holiday_dates = []
		holiday_lists = [hl.holiday_list for hl in frappe.db.get_all("Applicable Holiday List", fields=["holiday_list"], filters={"parent": data.outlet})]
		for hl in holiday_lists:
			holiday_dates += [getdate(cstr(h.holiday_date)) for h in frappe.db.get_all("Holiday", fields=["holiday_date"], filters={"parent": hl})]

		tables = frappe.db.sql("""select name, table_name, capacity, preferred_area, days_of_week, start_time, end_time
			from `tabTable Config` where parent="{parent}" and days_of_week like "%{weekday}%"
			order by capacity desc""".format(parent=data.outlet, weekday=cstr(weekday)), as_dict=1)

		for t in tables:
			t_start_time = get_time(cstr(t.start_time))
			t_end_time = get_time(cstr(t.end_time))
			if getdate(cstr(data.booking_date)) in holiday_dates:
				continue

			table_bookings = frappe.db.sql("""select name, reservation_start_time, reservation_end_time
				from `tabTable Booking` where docstatus=1 and status="Approved" and booking_date=%s and outlet=%s
				order by name asc""", (data.booking_date, data.outlet), as_dict=1)
			table_bookings = [i for i in table_bookings if frappe.db.get_all("Applicable Table Config", filters={"parent": i.name, "table_config": t.name})]

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


@frappe.whitelist(allow_guest=True)
def outlet_capacity():
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

		holiday_dates = []
		holiday_lists = [hl.holiday_list for hl in frappe.db.get_all("Applicable Holiday List", fields=["holiday_list"], filters={"parent": data.outlet})]
		for hl in holiday_lists:
			holiday_dates += [getdate(cstr(h.holiday_date)) for h in frappe.db.get_all("Holiday", fields=["holiday_date"], filters={"parent": hl})]

		tables = frappe.db.sql("""select name, table_name, capacity, preferred_area, days_of_week, start_time, end_time
			from `tabTable Config` where parent="{parent}" and days_of_week like "%{weekday}%"
			order by table_name asc""".format(parent=data.outlet, weekday=cstr(weekday)), as_dict=1)

		for t in tables:
			t_start_time = get_time(cstr(t.start_time))
			t_end_time = get_time(cstr(t.end_time))
			if getdate(cstr(data.booking_date)) in holiday_dates:
				continue

			table_bookings = frappe.db.sql("""select name, reservation_start_time, reservation_end_time
				from `tabTable Booking` where docstatus=1 and status="Approved" and booking_date=%s and outlet=%s
				order by name asc""", (data.booking_date, data.outlet), as_dict=1)
			table_bookings = [i for i in table_bookings if frappe.db.get_all("Applicable Table Config", filters={"parent": i.name, "table_config": t.name})]

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


@frappe.whitelist()
def get_area_options():
	areas = frappe.db.sql("""select distinct preferred_area
		from `tabTable Config`
		order by preferred_area asc""", as_dict=1)
	return "\n".join([a.preferred_area for a in areas])


@frappe.whitelist()
def book_area(outlet, area, booking_date, start_time, end_time, customer_name, contact_email, customer_mobile, no_of_people, no_of_baby_chairs=None):
	table_booking = frappe.new_doc("Table Booking")
	table_booking.update({
		"outlet": outlet,
		"preferred_area": area,
		"booking_date": booking_date,
		"reservation_start_time": start_time,
		"reservation_end_time": end_time,
		"customer_name": customer_name,
		"contact_email": contact_email,
		"customer_mobile": customer_mobile,
		"no_of_people": no_of_people,
		"no_of_baby_chairs": no_of_baby_chairs
	})

	for bt in get_vacant_tables(table_booking, book_area=True):
		table_booking.append("booked_tables", {
			"doctype": "Applicable Table Config",
			"table_config": bt.name,
			"table_name": bt.table_name,
			"capacity": bt.capacity,
			"preferred_area": bt.preferred_area
		})

	return table_booking.as_dict()
