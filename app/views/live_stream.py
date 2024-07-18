from flask import Blueprint, flash, redirect, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from app.controllers.live_stream_controller import (
    add_product,
    list_streams,
    create_stream,
    host_stream,
    watch_stream,
    end_stream,
    get_stream_info,
    leave_stream,
    delete_stream
)
from app.models.live_stream import LiveStream

live_stream = Blueprint('live_stream', __name__)

@live_stream.route('/streams')
def streams_list():
    page = request.args.get('page', 1, type=int)
    return list_streams(page)

@live_stream.route('/stream/create', methods=['GET', 'POST'])
@login_required
def stream_create():
    return create_stream()

@live_stream.route('/stream/host/<int:stream_id>')
@login_required
def stream_host(stream_id):
    return host_stream(stream_id)

@live_stream.route('/stream/watch/<int:stream_id>')
def stream_watch(stream_id):
    return watch_stream(stream_id)

@live_stream.route('/stream/end/<int:stream_id>', methods=['POST'])
@login_required
def stream_end(stream_id):
    return end_stream(stream_id)

@live_stream.route('/stream/info/<int:stream_id>')
def stream_info(stream_id):
    return jsonify(get_stream_info(stream_id))

# WebSocket 이벤트를 처리하는 라우트는 필요하지 않습니다.
# 이벤트 핸들러는 live_stream_controller.py에 이미 정의되어 있습니다.

# 추가적인 라우트: 판매자의 라이브 스트림 목록
@live_stream.route('/my-streams')
@login_required
def my_streams():
    if not current_user.is_seller:
        flash('판매자만 접근할 수 있습니다.', 'warning')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    streams = LiveStream.query.filter_by(seller_id=current_user.id).order_by(LiveStream.start_time.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('live_stream/my_streams.html', streams=streams)

# 라이브 스트림 검색
@live_stream.route('/search')
def search_streams():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    streams = LiveStream.query.filter(LiveStream.title.contains(query) | LiveStream.description.contains(query)).order_by(LiveStream.start_time.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('live_stream/search.html', streams=streams, query=query)

@live_stream.route('/add_product', methods=['POST'])
@login_required
def stream_add_product():
    return add_product()

@live_stream.route('/leave_stream', methods=['POST'])
def leave_stream_route():
    data = request.json
    stream_id = data['streamId']
    print(f"Received leave_stream request for stream {stream_id}")
    
    """ if current_user.is_authenticated:
        user_id = current_user.id
        stream = LiveStream.query.get(stream_id)
        if stream:
            stream.viewer_count = max(0, stream.viewer_count - 1)
            db.session.commit()
            print(f"Updated viewer count for stream {stream_id}: {stream.viewer_count}")
    
    return jsonify({"status": "success"}), 200 """
    return leave_stream(stream_id)

@live_stream.route('/delete_stream/<int:stream_id>', methods=['POST'])
def delete_stream_route(stream_id):
    return delete_stream(stream_id)