from ..validation.items import valid_price, valid_new_item, valid_update_item
from random import randrange


def test_valid_price() -> None:
    assert valid_price(2.40) == True
    assert valid_price(492) == True
    assert valid_price("dafsd") == False
    assert valid_price(dict()) == False


def test_valid_new_item() -> None:
    item = {"price": 2.5, "name": "Gum", "store_id": "id"}
    assert valid_new_item(item) == True

    item = {"price": 22.12, "name": "Chair", "store_id": "id"}
    assert valid_new_item(item) == True

    item = {"price": 74, "name": "Ladder", "store_id": "id"}
    assert valid_new_item(item) == True

    item = {"price": randrange(1500), "name": "Random Item", "store_id": "id"}
    assert valid_new_item(item) == True


def test_valid_update_item() -> None:
    assert valid_update_item({"price": 2.5, "name": "Gum"}) == True
    assert valid_update_item({"price": 22.12, "name": "Chair"}) == True
    assert valid_update_item({"price": 74, "name": "Ladder"}) == True

    item = {"price": randrange(1500), "name": "Random Item"}
    assert valid_update_item(item) == True