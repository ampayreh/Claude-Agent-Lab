"""
CloudCart — Fictional e-commerce data for the Claude Agent Lab.

All customers, orders, and policies are fictional. This data exists
solely to give the lab's agent something concrete to look up via
tool calls.
"""

CUSTOMERS = {
    "CUST-001": {
        "id": "CUST-001",
        "name": "Sarah Chen",
        "email": "sarah.chen@example.com",
        "orders": ["ORD-001", "ORD-006"],
    },
    "CUST-002": {
        "id": "CUST-002",
        "name": "Marcus Johnson",
        "email": "m.johnson@example.com",
        "orders": ["ORD-002", "ORD-007"],
    },
    "CUST-003": {
        "id": "CUST-003",
        "name": "Priya Patel",
        "email": "priya.p@example.com",
        "orders": ["ORD-003", "ORD-008"],
    },
    "CUST-004": {
        "id": "CUST-004",
        "name": "James Wilson",
        "email": "jwilson@example.com",
        "orders": ["ORD-004", "ORD-009"],
    },
    "CUST-005": {
        "id": "CUST-005",
        "name": "Anika Okafor",
        "email": "anika.o@example.com",
        "orders": ["ORD-005", "ORD-010"],
    },
}

ORDERS = {
    "ORD-001": {
        "id": "ORD-001",
        "customer_id": "CUST-001",
        "status": "delivered",
        "items": [
            {"name": "Wireless Keyboard", "category": "electronics", "price": 79.99, "qty": 1},
            {"name": "USB-C Hub", "category": "electronics", "price": 45.00, "qty": 1},
        ],
        "total": 124.99,
        "order_date": "2026-07-15",
        "delivered_date": "2026-07-20",
        "tracking": "TRK-1001-A",
    },
    "ORD-002": {
        "id": "ORD-002",
        "customer_id": "CUST-002",
        "status": "delivered",
        "items": [
            {"name": "Noise-Canceling Headphones", "category": "electronics", "price": 249.99, "qty": 1},
        ],
        "total": 249.99,
        "order_date": "2026-08-01",
        "delivered_date": "2026-08-05",
        "tracking": "TRK-2002-B",
    },
    "ORD-003": {
        "id": "ORD-003",
        "customer_id": "CUST-003",
        "status": "shipped",
        "items": [
            {"name": "Running Shoes", "category": "footwear", "price": 129.95, "qty": 1},
            {"name": "Athletic Socks (3-pack)", "category": "apparel", "price": 18.99, "qty": 2},
        ],
        "total": 167.93,
        "order_date": "2026-08-10",
        "shipped_date": "2026-08-12",
        "tracking": "TRK-3003-C",
        "estimated_delivery": "2026-08-18",
    },
    "ORD-004": {
        "id": "ORD-004",
        "customer_id": "CUST-004",
        "status": "processing",
        "items": [
            {"name": "Standing Desk", "category": "furniture", "price": 599.00, "qty": 1},
        ],
        "total": 599.00,
        "order_date": "2026-08-14",
    },
    "ORD-005": {
        "id": "ORD-005",
        "customer_id": "CUST-005",
        "status": "delivered",
        "items": [
            {"name": "Yoga Mat", "category": "fitness", "price": 39.99, "qty": 1},
            {"name": "Swim Goggles", "category": "swimwear", "price": 24.99, "qty": 1},
        ],
        "total": 64.98,
        "order_date": "2026-07-01",
        "delivered_date": "2026-07-06",
        "tracking": "TRK-5005-E",
    },
    "ORD-006": {
        "id": "ORD-006",
        "customer_id": "CUST-001",
        "status": "processing",
        "items": [
            {"name": "Desk Lamp", "category": "home", "price": 49.99, "qty": 1},
        ],
        "total": 49.99,
        "order_date": "2026-08-15",
    },
    "ORD-007": {
        "id": "ORD-007",
        "customer_id": "CUST-002",
        "status": "cancelled",
        "items": [
            {"name": "Mechanical Keyboard", "category": "electronics", "price": 159.99, "qty": 1},
        ],
        "total": 159.99,
        "order_date": "2026-08-05",
        "cancelled_date": "2026-08-06",
        "cancel_reason": "Customer requested cancellation",
    },
    "ORD-008": {
        "id": "ORD-008",
        "customer_id": "CUST-003",
        "status": "delivered",
        "items": [
            {"name": "Backpack", "category": "accessories", "price": 89.99, "qty": 1},
            {"name": "Water Bottle", "category": "accessories", "price": 24.99, "qty": 1},
        ],
        "total": 114.98,
        "order_date": "2026-06-20",
        "delivered_date": "2026-06-25",
        "tracking": "TRK-8008-H",
    },
    "ORD-009": {
        "id": "ORD-009",
        "customer_id": "CUST-004",
        "status": "shipped",
        "items": [
            {"name": "Monitor Stand", "category": "furniture", "price": 79.99, "qty": 1},
            {"name": "Cable Management Kit", "category": "accessories", "price": 19.99, "qty": 1},
        ],
        "total": 99.98,
        "order_date": "2026-08-11",
        "shipped_date": "2026-08-13",
        "tracking": "TRK-9009-I",
        "estimated_delivery": "2026-08-19",
    },
    "ORD-010": {
        "id": "ORD-010",
        "customer_id": "CUST-005",
        "status": "processing",
        "items": [
            {"name": "Resistance Bands Set", "category": "fitness", "price": 34.99, "qty": 1},
            {"name": "Jump Rope", "category": "fitness", "price": 14.99, "qty": 1},
        ],
        "total": 49.98,
        "order_date": "2026-08-16",
    },
}

POLICIES = {
    "general": {
        "category": "general",
        "return_window_days": 30,
        "condition": "Item must be unused and in original packaging",
        "refund_method": "Original payment method, processed within 5-7 business days",
        "exceptions": "See category-specific policies for electronics and swimwear",
    },
    "electronics": {
        "category": "electronics",
        "return_window_days": 15,
        "condition": "Item must be in original packaging with all accessories",
        "refund_method": "Original payment method, processed within 5-7 business days",
        "note": "Opened electronics may be subject to a 15% restocking fee",
    },
    "swimwear": {
        "category": "swimwear",
        "return_window_days": 0,
        "condition": "Final sale — swimwear cannot be returned for hygiene reasons",
        "refund_method": "N/A",
        "note": "Exchanges for size only, within 14 days, with tags attached",
    },
}
