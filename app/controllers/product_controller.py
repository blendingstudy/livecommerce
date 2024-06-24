from flask import flash, redirect, url_for, render_template
from flask_login import current_user, login_required
from app import db
from app.models import Product
from app.forms import ProductForm
from app.models.product import Category

def list_products(page=1, per_page=12, category=None):
    query = Product.query
    if category:
        query = query.filter(Product.category.has(name=category))
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    return render_template('product/list.html', products=products, categories=categories, selected_category=category)

def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product/detail.html', product=product)

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
            seller_id=current_user.id
        )
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
        flash('자신의 제품만 삭제할 수 있습니다.', 'warning')
        return redirect(url_for('product.product_detail', product_id=product.id))

    db.session.delete(product)
    db.session.commit()
    flash('제품이 성공적으로 삭제되었습니다.', 'success')
    return redirect(url_for('product.list_products'))

def search_products(query, page=1, per_page=12):
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('product/search.html', products=products, query=query)

def get_seller_products(seller_id, page=1, per_page=12):
    products = Product.query.filter_by(seller_id=seller_id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('product/seller_products.html', products=products, seller_id=seller_id)