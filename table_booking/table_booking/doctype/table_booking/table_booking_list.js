frappe.listview_settings['Table Booking'] = {
	add_fields: ["customer_name", "status"],
	get_indicator: function(doc) {
		if(doc.status==="Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Approved") {
			return [__("Approved"), "green", "status,=,Approved"];
		} else if(doc.status==="Not Approved") {
			return [__("Not Approved"), "red", "status,=,Not Approved"];
		} else if(doc.status==="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		}
	}
};
