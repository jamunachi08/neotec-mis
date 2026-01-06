frappe.query_reports["Neotec MIS Report"] = {
  "filters": [
    {"fieldname":"company","label":"Company","fieldtype":"Link","options":"Company","reqd":1},
    {"fieldname":"format","label":"Report Format","fieldtype":"Link","options":"MIS Report Format","reqd":1},
    {"fieldname":"from_date","label":"From Date","fieldtype":"Date","reqd":1},
    {"fieldname":"to_date","label":"To Date","fieldtype":"Date","reqd":1},
    {"fieldname":"cost_center","label":"Cost Center","fieldtype":"Link","options":"Cost Center"},
    {"fieldname":"project","label":"Project","fieldtype":"Link","options":"Project"},
    {"fieldname":"finance_book","label":"Finance Book","fieldtype":"Link","options":"Finance Book"}
  ]
};
