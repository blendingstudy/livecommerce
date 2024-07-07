from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.controllers import payment_controller
from app.services.iamport_service import IamportService

payment = Blueprint('payment', __name__)

@payment.route('/create_order', methods=['POST'])
@login_required
def create_order():
    data = request.json
    order, error = payment_controller.create_order(data.get('products', []))
    
    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'order_id': order.id, 
        'redirect_url': url_for('payment.checkout', order_id=order.id)
    }), 201

@payment.route('/checkout/<int:order_id>', methods=['GET'])
@login_required
def checkout(order_id):
    order, error = payment_controller.get_order_for_checkout(order_id, current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    return render_template('payment/checkout.html', order=order)

@payment.route('/verify/<int:order_id>', methods=['POST'])
@login_required
def verify_payment(order_id):
    """ print('hi')
    data = request.json
    current_app.logger.info(f"Received verification request for order {order_id}: {data}")
    print(f'Received verification request for order {order_id}: {data}')
    imp_uid = data.get('imp_uid')
    merchant_uid = data.get('merchant_uid')

    iamport_service = IamportService()
    try:
        payment_data = iamport_service.find_payment(imp_uid)
        if payment_data['status'] == 'paid':
            # 결제 금액 검증
            order, _ = payment_controller.get_order_for_checkout(order_id, current_user.id)
            if order and order.total_price == payment_data['amount']:
                # 결제 성공 처리
                success, message = payment_controller.process_payment(order_id, 'iamport', imp_uid)
                if success:
                    return jsonify({'success': True, 'message': '결제가 성공적으로 처리되었습니다.'}), 200
                else:
                    return jsonify({'success': False, 'message': message}), 400
            else:
                # 결제 금액 불일치
                return jsonify({'success': False, 'message': '결제 금액이 일치하지 않습니다.'}), 400
        else:
            # 결제 실패
            return jsonify({'success': False, 'message': '결제에 실패했습니다.'}), 400
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {str(e)}")
        return jsonify({'success': False, 'message': '결제 검증 중 오류가 발생했습니다.'}), 500 """
    data = request.json
    current_app.logger.info(f"Received verification request for order {order_id}: {data}")
    imp_uid = data.get('imp_uid')
    merchant_uid = data.get('merchant_uid')

    try:
        success, message = payment_controller.verify_payment(order_id, imp_uid, merchant_uid)
        if success:
            return jsonify({'success': True, 'message': '결제가 성공적으로 처리되었습니다.'}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {str(e)}")
        return jsonify({'success': False, 'message': '결제 검증 중 오류가 발생했습니다.'}), 500
    
    

@payment.route('/order_status/<int:order_id>')
@login_required
def order_status(order_id):
    print('order status')
    order, error = payment_controller.get_order_status(order_id)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))

    return render_template('payment/order_status.html', order=order)

@payment.route('/order_history')
@login_required
def order_history():
    orders = payment_controller.get_user_order_history()
    return render_template('payment/order_history.html', orders=orders)

@payment.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    success, message = payment_controller.cancel_order(order_id)

    if not success:
        return jsonify({'error': message}), 400

    return jsonify({'message': message}), 200

@payment.route('/test', methods=['GET'])
def test_route():
    print('hi')
    return jsonify({"message": "Test route is working"}), 200