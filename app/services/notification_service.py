from flask import current_app
from flask_mail import Message
from app import mail

def send_email_notification(user, stream):
    """ msg = Message('Stream Notification',
                  recipients=[user.email])
    msg.body = f"Your stream '{stream.title}' is starting soon!"
    current_app.extensions['mail'].send(msg) """
    print("send_email")

# 카카오톡이나 SMS 알림 기능도 비슷한 방식으로 구현할 수 있습니다.
# 이를 위해서는 각각의 API를 사용해야 합니다.