ACCOUNT_GROUP = {
    "id": 1253,
    "name": "Productos",
    "active": True,
}

TAX = {
    "id": 13156,
    "name": "IVA 19%",
    "type": "IVA",
    "percentage": 19,
    "active": True,
}

PRICE_LIST = {
    "id": 2766,
    "name": "Precio de venta 1",
    "active": True,
    "position": 1,
}

WAREHOUSE = {
    "id": 1270,
    "name": "Bodega principal",
    "active": True,
    "has_movements": True,
}

USERS = {
    "id": 35071,
    "username": "usuario@prueba.com",
    "first_name": "David Felipe",
    "last_name": "Yepes Sánchez",
    "email": "usuario@prueba.com",
    "active": True,
    "identification": "13832082",
}

DOCUMENT_TYPE = {
    "id": 24446,
    "code": "1",
    "name": "Factura",
    "description": "Factura de venta",
    "type": "FV",
    "active": True,
    "seller_by_item": False,
    "cost_center": False,
    "cost_center_mandatory": False,
    "automatic_number": True,
    "consecutive": 3,
    "discount_type": "Percentage",
    "decimals": True,
    "advance_payment": False,
    "reteiva": True,
    "reteica": True,
    "self_withholding": False,
    "self_withholding_limit": 0,
    "electronic_type": "NoElectronic",
    "cargo_transportation": True,
    "healthcare_company": True,
    "customer_by_item": True,
}

PAYMENT_TYPE = {
    "id": 5636,
    "name": "Crédito",
    "type": "Cartera",
    "active": True,
    "due_date": True,
}

COST_CENTER = {
    "id": 25732,
    "code": "13",
    "name": "Principal",
    "active": True,
}

FIXED_ASSETS = {
    "id": 13156,
    "name": "Equipo de oficina",
    "group": "Equipo de computación",
    "active": True,
}

PRODUCT = {
    "id": "00584089-4ebc-49de-bf75-6a6cc968a96d",
    "code": "Item-1",
    "name": "Camiseta de algodón",
    "account_group": {
        "id": 1253,
        "name": "Productos",
    },
    "type": "Product",
    "stock_control": False,
    "active": True,
    "tax_classification": "Taxed",
    "tax_included": False,
    "tax_consumption_value": 0,
    "taxes": [
        {
            "id": 13156,
            "name": "IVA 19%",
            "type": "IVA",
            "percentage": 19.00,
        }
    ],
    "unit_label": "unidad",
    "unit": {
        "code": "94",
        "name": "unidad",
    },
    "reference": "REF1",
    "description": "Camiseta de algodón blanca",
    "additional_fields": {
        "barcode": "B0123",
        "brand": "Gef",
        "tariff": "151612",
        "model": "Loiry",
    },
    "available_quantity": 0,
    "warehouses": [
        {
            "id": 1270,
            "name": "Bodega principal",
            "quantity": 1,
        }
    ],
    "metadata": {
        "created": "2020-06-15T03:33:17.208Z",
        "last_updated": "null",
    },
    "prices": [
        {
            "currency_code": "COP",
            "price_list": [
                {
                    "position": 1,
                    "name": "Precio de venta 1",
                    "value": 12000,
                }
            ],
        }
    ],
}

CUSTOMER = {
    "id": "6b6ceb28-b2eb-4b98-b3dd-26648a933c81",
    "type": "Customer",
    "person_type": "Person",
    "id_type": {
        "code": "13",
        "name": "Cédula de ciudadanía",
    },
    "identification": "13832081",
    "check_digit": "4",
    "name": [
        "Marcos",
        "Castillo",
    ],
    "commercial_name": "Siigo",
    "branch_office": 0,
    "active": True,
    "vat_responsible": True,
    "fiscal_responsibilities": [
        {
            "code": "R-99-PN",
            "name": "No responsable",
        }
    ],
    "address": {
        "address": "Cra. 18 #79A - 42",
        "city": {
            "country_code": "Co",
            "country_name": "Colombia",
            "state_code": "19",
            "state_name": "Cauca",
            "city_code": "19001",
            "city_name": "Popayán",
        },
        "postal_code": "110911",
    },
    "phones": [
        {
            "indicative": "57",
            "number": "3006003345",
            "extension": "132",
        }
    ],
    "contacts": [
        {
            "first_name": "Marcos",
            "last_name": "Castillo",
            "email": "marcos.castillo@contacto.com",
            "phone": {
                "indicative": "57",
                "number": "3006003345",
                "extension": "132",
            },
        }
    ],
    "comments": "Comentarios",
    "related_users": {
        "seller_id": 629,
        "collector_id": 629,
    },
    "metadata": {
        "created": "2020-06-15T03:33:17.208Z",
        "last_updated": "null",
    },
}
