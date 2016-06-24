
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
				var d = new frappe.ui.Dialog({
			        title: __("Approve the table reservation"),
			        fields: [
						{
	                        fieldname: "table_number",
	                        label: "Table Number",
	                        fieldtype: "Data",
	                        reqd: 1
	                    }
			        ]
			    });
			    d.set_primary_action(__("Approve"), function() {
			    	var values = d.get_values();
                    if(!values) {
                        return;
                    }
			        d.hide();
					
					cur_frm.doc.table_number = values.table_number;
					cur_frm.call({
						freeze: true,
						doc: cur_frm.doc,
						method: "approve",
						callback: function(r) {
							if(!r.exc) {
								cur_frm.reload_doc();
								cur_frm.email_doc("<h5>Hello " + cur_frm.doc.customer_name + ",</h5><br><h5>Your table reservation was approved. Your table number is " + cur_frm.doc.table_number + "</h5>");
							}
						}
					}); 
			    });
			    d.show();
			}
		).addClass("btn-success");
	}
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	cur_frm.reload_doc();
}
