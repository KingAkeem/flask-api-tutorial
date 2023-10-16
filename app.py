from flask import Flask, request
from db import stores, items
from uuid import uuid4
from http import HTTPStatus
from flask_smorest import abort

app = Flask(__name__)

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
    except ValueError:
        return False


@app.get("/store")
def get_stores() -> (dict, HTTPStatus):
    return {"stores": list(stores.values())}, HTTPStatus.OK


@app.get("/item")
def get_all_items() -> (dict, HTTPStatus):
    return {"items": list(items.values())}, HTTPStatus.OK


@app.post("/store")
def create_store() -> (dict, HTTPStatus):
    store_data = request.get_json()
    if 'name' not in store_data:
        abort(HTTPStatus.BAD_REQUEST, message='Ensure name is included in the JSON payload.')

    for store in stores.values():
        name = store_data['name']
        if name == store['name']:
            abort(HTTPStatus.BAD_REQUEST, message='Store already exists.')

    store_id = uuid4().hex
    store = {**store_data, 'id': store_id}
    stores[store_id] = store
    return store, HTTPStatus.CREATED


@app.post("/item")
def create_item() -> (dict, HTTPStatus):
    item_data = request.get_json()

    try:
        if not valid_new_item(item=item_data):
            abort(HTTPStatus.BAD_REQUEST, message='Invalid item found.')
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, message=str(e))

    name = item_data['name']
    store_id = item_data['store_id']

    if store_id not in stores:
        abort(HTTPStatus.BAD_REQUEST, message="Store does not exist.")
    
    for item in items.values():
        if name == item['name'] and store_id == item['store_id']:
            abort(HTTPStatus.BAD_REQUEST, message='Item already exists.')  

    item_id = uuid4().hex
    item = {**item_data, "id": item_id}
    items[item_id] = item
    return item, HTTPStatus.CREATED


@app.get("/store/<string:store_id>")
def get_store(store_id: str) -> (dict, HTTPStatus):
    try:
        return stores[store_id]
    except KeyError:
        abort(HTTPStatus.NOT_FOUND, "Store not found")


@app.get('/item/<string:item_id>')
def get_item(item_id: str) -> (dict, HTTPStatus):
    try:
        return items[item_id]
    except KeyError:
        abort(HTTPStatus.NOT_FOUND, "Item not found")


@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message": "Item deleted."}
    except KeyError:
        abort(HTTPStatus.NOT_FOUND, message="Item not found.")


@app.put("/item/<string:item_id>")
def update_item(item_id):
    item_data = {**request.get_json()}
    try:
        if not valid_update_item(item=item_data):
            abort(HTTPStatus.BAD_REQUEST, message='Invalid item found.')
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, message=str(e))


    if 'store_id' in item_data and item_data['store_id'] not in stores:
        abort(HTTPStatus.BAD_REQUEST, message="Store does not exist.")
    
    try:
        item = items[item_id]
        item |= item_data

        return item
    except KeyError:
        abort(HTTPStatus.NOT_FOUND, message="Item not found.")
