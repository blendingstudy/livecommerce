from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.controllers import cart_controller, payment_controller
from app.forms import AddToCartForm
from flask_wtf import FlaskForm

cart = Blueprint('cart', __name__)

@cart.route('/cart', methods=['GET'])
@login_required
def view_cart():
    cart_items = cart_controller.get_cart_items()
    cart_total = cart_controller.get_cart_total()
    
    update_form = FlaskForm()
    remove_form = FlaskForm()
    clear_form = FlaskForm()
    
    return render_template('cart/view.html', 
                           cart_items=cart_items, 
                           cart_total=cart_total,
                           update_form=update_form,
                           remove_form=remove_form,
                           clear_form=clear_form)

@cart.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    form = AddToCartForm()
    if form.validate_on_submit():
        try:
            product_id = int(form.product_id.data)
            quantity = int(form.quantity.data)
            print(product_id)
            if product_id <= 0 or quantity <= 0:
                raise ValueError("Invalid product_id or quantity")
            success, message = cart_controller.add_to_cart(product_id, quantity)
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
        except ValueError:
            flash('잘못된 입력입니다.', 'error')
    else:
        flash('폼 유효성 검사에 실패했습니다.', 'error')
    return redirect(url_for('product.product_detail', product_id=product_id))



@cart.route('/cart/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    success, message = cart_controller.remove_from_cart(product_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    success, message = cart_controller.update_cart_item(product_id, quantity)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    success, message = cart_controller.clear_cart()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/checkout', methods=['GET'])
@login_required
def checkout():
    cart_items = cart_controller.get_cart_items()
    cart_total = cart_controller.get_cart_total()
    
    if not cart_items:
        flash('장바구니가 비어있습니다.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    order, error =  payment_controller.create_order(cart_items)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('cart.view_cart'))

    return redirect(url_for('payment.checkout', order_id=order.id))

@cart.route('/api/cart', methods=['GET'])
@login_required
def api_get_cart():
    cart_items = cart_controller.get_cart_items()
    cart_total = cart_controller.get_cart_total()
    return jsonify({
        'items': cart_items,
        'total': cart_total
    })

@cart.route('/api/cart/add', methods=['POST'])
@login_required
def api_add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    success, message = cart_controller.add_to_cart(product_id, quantity)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@cart.route('/api/cart/remove', methods=['POST'])
@login_required
def api_remove_from_cart():
    data = request.json
    product_id = data.get('product_id')
    
    success, message = cart_controller.remove_from_cart(product_id)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@cart.route('/api/cart/update', methods=['POST'])
@login_required
def api_update_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    success, message = cart_controller.update_cart_item(product_id, quantity)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400