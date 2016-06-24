# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "table_booking"
app_title = "Table Booking"
app_publisher = "olhonko"
app_description = "Table Booking App"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "olhonko@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/table_booking/css/table_booking.css"
# app_include_js = "/assets/table_booking/js/table_booking.js"

# include js, css files in header of web template
# web_include_css = "/assets/table_booking/css/table_booking.css"
# web_include_js = "/assets/table_booking/js/table_booking.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "table_booking.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "table_booking.install.before_install"
# after_install = "table_booking.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "table_booking.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"table_booking.tasks.all"
# 	],
# 	"daily": [
# 		"table_booking.tasks.daily"
# 	],
# 	"hourly": [
# 		"table_booking.tasks.hourly"
# 	],
# 	"weekly": [
# 		"table_booking.tasks.weekly"
# 	]
# 	"monthly": [
# 		"table_booking.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "table_booking.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "table_booking.event.get_events"
# }

calendars = ["Table Booking"]
