from items import valid_price

def test_valid_price() -> None:
    assert valid_price(2.40) == True
    assert valid_price(492) == True
    assert valid_price('dafsd') == False
    assert valid_price(dict()) == False