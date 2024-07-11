from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.controllers import host_controller
from app.forms import ProductForm, LiveStreamForm
from datetime import datetime

from app.models.live_stream import LiveStream

host = Blueprint('host', __name__)

@host.route('/host/mypage')
@login_required
def mypage():
    if not current_user.is_seller:
        abort(403)
    
    total_revenue, _ = host_controller.get_host_revenue(current_user.id, 'all')
    monthly_revenue, _ = host_controller.get_host_revenue(current_user.id, 'monthly')
    streams, _ = host_controller.get_host_streams(current_user.id)
    products, _ = host_controller.get_host_products(current_user.id)
    recent_orders, _ = host_controller.get_host_orders(current_user.id, page=None, per_page=None)

    return render_template('host/mypage.html',
                           total_revenue=total_revenue['total'],
                           monthly_revenue=monthly_revenue['total'],
                           upcoming_streams=streams['upcoming'],
                           products=products[:5],
                           recent_orders=recent_orders[:5])

@host.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_seller:
        abort(403)
    
    streams, _ = host_controller.get_host_streams(current_user.id)
    products, _ = host_controller.get_host_products(current_user.id)
    total_revenue, _ = host_controller.get_host_revenue(current_user.id, 'all')
    monthly_revenue, _ = host_controller.get_host_revenue(current_user.id, 'monthly')
    recent_orders, _ = host_controller.get_host_orders(current_user.id, page=None, per_page=None)
    
    revenue = {
        'total': total_revenue['total'],
        'monthly': monthly_revenue['total']
    }
    
    return render_template('host/dashboard.html', 
                           streams=streams, 
                           products=products, 
                           revenue=revenue, 
                           recent_orders=recent_orders[:5])
    
@host.route('/stream_dashboard/<int:stream_id>')
@login_required
def stream_dashboard(stream_id):
    if not current_user.is_seller:
        abort(403)
    
    stream = LiveStream.query.get_or_404(stream_id)
    if stream.seller_id != current_user.id:
        abort(403)
    
    return render_template('host/stream_dashboard.html', stream=stream)

@host.route('/host/products')
@login_required
def products():
    if not current_user.is_seller:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 페이지당 표시할 제품 수

    products_query, error = host_controller.get_host_products(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    products = products_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('host/products.html', products=products)


@host.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_seller:
        abort(403)
    
    success, error = host_controller.delete_product(current_user.id, product_id)
    if error:
        flash(error, 'error')
    else:
        flash('제품이 성공적으로 삭제되었습니다.', 'success')
    return redirect(url_for('host.products'))

@host.route('/host/streams')
@login_required
def streams():
    if not current_user.is_seller:
        abort(403)
    
    streams, error = host_controller.get_host_streams(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    return render_template('host/streams.html', 
                           upcoming_streams=streams['upcoming'],
                           past_streams=streams['past'])

@host.route('/revenue')
@login_required
def revenue():
    if not current_user.is_seller:
        abort(403)
    
    period = request.args.get('period', 'all')
    revenue_data, error = host_controller.get_host_revenue(current_user.id, period)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    return render_template('host/revenue.html', revenue_data=revenue_data, period=period)

@host.route('/host/orders')
@login_required
def orders():
    if not current_user.is_seller:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    per_page = 10  # 페이지당 표시할 주문 수
    
    orders, error = host_controller.get_host_orders(current_user.id, status, page, per_page)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.mypage'))
    
    return render_template('host/orders.html', orders=orders, status=status)

@host.route('/stream_stats/<int:stream_id>')
@login_required
def stream_stats(stream_id):
    if not current_user.is_seller:
        abort(403)
    
    stats, error = host_controller.get_stream_stats(current_user.id, stream_id)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.streams'))
    
    return render_template('host/stream_stats.html', stats=stats)

from flask import request, jsonify

@host.route('/host/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_seller:
        abort(403)
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'success': False, 'error': '새로운 상태가 제공되지 않았습니다.'}), 400

    new_status = data['status']
    result, status_code = host_controller.update_order_status(current_user.id, order_id, new_status)
    
    return result, status_code