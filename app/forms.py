from flask_wtf import FlaskForm
from wtforms import DateTimeField, DateTimeLocalField, FieldList, FileField, FloatField, FormField, HiddenField, IntegerField, RadioField, SelectField, SelectMultipleField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email as EmailValidator, EqualTo, Length, NumberRange, Optional
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

class LiveStreamForm(FlaskForm):
    title = StringField('스트림 제목', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('설명', validators=[Length(max=500)])
    existing_products = SelectMultipleField('기존 제품', coerce=int)
    #new_products = FieldList(FormField(ProductForm), min_entries=1)
    start_time = DateTimeLocalField('예약 시작 시간', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    thumbnail = FileField('썸네일 이미지', validators=[FileAllowed(['jpg', 'png'], '이미지만 업로드 가능합니다.')])
    submit = SubmitField('스트림 생성')
    #category = SelectField('카테고리', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LiveStreamForm, self).__init__(*args, **kwargs)
        
class AddToCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    
class UserProfileForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('이메일', validators=[DataRequired(), EmailValidator()])
    phone_number = StringField('전화번호')
    address = StringField('주소')
    password = PasswordField('새 비밀번호', validators=[EqualTo('confirm_password', message='비밀번호가 일치하지 않습니다')])
    confirm_password = PasswordField('새 비밀번호 확인')
    submit = SubmitField('프로필 업데이트')
    
class ReviewForm(FlaskForm):
    rating = IntegerField('평점', validators=[DataRequired(), NumberRange(min=1, max=5)])
    content = TextAreaField('리뷰 내용', validators=[DataRequired()])
    submit = SubmitField('리뷰 제출')
    
