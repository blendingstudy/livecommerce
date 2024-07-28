from datetime import datetime
import os
from flask import current_app, flash, jsonify, redirect, request, url_for, render_template
from flask_login import current_user, login_required
from sqlalchemy import and_
from app import db
from app.controllers import discount_controller
from app.models import Product
from app.forms import AddToCartForm, ProductForm
from app.models.discount import Discount
from app.models.product import Category
from werkzeug.utils import secure_filename

def list_products(page=1, per_page=12, category=None):
    query = Product.query
    if category:
        query = query.filter(Product.category.has(name=category))
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    return render_template('product/list.html', products=products, categories=categories, selected_category=category)

def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm(product_id=product_id)  # 장바구니 추가 폼 생성
    discount = discount_controller.get_product_discount(product_id)
    
    original_price = product.price
    discounted_price = original_price
    
    if discount:
        if discount.discount_type == 'percentage':
            discounted_price = original_price * (1 - discount.value / 100)
        else:  # fixed amount
            discounted_price = max(original_price - discount.value, 0)
    
    product.view_count += 1
    db.session.commit()
    return render_template('product/detail.html', product=product, 
                           original_price=original_price, 
                           discounted_price=discounted_price,
                           discount=discount, form=form)
    
@login_required
def create_product():
    if not current_user.is_seller:
        flash('판매자만 제품을 등록할 수 있습니다.', 'warning')
        return redirect(url_for('main.index'))

    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            seller_id=current_user.id,
            category_id=form.category.data
        )

        # 이미지 파일 처리
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(current_app.root_path, 'static/product_images', filename)
            
            # 동일한 파일명이 존재할 경우 고유한 파일명 생성
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                filename = f"{base}_{counter}{extension}"
                file_path = os.path.join(current_app.root_path, 'static/product_images', filename)
                counter += 1

            image_file.save(file_path)
            product.image_url = filename

        db.session.add(product)
        db.session.commit()
        flash('제품이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('product.product_detail', product_id=product.id))
    return render_template('product/create.html', form=form)

@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        flash('자신의 제품만 수정할 수 있습니다.', 'warning')
        return redirect(url_for('product.product_detail', product_id=product.id))

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        # form.populate_obj(product) 대신 수동으로 각 필드를 업데이트합니다.
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        
        # 카테고리는 ID로 설정하지 않고 객체로 설정합니다.
        category = Category.query.get(form.category.data)
        if category:
            product.category = category
        else:
            flash('유효하지 않은 카테고리입니다.', 'danger')
            return render_template('product/edit.html', form=form, product=product)

        """ if form.image.data:
            image_filename = save_image(form.image.data)
            product.image_url = image_filename """

        db.session.commit()
        flash('제품 정보가 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('product.product_detail', product_id=product.id))
    
    # GET 요청 시 현재 카테고리 ID를 폼에 설정
    if product.category:
        form.category.data = product.category.id
    
    return render_template('product/edit.html', form=form, product=product)

@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'error': '자신의 제품만 삭제할 수 있습니다.'}), 403
        flash('자신의 제품만 삭제할 수 있습니다.', 'warning')
        return redirect(url_for('product.product_detail', product_id=product_id))

    try:
        db.session.delete(product)
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'message': '제품이 성공적으로 삭제되었습니다.'}), 200
        flash('제품이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('product.products_list'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'제품 삭제 중 오류가 발생했습니다: {str(e)}', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))

def search_products(query, page=1, per_page=12):
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('product/search.html', products=products, query=query)

def get_seller_products(seller_id, page=1, per_page=12):
    products = Product.query.filter_by(seller_id=seller_id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('product/seller_products.html', products=products, seller_id=seller_id)

def get_discounted_products(page=1, per_page=12):
    now = datetime.utcnow()
    discounted_products = Product.query.join(Product.discounts).filter(
        and_(
            Discount.start_date <= now,
            Discount.end_date >= now,
            Discount.is_active == True
        )
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return discounted_products

def toggle_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    if product in current_user.favorite_products:
        current_user.favorite_products.remove(product)
        status = 'removed'
    else:
        current_user.favorite_products.append(product)
        status = 'added'
    db.session.commit()
    return jsonify({'status': status})