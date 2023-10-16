def valid_update_item(item: dict) -> bool:
    required_keys = ['price', 'name']
    all_keys = [*required_keys, 'store_id', 'item_id']

    # check for invalid keys within the item
    for key in item.keys():
        if key not in all_keys:
            raise Exception('Invalid item key found.')

    # ensure required keys are found
    found_required = False
    for key in required_keys:
        if key in item:
            found_required = True
            break
    
    # a single required argument is found
    if not found_required:
        raise Exception(f'Missing required key for item, {key}')
    
    # validate price
    if 'price' in item and not valid_price(price=item['price']):
        price = item['price']
        raise Exception(f'Invalid price found. Price: {price}')
    
    return True


def valid_new_item(item: dict) -> bool:
    required_keys = ['price', 'name']
    all_keys = [*required_keys, 'store_id', 'item_id']

    # check for invalid keys within the item
    for key in item.keys():
        if key not in all_keys:
            raise Exception('Invalid item key found.')

    # ensure required keys are found
    for key in required_keys:
        if key not in item:
            raise Exception(f'Missing required key for item, {key}')
    
    # validate price
    price = item['price']
    if not valid_price(price=price):
        raise Exception(f'Invalid price found. Price: {price}')
    
    return True
    

def valid_price(price: float) -> bool:
    try:
        if float(price) < 0:
            return False
        return True
    except (ValueError, TypeError):
        return False
