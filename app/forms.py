from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, IntegerField, RadioField, SelectField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email as EmailValidator, EqualTo, Length, NumberRange
from flask_wtf.file import FileAllowed

from app.models.product import Category
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), EmailValidator()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    remember = BooleanField('로그인 상태 유지')
    submit = SubmitField('로그인')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(), EmailValidator()])
    submit = SubmitField('비밀번호 재설정 요청')

class RegistrationForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('이메일', validators=[DataRequired(), EmailValidator()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    user_type = RadioField('계정 유형', choices=[('buyer', '구매자'), ('seller', '판매자')], validators=[DataRequired()])
    submit = SubmitField('가입하기')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 등록된 이메일입니다.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('현재 비밀번호', validators=[DataRequired()])
    new_password = PasswordField('새 비밀번호', validators=[DataRequired()])
    confirm_password = PasswordField('새 비밀번호 확인', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('비밀번호 변경')

class ProductForm(FlaskForm):
    name = StringField('제품명', validators=[DataRequired()])
    description = TextAreaField('설명')
    price = FloatField('가격', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('재고', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('카테고리', coerce=int, validators=[DataRequired()])
    image = FileField('이미지', validators=[FileAllowed(['jpg', 'png'], '이미지만 업로드 가능합니다.')])
    submit = SubmitField('제출')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.order_by('name')]