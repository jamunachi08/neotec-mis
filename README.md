# Neotec MIS Builder (Frappe/ERPNext v15+ & v16+)

Design Excel-like MIS report formats and map each line item to one or more **Flags** (each flag maps to one or more **Accounts**). The report engine reads **GL Entry** and produces Monthly + YTD output.

## Features
- Flags (many-to-many) ↔ Accounts mapping
- Report Formats with Lines (Detail / Header / Total / Subtotal / Percent / Text)
- Line formulas referencing Line Codes
- Monthly columns + YTD in a Script Report
- Optional filters: Cost Center, Project, Finance Book

## Install
```bash
bench get-app https://github.com/<your_org>/neotec-mis
bench --site <site> install-app neotec_mis
bench --site <site> migrate
```

## Use (quick)
1. Assign roles: **Neotec MIS Admin** / **Neotec MIS User**
2. Create **MIS Flag** (map accounts)
3. Create **MIS Report Format** (define lines + formulas)
4. Run **Neotec MIS Report**

## Compatibility
Tested design for Frappe/ERPNext v15 and v16.
