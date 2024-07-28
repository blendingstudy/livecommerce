from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.controllers import product_controller
from app.controllers.product_controller import (
    list_products,
    get_product,
    create_product,
    edit_product,
    delete_product,
    search_products,
    get_seller_products,
    get_discounted_products,
    toggle_favorite
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

@product.route('/discounted')
def discounted_products():
    page = request.args.get('page', 1, type=int)
    discounted_products = get_discounted_products(page)
    return render_template('product/discounted.html', products=discounted_products)

@product.route('/toggle_favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite_route(product_id):
    toggle_favorite(product_id)
    return redirect(url_for('product.product_detail', product_id=product_id))