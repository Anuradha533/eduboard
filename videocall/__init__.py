# views.py
from flask import Blueprint, request , url_for ,jsonify , render_template
from flask_login import login_required, current_user
from models import studentDetails , TeacherDetails , User
import os
import time

video = Blueprint('video', __name__, template_folder='templates',static_folder="static",static_url_path='/static/video')
from dotenv import load_dotenv
load_dotenv()

from agora_token_builder import RtcTokenBuilder, RtmTokenBuilder

ROLE_RTM_USER = 1
ROLE_PUBLISHER = 1

@video.route('/video')
@login_required
def index():
    users = User.query.all()
    return render_template('video.html', title='Video Chat', allUsers=users , agoraAppID=os.getenv('AGORA_APP_ID'))

@video.route('/video/users')
def fetch_users():
    users = User.query.all()
    all_users = [user.to_json() for user in users] 

    return jsonify(all_users)

@video.route('/video/token',  methods=['POST'])
def generate_agora_token():
    auth_user = current_user
    appID = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = request.json['channelName']
    userAccount = auth_user.email
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, ROLE_PUBLISHER, privilegeExpiredTs)

    rtm_token = RtmTokenBuilder.buildToken(
        appID, appCertificate, userAccount, ROLE_RTM_USER, privilegeExpiredTs)
    return jsonify({'token': token, 'rtm_token': rtm_token, 'appID': appID})