import argparse
import os
import sys

import httpx

BASE_URL = os.environ.get("ORDERING_API_URL", "http://localhost:8000")


def cmd_create(args: argparse.Namespace) -> None:
    payload = {
        "customer_name": args.customer,
        "items": [
            {
                "product_name": args.item,
                "quantity": args.quantity,
                "unit_price": args.unit_price,
            }
        ],
    }
    response = httpx.post(f"{BASE_URL}/orders", json=payload)
    response.raise_for_status()
    data: dict[str, object] = response.json()
    print(f"Created order {data['id']}")


def cmd_list(args: argparse.Namespace) -> None:
    params: dict[str, str] = {}
    if args.status:
        params["status"] = args.status.lower()
    response = httpx.get(f"{BASE_URL}/orders", params=params)
    if response.status_code == 422:
        print(f"Unknown status '{args.status}'.", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()
    orders: list[dict[str, object]] = response.json()
    if not orders:
        print("No orders found.")
        return
    for order in orders:
        print(f"  {order['id']}  customer={order['customer_name']}  status={order['status']}  total={order['total']}")


def cmd_get(args: argparse.Namespace) -> None:
    response = httpx.get(f"{BASE_URL}/orders/{args.order_id}")
    if response.status_code == 404:
        print(f"Order '{args.order_id}' not found.", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()
    print(response.json())


def cmd_update_status(args: argparse.Namespace) -> None:
    response = httpx.patch(
        f"{BASE_URL}/orders/{args.order_id}",
        json={"status": args.status.lower()},
    )
    if response.status_code == 404:
        print(f"Order '{args.order_id}' not found.", file=sys.stderr)
        sys.exit(1)
    if response.status_code == 409:
        data: dict[str, object] = response.json()
        print(f"Cannot update: {data['detail']}", file=sys.stderr)
        sys.exit(1)
    if response.status_code == 422:
        print(f"Unknown status '{args.status}'.", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()
    data = response.json()
    print(f"Updated order {args.order_id} status to '{data['status']}'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ordering system CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_p = subparsers.add_parser("create", help="Create a new order")
    create_p.add_argument("--customer", required=True, help="Customer name")
    create_p.add_argument("--item", required=True, help="Item name")
    create_p.add_argument("--quantity", type=int, required=True, help="Quantity")
    create_p.add_argument("--unit-price", type=float, required=True, dest="unit_price", help="Unit price")

    list_p = subparsers.add_parser("list", help="List orders")
    list_p.add_argument("--status", help="Filter by status (e.g. pending, shipped)")

    get_p = subparsers.add_parser("get", help="Get a single order by ID")
    get_p.add_argument("order_id", help="Order ID")

    update_p = subparsers.add_parser("update", help="Update order status")
    update_p.add_argument("order_id", help="Order ID")
    update_p.add_argument("status", help="New status")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "update":
        cmd_update_status(args)


if __name__ == "__main__":
    main()
