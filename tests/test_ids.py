from src.utils.ids import generate_order_id


def test_returns_string() -> None:
    assert isinstance(generate_order_id(), str)


def test_ids_are_unique() -> None:
    ids = {generate_order_id() for _ in range(100)}
    assert len(ids) == 100
