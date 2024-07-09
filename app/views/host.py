from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.controllers import host_controller
from app.forms import ProductForm, LiveStreamForm
from datetime import datetime

host = Blueprint('host', __name__)

@host.route('/host/mypage')
@login_required
def mypage():
    if not current_user.is_seller:
        abort(403)
    
    total_revenue, _ = host_controller.get_host_revenue(current_user.id, 'all')
    monthly_revenue, _ = host_controller.get_host_revenue(current_user.id, 'monthly')
    live_streams, _ = host_controller.get_host_streams(current_user.id, 'live')
    upcoming_streams, _ = host_controller.get_host_streams(current_user.id, 'upcoming')
    products, _ = host_controller.get_host_products(current_user.id)
    recent_orders, _ = host_controller.get_host_orders(current_user.id)

    return render_template('host/mypage.html',
                           total_revenue=total_revenue['total'],
                           monthly_revenue=monthly_revenue['total'],
                           live_streams=live_streams,
                           upcoming_streams=upcoming_streams,
                           products=products[:5],
                           recent_orders=recent_orders[:5])

@host.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_seller:
        abort(403)
    
    host, error = host_controller.get_host_profile(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    streams, _ = host_controller.get_host_streams(current_user.id)
    products, _ = host_controller.get_host_products(current_user.id)
    revenue, _ = host_controller.get_host_revenue(current_user.id)
    
    return render_template('host/dashboard.html', host=host, streams=streams, products=products, revenue=revenue)

@host.route('/products')
@login_required
def products():
    if not current_user.is_seller:
        abort(403)
    
    products, error = host_controller.get_host_products(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    return render_template('host/products.html', products=products)

@host.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    if not current_user.is_seller:
        abort(403)
    
    form = ProductForm()
    if form.validate_on_submit():
        product_data = {
            'name': form.name.data,
            'description': form.description.data,
            'price': form.price.data,
            'stock': form.stock.data
        }
        product, error = host_controller.create_product(current_user.id, product_data)
        if error:
            flash(error, 'error')
        else:
            flash('제품이 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('host.products'))
    
    return render_template('host/create_product.html', form=form)

@host.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_seller:
        abort(403)
    
    product, error = host_controller.get_host_products(current_user.id)
    if error or not product:
        flash('제품을 찾을 수 없습니다.', 'error')
        return redirect(url_for('host.products'))
    
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product_data = {
            'name': form.name.data,
            'description': form.description.data,
            'price': form.price.data,
            'stock': form.stock.data
        }
        success, error = host_controller.update_product(current_user.id, product_id, product_data)
        if error:
            flash(error, 'error')
        else:
            flash('제품이 성공적으로 업데이트되었습니다.', 'success')
            return redirect(url_for('host.products'))
    
    return render_template('host/edit_product.html', form=form, product=product)

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

@host.route('/streams')
@login_required
def streams():
    if not current_user.is_seller:
        abort(403)
    
    streams, error = host_controller.get_host_streams(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    return render_template('host/streams.html', streams=streams)

@host.route('/streams/create', methods=['GET', 'POST'])
@login_required
def create_stream():
    if not current_user.is_seller:
        abort(403)
    
    form = LiveStreamForm()
    if form.validate_on_submit():
        stream_data = {
            'title': form.title.data,
            'description': form.description.data,
            'scheduled_start_time': form.scheduled_start_time.data,
            'products': form.products.data
        }
        stream, error = host_controller.create_stream(current_user.id, stream_data)
        if error:
            flash(error, 'error')
        else:
            flash('라이브 스트림이 성공적으로 생성되었습니다.', 'success')
            return redirect(url_for('host.streams'))
    
    return render_template('host/create_stream.html', form=form)

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

@host.route('/orders')
@login_required
def orders():
    if not current_user.is_seller:
        abort(403)
    
    status = request.args.get('status', 'all')
    orders, error = host_controller.get_host_orders(current_user.id, status)
    if error:
        flash(error, 'error')
        return redirect(url_for('host.dashboard'))
    
    return render_template('host/orders.html', orders=orders, status=status)