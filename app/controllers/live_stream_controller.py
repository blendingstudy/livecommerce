from flask import app, current_app, flash, jsonify, redirect, url_for, render_template, request, abort
from flask_login import current_user, login_required
from app import db, socketio
from app.models import LiveStream, Product, User
from app.forms import LiveStreamForm
from datetime import datetime

from app.models.product import Category

def list_streams(page=1, per_page=10):
    streams = LiveStream.query.filter_by(is_live=True).order_by(LiveStream.start_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('live_stream/list.html', streams=streams)

from app.models import LiveStream, Product
from app.forms import LiveStreamForm, ProductForm

""" @login_required
def create_stream():
    if not current_user.is_seller:
        flash('판매자만 라이브 스트림을 생성할 수 있습니다.', 'warning')
        return redirect(url_for('main.index'))

    form = LiveStreamForm()
    # 기존 제품 선택지 설정
    form.existing_products.choices = [(p.id, p.name) for p in Product.query.filter_by(seller_id=current_user.id).all()]
    # 카테고리 선택지 설정
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

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
    
    return render_template('live_stream/create.html', form=form) """

@login_required
def create_stream():
    current_app.logger.info("Create stream function called")
    if request.method == 'POST':
        current_app.logger.info("POST request received")
        current_app.logger.info(f"Form data: {request.form}")
        
    if not current_user.is_seller:
        flash('판매자만 라이브 스트림을 생성할 수 있습니다.', 'warning')
        return redirect(url_for('main.index'))

    stream_form = LiveStreamForm()
    product_form = ProductForm()

    stream_form.existing_products.choices = [(p.id, p.name) for p in Product.query.filter_by(seller_id=current_user.id).all()]
    product_form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if stream_form.validate_on_submit():
        stream = LiveStream(
            title=stream_form.title.data,
            description=stream_form.description.data,
            seller_id=current_user.id
        )
        
        for product_id in stream_form.existing_products.data:
            product = Product.query.get(product_id)
            if product:
                stream.products.append(product)
        
        db.session.add(stream)
        db.session.commit()
        flash('라이브 스트림이 생성되었습니다.', 'success')
        return redirect(url_for('live_stream.stream_host', stream_id=stream.id))
    
    # 폼 유효성 검사 실패 시 에러 출력
    if stream_form.errors:
        print(stream_form.errors)
    
    return render_template('live_stream/create.html', stream_form=stream_form, product_form=product_form)

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
    print('end')
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
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category.data,
            seller_id=current_user.id
        )

        if form.image.data:
            # 이미지 처리 로직 (파일 저장 등)
            pass

        db.session.add(product)
        db.session.commit()

        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'description': product.description
        })

    return jsonify({'error': 'Invalid form data'}), 400