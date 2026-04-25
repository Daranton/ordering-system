import argparse
import sys
from pathlib import Path

from src.utils.ids import generate_order_id
from src.utils.models import Order, OrderStatus, load_orders, save_orders

DATA_FILE = Path(__file__).parent.parent / "data" / "orders.json"


def cmd_create(args: argparse.Namespace) -> None:
    orders = load_orders(DATA_FILE)
    order_id = generate_order_id()
    order = Order(
        order_id=order_id,
        customer=args.customer,
        item=args.item,
        quantity=args.quantity,
    )
    orders[order_id] = order
    save_orders(DATA_FILE, orders)
    print(f"Created order {order_id}")


def cmd_list(args: argparse.Namespace) -> None:
    orders = load_orders(DATA_FILE)
    if not orders:
        print("No orders found.")
        return
    if args.status:
        try:
            status_filter: OrderStatus | None = OrderStatus(args.status.lower())
        except ValueError:
            print(f"Unknown status '{args.status}'. Valid values: {[s.value for s in OrderStatus]}", file=sys.stderr)
            sys.exit(1)
    else:
        status_filter = None
    shown = 0
    for order in orders.values():
        if status_filter and order.status != status_filter:
            continue
        print(f"  {order.order_id}  customer={order.customer}  item={order.item}  qty={order.quantity}  status={order.status}")
        shown += 1
    if shown == 0:
        print(f"No orders with status '{args.status}'.")


def cmd_get(args: argparse.Namespace) -> None:
    orders = load_orders(DATA_FILE)
    order = orders.get(args.order_id)
    if order is None:
        print(f"Order '{args.order_id}' not found.", file=sys.stderr)
        sys.exit(1)
    print(order)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ordering system CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_p = subparsers.add_parser("create", help="Create a new order")
    create_p.add_argument("--customer", required=True, help="Customer name")
    create_p.add_argument("--item", required=True, help="Item name")
    create_p.add_argument("--quantity", type=int, required=True, help="Quantity")

    list_p = subparsers.add_parser("list", help="List orders")
    list_p.add_argument("--status", help="Filter by status (e.g. pending, shipped)")

    get_p = subparsers.add_parser("get", help="Get a single order by ID")
    get_p.add_argument("order_id", help="Order ID")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)


if __name__ == "__main__":
    main()
