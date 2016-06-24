frappe.views.calendar["Table Booking"] = {
	field_map: {
		"start": "booking_date",
		"end": "booking_date",
		"id": "name",
		"title": "customer_name",
		"allDay": "allDay"
	},
	gantt: true,
	filters: [
		{
			"fieldtype": "Select",
			"fieldname": "outlet_type",
			"options": "Coastes\nBikini Bar\nSand Bar",
			"label": __("Outlet Type")
		},
	],
	get_events_method: "table_booking.table_booking.doctype.table_booking.table_booking.get_events",
	get_css_class: function(data) {
		if(data.status=="Draft") {
			return "warning";
		} else if(data.status=="Submitted") {
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
