from flask import Blueprint, request
from app.controllers.product_controller import (
    list_products,
    get_product,
    create_product,
    edit_product,
    delete_product,
    search_products,
    get_seller_products
)

product = Blueprint('product', __name__)

@product.route('/products')
def products_list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    return list_products(page=page, category=category)

@product.route('/product/<int:product_id>')
def product_detail(product_id):
    return get_product(product_id)

@product.route('/product/create', methods=['GET', 'POST'])
def product_create():
    return create_product()

@product.route('/product/<int:product_id>/edit', methods=['GET', 'POST'])
def product_edit(product_id):
    return edit_product(product_id)

@product.route('/product/<int:product_id>/delete', methods=['POST'])
def product_delete(product_id):
    return delete_product(product_id)

@product.route('/products/search')
def product_search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    return search_products(query, page)

@product.route('/seller/<int:seller_id>/products')
def seller_products(seller_id):
    page = request.args.get('page', 1, type=int)
    return get_seller_products(seller_id, page)