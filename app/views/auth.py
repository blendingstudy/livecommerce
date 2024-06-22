# app/views/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app.controllers.auth_controller import register, login, logout, profile, change_password
from app.models.user import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register_route():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return register()

@auth.route('/login', methods=['GET', 'POST'])
def login_route():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return login()

@auth.route('/logout')
@login_required
def logout_route():
    return logout()

@auth.route('/profile')
@login_required
def profile_route():
    return profile()

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password_route():
    return change_password()

@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # 여기에 비밀번호 재설정 이메일 전송 로직을 구현합니다.
            # 예: send_password_reset_email(user)
            flash('비밀번호 재설정 지침이 이메일로 전송되었습니다.', 'info')
        else:
            flash('해당 이메일 주소로 등록된 계정이 없습니다.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()
        flash('비밀번호가 재설정되었습니다.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')