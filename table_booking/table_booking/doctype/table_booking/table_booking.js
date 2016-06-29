
cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  	if(!doc.__islocal && doc.docstatus==1 && doc.status == "Submitted") {
		cur_frm.add_custom_button(__('Decline'),
			function() {
				cur_frm.call({
					freeze: true,
					doc: cur_frm.doc,
					method: "decline",
					callback: function(r) {
						if(!r.exc) {
							cur_frm.reload_doc();
							cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>We are sorry to notify you, your table reservation was declined.</h5>");
						}
					}
				});
			}
		).addClass("btn-danger");

		cur_frm.add_custom_button(__('Approve'),
			function() {
				frappe.call({
					type: "GET",
					method: "table_booking.table_booking.doctype.table_booking.table_booking.get_vacant_table",
					args: {
						table_booking: cur_frm.doc.name
					},
					callback: function(r) {
						if (!r.exc) {
							var table_config = r.message;
							if(!table_config) {
								frappe.msgprint("Cannot find a vacant table for this Booking Table")
								return;
							}
							var d = new frappe.ui.Dialog({
						        title: __("Approve the table reservation"),
						        fields: [
									{
										fieldname: "table_config",
										fieldtype: "Link",
										options: "Table Config",
										default: table_config
									}
						        ]
						    });
						    d.set_primary_action(__("Approve"), function() {
						    	var values = d.get_values();
			                    if(!values) {
			                        return;
			                    }
						        d.hide();

								cur_frm.doc.booked_table = values.table_config;
								cur_frm.call({
									freeze: true,
									doc: cur_frm.doc,
									method: "approve",
									callback: function(r) {
										if(!r.exc && r.message) {
											cur_frm.reload_doc();
											cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>Your table reservation was approved. Your table is " + r.message.table_name + "</h5>");
										}
									}
								});
						    });
						    d.show();
						}
					}
				});
			}
		).addClass("btn-success");
	}
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	cur_frm.reload_doc();
}
