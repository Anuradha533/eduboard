# views.py
from flask import Blueprint, render_template, request , jsonify ,render_template_string ,url_for , flash , redirect
from flask_login import login_required, current_user
from models import User , Message , Notification,db
from auth import online_users
from forms import MessageForm 
from datetime import datetime
from sqlalchemy import or_

chat = Blueprint('chat', __name__, template_folder='templates',static_folder="static",static_url_path='/static/chat')

# Function to create notifications
def create_notification(user_id, message):
    notification = Notification(user_id=user_id, message=message)
    db.session.add(notification)
    db.session.commit()

@chat.route('/inbox')
@login_required
def home():
    # Fetch conversations of the current user
    conversations = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    
    # Create a dictionary to store online status of users
    online_status = {}
    for conversation in conversations:
        if conversation.sender_id != current_user.id:
            online_status[conversation.sender_id] = conversation.sender.id in online_users.values()
        if conversation.receiver_id != current_user.id:
            online_status[conversation.receiver_id] = conversation.receiver.id in online_users.values()
    
    return render_template('inbox.html', online_users=online_users, conversations=conversations, online_status=online_status)

# Route to access unread notifications for the current user as JSON
@chat.route('/notifications', methods=['GET'])
@login_required
def get_unread_notifications():
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    notifications_data = []
    for notification in unread_notifications:
        notifications_data.append({
            'id': notification.id,
            'message': notification.message,
            'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(notifications_data)

@chat.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def room(user_id):
    # Fetch conversations of the current user
    conversations = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    
    # Create a dictionary to store online status of users
    online_status = {}
    for conversation in conversations:
        if conversation.sender_id != current_user.id:
            online_status[conversation.sender_id] = conversation.sender.id in online_users.values()
        if conversation.receiver_id != current_user.id:
            online_status[conversation.receiver_id] = conversation.receiver.id in online_users.values()

    form = MessageForm()
    recipient_user = User.query.get_or_404(user_id)
    
    # Fetch messages between the current user and the recipient user
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) & (Message.receiver_id == user_id) |
        (Message.sender_id == user_id) & (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp)
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            receiver_id=user_id,
            content=form.content.data,
            status='unread'
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        create_notification(user_id , f"You have a new message from {current_user.email}")
        return redirect(url_for('chat.room', user_id=user_id))
    
    return render_template('chatroom.html', online_users=online_users, form=form, recipient_user=recipient_user, messages=messages , conversations=conversations, online_status=online_status)

@chat.route('/chat_search')
@login_required
def search():
    query = request.args.get('q', '').lower()  # Get the search query from the request
    filtered_users = {user_id: user_info for user_id, user_info in online_users.items() if query in user_info['email'].lower()}
    
    # Build the HTML for the <li> elements
    sidebar_html = ""
    for user_id, user_info in filtered_users.items():
        sidebar_html += f"""
            <li>
                <a href="{url_for('chat.room',user_id=user_info['id'])}" id="{user_info['email']}" class="select-room uk-active">
                    <img class="uk-border-circle uk-margin-small-right" src="https://via.placeholder.com/50" alt="User Avatar">
                    {user_info['email']}
                </a>
            </li>
        """

    return render_template_string(sidebar_html)
