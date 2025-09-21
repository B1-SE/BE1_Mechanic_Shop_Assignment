"""
Schemas package for the mechanic shop application.
"""

from .customer import CustomerSchema, customer_schema, customers_schema
from .mechanic import MechanicSchema, mechanic_schema, mechanics_schema
from .service_ticket import ServiceTicketSchema, service_ticket_schema, service_tickets_schema
from .inventory import InventoryItemSchema, inventory_item_schema, inventory_items_schema
from .member import MemberSchema, member_schema, members_schema

__all__ = [
    'CustomerSchema', 'customer_schema', 'customers_schema',
    'MechanicSchema', 'mechanic_schema', 'mechanics_schema',
    'ServiceTicketSchema', 'service_ticket_schema', 'service_tickets_schema',
    'InventoryItemSchema', 'inventory_item_schema', 'inventory_items_schema',
    'MemberSchema', 'member_schema', 'members_schema'
]