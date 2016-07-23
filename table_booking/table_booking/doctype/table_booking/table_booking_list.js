frappe.listview_settings['Table Booking'] = {
	add_fields: ["customer_name", "status"],
	onload: function(listview) {
		listview.page.add_action_item(__("Book Area"), function() {
			frappe.call({
				type: "GET",
				freeze: true,
				method: "table_booking.table_booking.doctype.table_booking.table_booking.get_area_options",
				callback: function(r) {
					if (!r.exc) {
						var area_options = r.message;
						if(!area_options) {
							frappe.msgprint("Cannot find any area")
							return;
						}

						var fields = [
							{
								fieldname: "outlet",
								fieldtype: "Link",
								label: "Outlet",
								options: "Outlet Config",
								reqd: 1
							},
							{
								fieldname: "area",
								fieldtype: "Select",
								label: "Area",
								options: area_options,
								reqd: 1
							},
					        {fieldtype:"Column Break"},
							{
								fieldname: "booking_date",
								fieldtype: "Date",
								label: "Booking Date",
								reqd: 1
							},
							{
								fieldname: "start_time",
								fieldtype: "Time",
								label: "Start Time",
								reqd: 1
							},
							{
								fieldname: "end_time",
								fieldtype: "Time",
								label: "End Time",
								reqd: 1
							},
					        {fieldtype:"Section Break"},
							{
								fieldname: "customer_name",
								fieldtype: "Data",
								label: "Customer Name",
								reqd: 1
							},
							{
								fieldname: "contact_email",
								fieldtype: "Data",
								label: "Email",
								reqd: 1
							},
							{
								fieldname: "customer_mobile",
								fieldtype: "Data",
								label: "Phone",
								reqd: 1
							},
					        {fieldtype:"Column Break"},
							{
								fieldname: "no_of_people",
								fieldtype: "Int",
								label: "No Of People",
								reqd: 1
							},
							{
								fieldname: "no_of_baby_chairs",
								fieldtype: "Int",
								label: "No Of Baby Chairs",
								reqd: 0
							},
					    ];
					    var d = new frappe.ui.Dialog({
					        fields: fields,
					        title: __("Book Area"),
					    });

					    d.$wrapper.find("input[data-fieldname='start_time']").removeClass("hasDatepicker").timepicker({
					        timeFormat: 'HH:mm',
					        stepMinute: 30,
					    });
					    d.$wrapper.find("input[data-fieldname='end_time']").removeClass("hasDatepicker").timepicker({
					        timeFormat: 'HH:mm',
					        stepMinute: 30,
					    });

					    d.set_primary_action(__("Book"), function() {
					        var values = d.get_values();
					        if(!values) {
					            return;
					        }
					        d.hide();

							return frappe.call({
								freeze: true,
								method: "table_booking.table_booking.doctype.table_booking.table_booking.book_area",
								args: {
									"outlet": values.outlet,
									"area": values.area,
									"booking_date": values.booking_date,
									"start_time": values.start_time,
									"end_time": values.end_time,
									"customer_name": values.customer_name,
									"contact_email": values.contact_email,
									"customer_mobile": values.customer_mobile,
									"no_of_people": values.no_of_people,
									"no_of_baby_chairs": values.no_of_baby_chairs
								},
								callback: function(r) {
									var doclist = frappe.model.sync(r.message);
									frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
								}
							});
					    });

					    d.show();
					}
				}
			});

		});
	},
	get_indicator: function(doc) {
		if(doc.status==="Draft") {
			return [__("Awaiting Approval"), "blue", "status,=,Draft"];
		} else if(doc.status==="Submitted") {
			return [__("Awaiting Approval"), "blue", "status,=,Submitted"];
		} else if(doc.status==="Awaiting Approval") {
			return [__("Awaiting Approval"), "blue", "status,=,Awaiting Approval"];
		} else if(doc.status==="Approved") {
			return [__("Approved"), "green", "status,=,Approved"];
		} else if(doc.status==="Not Approved") {
			return [__("Not Approved"), "red", "status,=,Not Approved"];
		} else if(doc.status==="Cancelled") {
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		}
	}
};
