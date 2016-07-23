frappe.views.calendar["Table Booking"] = {
	field_map: {
		"start": "booking_date",
		"end": "booking_date",
		"id": "name",
		"title": "name",
		"allDay": "allDay"
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "outlet",
			"options": "Outlet Config",
			"label": __("Outlet")
		},
		{
			"fieldtype": "Link",
			"fieldname": "table",
			"options": "Table Config",
			"label": __("Table")
		}
	],
	get_events_method: "table_booking.table_booking.doctype.table_booking.table_booking.get_events",
	get_css_class: function(data) {
		if(data.status=="Draft") {
			return "primary";
		} else if(data.status=="Awaiting Approval") {
			return "primary";
		} else if(data.status=="Not Approved") {
			return "danger";
		} else if(data.status=="Approved") {
			return "success";
		} else if(data.status=="Cancelled") {
			return "danger";
		}
	}
}
