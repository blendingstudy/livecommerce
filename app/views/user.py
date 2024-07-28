from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.controllers import review_controller, user_controller
from app.forms import UserProfileForm
from app.models.review import Review

user = Blueprint('user', __name__)

@user.route('/user/mypage')
@login_required
def mypage():
    return render_template('user/mypage.html')

@user.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if current_user.id != user_id:
        abort(403)
    
    user, error = user_controller.get_user_profile(user_id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    return render_template('user/profile.html', user=user)

@user.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    if current_user.id != user_id:
        abort(403)
    
    form = UserProfileForm()
    
    if form.validate_on_submit():
        data = {
            'username': form.username.data,
            'email': form.email.data,
            'phone_number': form.phone_number.data,
            'address': form.address.data
        }
        if form.password.data:
            data['password'] = form.password.data
        
        success, message = user_controller.update_user_profile(user_id, data)
        if success:
            flash(message, 'success')
            if current_user.is_seller:
                return redirect(url_for('host.mypage', user_id=user_id))
            else:
                return redirect(url_for('user.mypage', user_id=user_id))
        else:
            flash(message, 'error')
    
    user, _ = user_controller.get_user_profile(user_id)
    form.username.data = user.username
    form.email.data = user.email
    form.phone_number.data = user.phone_number
    form.address.data = user.address
    
    return render_template('user/edit_profile.html', form=form, user=user)

@user.route('/purchase_history')
@login_required
def purchase_history():
    history, error = user_controller.get_purchase_history(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    return render_template('user/purchase_history.html', history=history)

@user.route('/favorites')
@login_required
def favorites():
    favorites, error = user_controller.get_user_favorites(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    return render_template('user/favorites.html', favorites=favorites)

@user.route('/add_favorite/<string:item_type>/<int:item_id>', methods=['POST'])
@login_required
def add_favorite(item_type, item_id):
    success, message = user_controller.add_to_favorites(current_user.id, item_type, item_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(request.referrer or url_for('main.index'))

@user.route('/remove_favorite/<string:item_type>/<int:item_id>', methods=['POST'])
@login_required
def remove_favorite(item_type, item_id):
    success, message = user_controller.remove_from_favorites(current_user.id, item_type, item_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(request.referrer or url_for('main.index'))

""" @user.route('/revenue')
@login_required
def revenue():
    if not current_user.is_seller:
        abort(403)
    
    revenue_data, error = user_controller.get_user_revenue(current_user.id)
    if error:
        flash(error, 'error')
        return redirect(url_for('main.index'))
    
    return render_template('user/revenue.html', revenue_data=revenue_data) """
    
@user.route('/reviews')
@login_required
def reviews():
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()
    
    # 사용자가 구매한 모든 상품 가져오기
    purchased_products = review_controller.get_purchased_products()
    
    # 사용자가 리뷰를 작성한 상품 ID 목록
    reviewed_product_ids = [review.product_id for review in user_reviews]
    
    return render_template('user/reviews.html', 
                           reviews=user_reviews, 
                           purchased_products=purchased_products, 
                           reviewed_products=reviewed_product_ids)

@user.route('/write_review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def write_review_route(product_id):
    return review_controller.write_review(product_id)

@user.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review_route(review_id):
    return review_controller.edit_review(review_id)

@user.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review_route(review_id):
    return review_controller.delete_review(review_id)