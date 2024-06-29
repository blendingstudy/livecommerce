from flask import app, flash, jsonify, redirect, url_for, render_template, request, abort
from flask_login import current_user, login_required
from app import db, socketio
from app.models import LiveStream, Product, User
from app.forms import LiveStreamForm
from datetime import datetime

def list_streams(page=1, per_page=10):
    streams = LiveStream.query.filter_by(is_live=True).order_by(LiveStream.start_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('live_stream/list.html', streams=streams)

from app.models import LiveStream, Product
from app.forms import LiveStreamForm, ProductForm

@login_required
def create_stream():
    if not current_user.is_seller:
        flash('판매자만 라이브 스트림을 생성할 수 있습니다.', 'warning')
        return redirect(url_for('main.index'))

    form = LiveStreamForm()
    form.existing_products.choices = [(p.id, p.name) for p in Product.query.filter_by(seller_id=current_user.id).all()]

    if form.validate_on_submit():
        stream = LiveStream(
            title=form.title.data,
            description=form.description.data,
            seller_id=current_user.id
        )
        
        # 선택된 제품 추가
        for product_id in form.existing_products.data:
            product = Product.query.get(product_id)
            if product:
                stream.products.append(product)
        
        db.session.add(stream)
        db.session.commit()
        flash('라이브 스트림이 생성되었습니다.', 'success')
        return redirect(url_for('live_stream.stream_host', stream_id=stream.id))
    
    return render_template('live_stream/create.html', form=form)

@login_required
def host_stream(stream_id):
    stream = LiveStream.query.get_or_404(stream_id)
    if stream.seller_id != current_user.id:
        abort(403)
    return render_template('live_stream/host.html', stream=stream)

def watch_stream(stream_id):
    stream = LiveStream.query.get_or_404(stream_id)
    if not stream.is_live:
        flash('이 스트림은 현재 라이브 상태가 아닙니다.', 'info')
        return redirect(url_for('live_stream.list_streams'))
    return render_template('live_stream/watch.html', stream=stream)

@login_required
def end_stream(stream_id):
    stream = LiveStream.query.get_or_404(stream_id)
    if stream.seller_id != current_user.id:
        abort(403)
    stream.end_stream()
    db.session.commit()
    flash('라이브 스트림이 종료되었습니다.', 'success')
    return redirect(url_for('live_stream.list_streams'))

def get_stream_info(stream_id):
    stream = LiveStream.query.get_or_404(stream_id)
    return {
        'id': stream.id,
        'title': stream.title,
        'description': stream.description,
        'viewer_count': stream.viewer_count,
        'start_time': stream.start_time.isoformat(),
        'is_live': stream.is_live,
        'seller': {
            'id': stream.seller.id,
            'username': stream.seller.username
        },
        'products': [{
            'id': product.id,
            'name': product.name,
            'price': product.price
        } for product in stream.products]
    }

@login_required
def add_product():
    data = request.json
    new_product = Product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        seller_id=current_user.id
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        'id': new_product.id,
        'name': new_product.name,
        'price': new_product.price,
        'description': new_product.description
    })