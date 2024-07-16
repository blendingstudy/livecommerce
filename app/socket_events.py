import traceback
from flask import request
from flask_login import current_user
import flask_login
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.models import LiveStream, User, Product
from app import db

# 시청자 목록을 저장할 딕셔너리
viewers = {}

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)
    if current_user.is_authenticated:
        flask_login.login_user(current_user)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected:', request.sid)
    disconnected_user = None
    disconnected_stream = None

    for stream_id, stream_viewers in list(viewers.items()):
        for user_id, user_info in list(stream_viewers.items()):
            if user_info.get('sid') == request.sid:
                disconnected_user = user_id
                disconnected_stream = stream_id
                break
        if disconnected_user:
            break

    if disconnected_user and disconnected_stream:
        print(f'Disconnected user {disconnected_user} found in stream {disconnected_stream}')
        handle_leave_stream({'streamId': disconnected_stream})
    else:
        print('Disconnected user not found in any stream')

@socketio.on('join_stream')
def handle_join_stream(data):
    print(f"Received join_stream event with data: {data}")
    stream_id = data['streamId']
    user_type = data.get('as', 'viewer')  # 'host' 또는 'viewer'
    user_id = current_user.id
    username = current_user.username
    room = f'stream_{stream_id}'
    join_room(room)
    print(f'User {request.sid} joined stream {stream_id} as {user_type}')
    
    if user_type == 'viewer':
        # 호스트에게 새 시청자 알림
        if stream_id not in viewers:
            viewers[stream_id] = {}
        viewers[stream_id][user_id] = {'username': username, 'sid': request.sid}
        emit('viewer_joined', request.sid, room=room, skip_sid=request.sid)
        emit('update_viewer_list', {k: v['username'] for k, v in viewers[stream_id].items()}, room=f'stream_{stream_id}')
        print(f"Emitted viewer_joined event for user {request.sid} in room {room}")

        # 시청자 수 업데이트
        stream = LiveStream.query.get(stream_id)
        if stream:
            stream.viewer_count += 1
            db.session.commit()
            emit('viewer_count_update', {'count': stream.viewer_count}, room=room)
    elif user_type == 'host':
        # 호스트용 로직 (필요한 경우)
        pass

@socketio.on('leave_stream')
def handle_leave_stream(data):
    print('leave_stream event received via WebSocket')
    stream_id = data['streamId']
    user_id = current_user.id if current_user.is_authenticated else None
    room = f'stream_{stream_id}'
    
    if stream_id in viewers and user_id in viewers[stream_id]:
        user_info = viewers[stream_id][user_id]
        username = user_info['username']
        del viewers[stream_id][user_id]
        leave_room(room)
        print(f'User {user_id} left stream {stream_id}')

        # 호스트에게 시청자 퇴장 알림
        emit('viewer_left', {'userId': user_id, 'username': username}, room=room)
            
        # 모든 시청자에게 업데이트된 시청자 목록 전송
        emit('update_viewer_list', {k: v['username'] for k, v in viewers[stream_id].items()}, room=room)

        # 시청자 수 업데이트
        stream = LiveStream.query.get(stream_id)
        if stream:
            stream.viewer_count = max(0, stream.viewer_count - 1)
            db.session.commit()
            emit('viewer_count_update', {'count': stream.viewer_count}, room=room)
    else:
        print(f'User {user_id} not found in stream {stream_id} viewers')

@socketio.on('start_stream')
def handle_start_stream(data):
    stream_id = data['streamId']
    stream = LiveStream.query.get(stream_id)
    if stream:
        stream.is_live = True
        db.session.commit()
        emit('stream_started', {'streamId': stream_id}, broadcast=True)
        emit('stream_started', {'streamId': stream_id}, room=f'stream_{stream_id}')
        print(f'Stream {stream_id} started')

@socketio.on('end_stream')
def handle_end_stream(data):
    stream_id = data['streamId']
    stream = LiveStream.query.get(stream_id)
    if stream:
        stream.is_live = False
        stream.viewer_count = 0
        db.session.commit()
        emit('stream_ended', {'streamId': stream_id}, room=f'stream_{stream_id}')
        print(f'Stream {stream_id} ended')

@socketio.on('offer')
def handle_offer(data):
    print(f"Handling offer: {data}")
    emit('offer', {'from': request.sid, 'offer': data['offer']}, room=data['to'])

@socketio.on('answer')
def handle_answer(data):
    print(f"Handling answer: {data}")
    emit('answer', {'from': request.sid, 'answer': data['answer']}, room=data['to'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    print(f"Handling ICE candidate: {data}")
    if 'to' in data:
        emit('ice_candidate', {'from': request.sid, 'candidate': data['candidate']}, room=data['to'])
    elif 'streamId' in data:
        room = f'stream_{data["streamId"]}'
        emit('ice_candidate', {'from': request.sid, 'candidate': data['candidate']}, room=room, include_self=False)

@socketio.on('chat_message')
def handle_chat_message(data):
    stream_id = data['streamId']
    message = data['message']
    if current_user.is_authenticated:
        user_id = current_user.id
        username = current_user.username
    else:
        user_id = None
        username = 'Anonymous'
    
    room = f'stream_{stream_id}'
    emit('new_chat_message', {'username': username, 'message': message}, room=room)

@socketio.on('show_product')
def handle_show_product(data):
    stream_id = data['streamId']
    product_id = data['productId']
    product = Product.query.get(product_id)
    room = f'stream_{stream_id}'
    print('product_shown')
    if product:
        emit('product_shown', {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'image_url': product.image_url
        }, room=room)

@socketio.on_error()
def error_handler(e):
    print('An error has occurred:', str(e))

@socketio.on('*')
def catch_all(event, data):
    print(f"Caught event: {event}, with data: {data}")

@socketio.on('create_room')
def handle_create_room(data):
    stream_id = data['streamId']
    room = f'stream_{stream_id}'
    join_room(room)
    print(f'Host created room: {room}')
        
from flask_socketio import disconnect

@socketio.on('kick_viewer')
def on_kick_viewer(data):
    print('Received kick_viewer event')
    stream_id = data['streamId']
    user_id = int(data['userId'])
    print(f"Attempting to kick user {user_id} from stream {stream_id}")
    print("Current viewers:", viewers)
    room = f'stream_{stream_id}'
    
    try:
        if stream_id in viewers and user_id in viewers[stream_id]:
            kicked_username = viewers[stream_id][user_id]
            del viewers[stream_id][user_id]
            
            print(f"Emitting viewer_kicked event for user {user_id}")
            emit('viewer_kicked', {'userId': user_id, 'username': kicked_username}, room=f'stream_{stream_id}')
            
            print(f"Emitting update_viewer_list event")
            emit('update_viewer_list', viewers[stream_id], room=f'stream_{stream_id}')
            
            # 시청자 수 업데이트
            stream = LiveStream.query.get(stream_id)
            if stream:
                stream.viewer_count = max(0, stream.viewer_count - 1)
                db.session.commit()
                emit('viewer_count_update', {'count': stream.viewer_count}, room=room)
            
            print(f"User {user_id} kicked successfully")
        else:
            print(f"User {user_id} not found in stream {stream_id}")
    except Exception as e:
        print(f"Error kicking viewer: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
