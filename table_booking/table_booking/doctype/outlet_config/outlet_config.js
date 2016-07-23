cur_frm.cscript.tables_on_form_rendered = function(doc, cdt, cdn){
	cur_frm.page.wrapper.find("input[data-fieldname='start_time']").removeClass("hasDatepicker").timepicker({
        timeFormat: 'HH:mm',
        stepMinute: 30,
    });
	cur_frm.page.wrapper.find("input[data-fieldname='end_time']").removeClass("hasDatepicker").timepicker({
        timeFormat: 'HH:mm',
        stepMinute: 30,
    });
}
