from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Table Booking"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Outlet Config",
					"label": _("Outlet Configs"),
					"description": _("Outlet Config")
				},
				{
					"type": "doctype",
					"name": "Table Booking",
					"label": _("Table Bookings"),
					"description": _("Table Booking")
				},
				{
					"type": "doctype",
					"name": "Event",
					"label": _("Table Booking Calendar"),
					"link": "Calendar/Table Booking",
					"description": _("Table Booking Calendar"),
				},
			]

		},
	]
