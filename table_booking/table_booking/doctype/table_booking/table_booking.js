cur_frm.cscript.onload_post_render = function(doc, cdt, cdn) {
	cur_frm.page.wrapper.find("input[data-fieldname='reservation_start_time']").removeClass("hasDatepicker").timepicker({
        timeFormat: 'HH:mm',
        stepMinute: 30,
    });
	cur_frm.page.wrapper.find("input[data-fieldname='reservation_end_time']").removeClass("hasDatepicker").timepicker({
        timeFormat: 'HH:mm',
        stepMinute: 30,
    });
}

cur_frm.cscript.refresh = function(doc, cdt, cdn) {
  	if(!doc.__islocal && doc.docstatus==1 && (doc.status === "Awaiting Approval" || doc.status === "Submitted" || doc.status === "Draft")) {
		cur_frm.add_custom_button(__('Decline'),
			function() {
				cur_frm.call({
					freeze: true,
					doc: cur_frm.doc,
					method: "decline",
					callback: function(r) {
						if(!r.exc) {
							cur_frm.reload_doc();
							cur_frm.cscript.send_decline_email();
						}
					}
				});
			}
		).addClass("btn-danger");

		cur_frm.add_custom_button(__('Approve'),
			function() {
				cur_frm.call({
					freeze: true,
					doc: cur_frm.doc,
					method: "approve",
					callback: function(r) {
						if(!r.exc) {
							if(r.message && r.message.success) {
								cur_frm.reload_doc();
								cur_frm.cscript.send_approve_email();
							} else {

							}
						}
					}
				});
			}
		).addClass("btn-success");
	}
}

cur_frm.cscript.send_decline_email = function() {
	cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>We are sorry to notify you, your table reservation was declined.</h5>");
}

cur_frm.cscript.send_approve_email = function(table_details) {
	var booked_tables = cur_frm.doc.booked_tables || [];
	if(booked_tables.length == 1) {
		cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>Your table reservation was approved. Your booked table is: " + booked_tables[0].table_name + "</h5>");
	} else if(booked_tables.length > 1) {
		var table_names = booked_tables[0].table_name;
		for(var i = 1; i < booked_tables.length; i++) {
			table_names += ", " + booked_tables[i].table_name;
		}
		cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>Your table reservation was approved. Your booked tables are: " + table_names + "</h5>");
	}
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	cur_frm.reload_doc();
	var fields = [
        {
            fieldname:"decline-btn",
            fieldtype:"HTML",
            options: "<div style=\"padding-top: 20px;\"><button id=\"decline-btn\" type=\"button\" class=\"btn btn-danger btn-block\">Decline</button></div>"
        },
        {fieldtype:"Column Break"},
        {
            fieldname:"approve-btn",
            fieldtype:"HTML",
            options: "<div style=\"padding-top: 20px;\"><button id=\"approve-btn\" type=\"button\" class=\"btn btn-success btn-block\">Approve</button></div>"
        }
    ];
    var d = new frappe.ui.Dialog({
        fields: fields,
        title: __("Approve or Decline the table reservation"),
    });

    d.$wrapper.on("click", "#decline-btn", function() {
        d.hide();
		cur_frm.call({
			freeze: true,
			doc: cur_frm.doc,
			method: "decline",
			callback: function(r) {
				if(!r.exc) {
					cur_frm.reload_doc();
					cur_frm.cscript.send_decline_email();
				}
			}
		});
    });

    d.$wrapper.on("click", "#approve-btn", function() {
        d.hide();
		cur_frm.call({
			freeze: true,
			doc: cur_frm.doc,
			method: "approve",
			callback: function(r) {
				if(!r.exc) {
					if(r.message && r.message.success) {
						cur_frm.reload_doc();
						cur_frm.cscript.send_approve_email();
					} else {

					}
				}
			}
		});
    });
    d.show();
}
