from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import and_
from app.forms import ReviewForm
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app import db

def get_purchased_products():
    # 사용자가 구매한 모든 상품 가져오기
    purchased_products = db.session.query(Product).join(Order.items).filter(
        Order.user_id == current_user.id
    ).distinct().all()
    
    return purchased_products

def write_review(product_id):
    product = Product.query.get_or_404(product_id)
    
    # 사용자가 해당 상품을 구매했는지 확인
    order = Order.query.filter(and_(Order.user_id == current_user.id, Order.items.any(product_id=product_id))).first()
    if not order:
        flash('구매한 상품에 대해서만 리뷰를 작성할 수 있습니다.', 'warning')
        return redirect(url_for('user.reviews'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=form.rating.data,
            content=form.content.data
        )
        db.session.add(review)
        db.session.commit()
        flash('리뷰가 성공적으로 작성되었습니다.', 'success')
        return redirect(url_for('user.reviews'))
    
    return render_template('user/write_review.html', form=form, product=product)

def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('이 리뷰를 수정할 권한이 없습니다.', 'danger')
        return redirect(url_for('user.reviews'))
    
    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.content = form.content.data
        db.session.commit()
        flash('리뷰가 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('user.reviews'))
    
    return render_template('user/edit_review.html', form=form, review=review)

def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        return jsonify({'success': False, 'message': '이 리뷰를 삭제할 권한이 없습니다.'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'success': True, 'message': '리뷰가 성공적으로 삭제되었습니다.'})



