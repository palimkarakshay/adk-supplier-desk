"""Fixture data for a fictional assembly plant. Nothing here is real customer data."""

SUPPLIERS = {
    "S-1042": "Kestrel Stamping",
    "S-2077": "Orchard Plastics",
}

ORDERS = {
    "SA-55001": {"supplier_id": "S-1042", "part": "Bracket, rear door LH", "qty_open": 4800,
                 "next_delivery": "2026-11-19", "status": "firm", "dock": "D4"},
    "SA-55002": {"supplier_id": "S-1042", "part": "Hinge reinforcement", "qty_open": 1200,
                 "next_delivery": "2026-11-24", "status": "forecast", "dock": "D4"},
    "SA-61010": {"supplier_id": "S-2077", "part": "Console bezel", "qty_open": 900,
                 "next_delivery": "2026-11-18", "status": "firm", "dock": "D2"},
}

ASNS = [
    {"asn": "ASN-90311", "order_id": "SA-55001", "supplier_id": "S-1042", "qty": 2400,
     "shipped": "2026-11-15", "state": "in transit"},
    {"asn": "ASN-90340", "order_id": "SA-55001", "supplier_id": "S-1042", "qty": 2400,
     "shipped": None, "state": "not sent, due 2026-11-18 14:00"},
    {"asn": "ASN-88102", "order_id": "SA-61010", "supplier_id": "S-2077", "qty": 900,
     "shipped": "2026-11-16", "state": "received"},
]

POLICY = [
    {"id": "P1", "title": "ASN timing",
     "text": "An advance ship notice (ASN) must be sent by EDI 856 no later than 30 minutes after the truck leaves "
             "the supplier dock. A shipment that arrives without an ASN is held at the gate until the ASN is received."},
    {"id": "P2", "title": "Late or missing ASN chargeback",
     "text": "A late or missing ASN is charged at 150 CAD per shipment. The charge is waived for the first occurrence "
             "in a calendar quarter if the supplier files a corrective action within 5 business days."},
    {"id": "P3", "title": "Firm and forecast windows",
     "text": "Schedule lines inside 10 business days are firm and cannot be changed by the supplier. Lines beyond 10 "
             "business days are forecast and may change with each weekly EDI 830 release."},
    {"id": "P4", "title": "Labels and packaging",
     "text": "Every container needs a master label with part number, quantity, supplier code and the ASN number as a "
             "barcode. Returnable containers must be used for all firm lines. Expendable packaging needs written "
             "approval from the plant packaging group."},
    {"id": "P5", "title": "Invoice disputes",
     "text": "A price or quantity dispute must be raised within 45 days of the invoice date. Disputes are reviewed "
             "against the goods receipt and the ASN quantity. Payment terms stay net 60 while a dispute is open."},
    {"id": "P6", "title": "Short shipments",
     "text": "A supplier that expects to ship short on a firm line must tell the plant at least 24 hours before the "
             "delivery window. Expedited freight caused by a short shipment is paid by the supplier."},
]
