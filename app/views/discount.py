from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Discount, Coupon
from app.controllers import discount_controller
from datetime import datetime

from app.models.product import Product

discount = Blueprint('discount', __name__)

@discount.route('/host/discounts')
@login_required
def host_discounts():
    if not current_user.is_seller:
        flash('판매자 권한이 필요합니다.', 'error')
        return redirect(url_for('main.index'))
    
    discounts = Discount.query.filter_by(seller_id=current_user.id).all()
    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template('host/discounts.html', discounts=discounts, products=products)

@discount.route('/host/coupons')
@login_required
def host_coupons():
    if not current_user.is_seller:
        flash('판매자 권한이 필요합니다.', 'error')
        return redirect(url_for('main.index'))
    
    coupons = Coupon.query.filter_by(seller_id=current_user.id).all()
    now = datetime.utcnow()
    return render_template('host/coupons.html', coupons=coupons, now=now)

@discount.route('/coupons', methods=['POST'])
@login_required
def create_coupon():
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    data = request.json
    new_coupon = Coupon(
        code=data['code'],
        discount_type=data['discount_type'],
        discount_value=float(data['discount_value']),
        usage_limit=int(data['usage_limit']),
        expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d'),
        seller_id=current_user.id
    )

    try:
        db.session.add(new_coupon)
        db.session.commit()
        return jsonify({"message": "쿠폰이 성공적으로 생성되었습니다.", "id": new_coupon.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@discount.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    data = request.json
    success, message, discount_amount, final_price = discount_controller.apply_coupon(data['order_id'], data['coupon_code'])

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'discount_amount': f"{discount_amount:,.0f}",
            'final_price': f"{final_price:,.0f}"
        }), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

@discount.route('/discounts/<int:discount_id>', methods=['PUT'])
@login_required
def update_discount(discount_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    data = request.json
    updated_discount = discount_controller.update_discount(discount_id, data)
    if updated_discount:
        return jsonify({"message": "할인이 성공적으로 업데이트되었습니다."}), 200
    else:
        return jsonify({"error": "할인 업데이트에 실패했습니다."}), 400

@discount.route('/discounts/<int:discount_id>', methods=['DELETE'])
@login_required
def delete_discount(discount_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    success = discount_controller.delete_discount(discount_id)
    if success:
        return jsonify({"message": "할인이 성공적으로 삭제되었습니다."}), 200
    else:
        return jsonify({"error": "할인 삭제에 실패했습니다."}), 400

@discount.route('/discount/coupons/<int:coupon_id>', methods=['GET'])
@login_required
def get_coupon(coupon_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    coupon = Coupon.query.get(coupon_id)
    if not coupon or coupon.seller_id != current_user.id:
        return jsonify({"error": "쿠폰을 찾을 수 없습니다."}), 404

    return jsonify({
        "id": coupon.id,
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "usage_limit": coupon.usage_limit,
        "expiration_date": coupon.expiration_date.strftime('%Y-%m-%d')
    })

@discount.route('/discount/coupons/<int:coupon_id>', methods=['PUT'])
@login_required
def update_coupon_route(coupon_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    data = request.json
    
    return discount_controller.update_coupon(coupon_id, data)

@discount.route('/discount/coupons/<int:coupon_id>', methods=['DELETE'])
@login_required
def delete_coupon_route(coupon_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    success, message = discount_controller.delete_coupon(coupon_id)
    if success:
        return jsonify({"message": message}), 200
    else:
        return jsonify({"error": message}), 400

@discount.route('/discounts/<int:discount_id>', methods=['GET'])
@login_required
def get_discount(discount_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    discount = Discount.query.get(discount_id)
    if not discount or discount.seller_id != current_user.id:
        return jsonify({"error": "할인을 찾을 수 없습니다."}), 404

    return jsonify({
        "id": discount.id,
        "name": discount.name,
        "description": discount.description,
        "discount_type": discount.discount_type,
        "value": discount.value,
        "start_date": discount.start_date.strftime('%Y-%m-%d'),
        "end_date": discount.end_date.strftime('%Y-%m-%d'),
        "is_active": discount.is_active
    })

@discount.route('/discounts/<int:discount_id>', methods=['PUT'])
@login_required
def update_discount_route(discount_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    data = request.json
    updated_discount = discount_controller.update_discount(discount_id, data)
    if updated_discount:
        return jsonify({"message": "할인이 성공적으로 업데이트되었습니다."}), 200
    else:
        return jsonify({"error": "할인 업데이트에 실패했습니다."}), 400

@discount.route('/discounts/<int:discount_id>', methods=['DELETE'])
@login_required
def delete_discount_route(discount_id):
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    success = discount_controller.delete_discount(discount_id)
    if success:
        return jsonify({"message": "할인이 성공적으로 삭제되었습니다."}), 200
    else:
        return jsonify({"error": "할인 삭제에 실패했습니다."}), 400
    
@discount.route('/discounts', methods=['POST'])
@login_required
def create_discount():
    if not current_user.is_seller:
        return jsonify({"error": "권한이 없습니다."}), 403

    data = request.json
    data['seller_id'] = current_user.id
    new_discount = discount_controller.create_discount(data)
    return jsonify({"message": "할인이 성공적으로 생성되었습니다.", "id": new_discount.id}), 201

@discount.route('/discounts/product/<int:product_id>')
def get_product_discount(product_id):
    discount = discount_controller.get_product_discount(product_id)
    if discount:
        return jsonify({
            "id": discount.id,
            "name": discount.name,
            "discount_type": discount.discount_type,
            "value": discount.value
        })
    else:
        return jsonify({"message": "적용 가능한 할인이 없습니다."}), 404