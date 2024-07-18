from flask import current_app
from pytz import timezone
from app import scheduler
from app.models import LiveStream
from app.services.notification_service import send_email_notification
from datetime import datetime, timedelta

def check_upcoming_streams():
    print('Checking upcoming streams...')
    # 현재 시간을 로컬 시간대로 가져옵니다.
    local_tz = timezone('Asia/Seoul')  # 또는 해당하는 로컬 시간대
    now = datetime.now(local_tz)
    
    # 30분 후의 시간을 계산합니다.
    thirty_mins_later = now + timedelta(minutes=30)
    
    upcoming_streams = LiveStream.query.filter(
        LiveStream.start_time.between(now.replace(tzinfo=None), thirty_mins_later.replace(tzinfo=None))
    ).all()
    
    print(f"Found {len(upcoming_streams)} upcoming streams")
    
    for stream in upcoming_streams:
        print(f"Sending notification for stream: {stream.title}, starting at: {stream.start_time}")
        send_email_notification(stream.seller, stream)