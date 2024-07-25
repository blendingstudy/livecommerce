from app import create_app, socketio, scheduler
import eventlet

eventlet.monkey_patch()
app = create_app()
#print(app.url_map)

if __name__ == '__main__':
    socketio.run(app)#, use_reloader=False)