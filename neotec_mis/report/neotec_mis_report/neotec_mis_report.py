import re
import frappe
from frappe.utils import getdate, add_months, flt

_SAFE_RE = re.compile(r"^[0-9A-Z_+\-*/(). <>=!%]+$")

def _month_start(d):
    d = getdate(d)
    return d.replace(day=1)

def _iter_month_starts(from_date, to_date):
    cur = _month_start(from_date)
    end = _month_start(to_date)
    out = []
    while cur <= end:
        out.append(cur)
        cur = add_months(cur, 1)
    return out

def _sum_gl(company, accounts, from_date, to_date, cost_center=None, project=None, finance_book=None):
    if not accounts:
        return 0.0

    cond = [
        "company=%(company)s",
        "posting_date >= %(from_date)s",
        "posting_date < %(to_date)s",
        "is_cancelled=0",
        "account in %(accounts)s",
    ]
    args = {"company": company, "from_date": from_date, "to_date": to_date, "accounts": tuple(accounts)}

    if cost_center:
        cond.append("cost_center=%(cost_center)s")
        args["cost_center"] = cost_center
    if project:
        cond.append("project=%(project)s")
        args["project"] = project
    if finance_book:
        cond.append("finance_book=%(finance_book)s")
        args["finance_book"] = finance_book

    r = frappe.db.sql(
        f"select sum(credit) as credit, sum(debit) as debit from `tabGL Entry` where {' and '.join(cond)}",
        args,
        as_dict=True
    )[0] or {}

    return flt(r.get("credit")) - flt(r.get("debit"))

def _accounts_for_flags(flags):
    acc = set()
    for f in flags:
        flag_doc = frappe.get_doc("MIS Flag", f)
        for row in (flag_doc.accounts or []):
            if int(row.include or 0) == 1 and row.account:
                acc.add(row.account)
    return sorted(acc)

def _safe_eval(expr, vars_dict):
    e = (expr or "").strip().upper()
    if not e:
        return 0.0
    if not _SAFE_RE.match(e):
        frappe.throw("Unsafe formula. Only line codes and math operators are allowed.")
    safe_locals = {k: flt(v) for k, v in vars_dict.items()}
    return flt(eval(e, {"__builtins__": {}}, safe_locals))

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company")
    fmt_name = filters.get("format")
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    cost_center = filters.get("cost_center")
    project = filters.get("project")
    finance_book = filters.get("finance_book")

    fmt = frappe.get_doc("MIS Report Format", fmt_name)
    lines = sorted(fmt.lines, key=lambda x: (int(x.display_order or 0), x.idx))
    months = _iter_month_starts(from_date, to_date)
    labels = [m.strftime("%b %Y") for m in months]

    columns = [{"fieldname": "line_item", "label": "Line Item", "fieldtype": "Data", "width": 320}]
    for i, lab in enumerate(labels):
        columns.append({"fieldname": f"m{i}", "label": lab, "fieldtype": "Currency", "width": 140})
    columns.append({"fieldname": "ytd", "label": "YTD", "fieldtype": "Currency", "width": 140})

    values = {}
    rows_meta = []

    for ln in lines:
        code = (ln.line_code or "").strip().upper()
        if not code:
            continue

        lt = (ln.line_type or "Detail")
        sign = -1 if (ln.sign or "+") == "-" else 1
        row = {"line_item": ("    " * int(ln.indent or 0)) + (ln.line_title or "")}

        if lt == "Detail":
            flags = [x.flag for x in (ln.flags or []) if x.flag]
            accounts = _accounts_for_flags(flags)

            per = []
            for i, m in enumerate(months):
                start = m
                end = add_months(m, 1)
                v = sign * _sum_gl(company, accounts, start, end, cost_center, project, finance_book)
                row[f"m{i}"] = v
                per.append(v)

            ytd = sign * _sum_gl(company, accounts, from_date, to_date, cost_center, project, finance_book)
            row["ytd"] = ytd

            values[code] = {f"m{i}": per[i] for i in range(len(months))}
            values[code]["ytd"] = ytd

            if int(ln.hide_if_zero or 0) == 1 and abs(ytd) < 0.000001 and all(abs(x) < 0.000001 for x in per):
                continue
        else:
            for i in range(len(months)):
                row[f"m{i}"] = None
            row["ytd"] = None

        rows_meta.append((ln, row))

    data = []
    for ln, row in rows_meta:
        code = (ln.line_code or "").strip().upper()
        lt = (ln.line_type or "Detail")
        formula = (ln.formula or "").strip()

        if lt in ("Total", "Subtotal", "Percent") and formula:
            for i in range(len(months)):
                vars_dict = {k: v.get(f"m{i}", 0.0) for k, v in values.items()}
                row[f"m{i}"] = _safe_eval(formula, vars_dict)

            vars_dict = {k: v.get("ytd", 0.0) for k, v in values.items()}
            row["ytd"] = _safe_eval(formula, vars_dict)

            values[code] = {f"m{i}": row[f"m{i}"] for i in range(len(months))}
            values[code]["ytd"] = row["ytd"]

        data.append(row)

    return columns, data
