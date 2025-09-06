from util.request import Request
from util.response import Response
from util.authentication import *
from util.multipart import *
from util.database import *
import uuid
from datetime import datetime
import ffmpeg
from dotenv import load_dotenv
import requests
def change_avatar(request,handler):
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    ret = parse_multipart(request)
    id = str(uuid.uuid4())
    avatar_part = ret.parts[0]
    file = (avatar_part.headers.get('Content-Disposition')).rsplit('filename=')[1]
    ext = file.rsplit('.',1)[1]
    ext=ext.replace('"','')
    ext=ext.lower()
    filename = './public/imgs/profile-pics/'+id+'.'+ext

    with open(filename,'wb') as f:
        f.write(avatar_part.content)
    
    filename='/public/imgs/profile-pics/'+id+'.'+ext
    updated = {'$set':{'imageURL':filename}}
    users.update_one({'username':user.get('username')},updated)
    

    res=Response()
    res.text("Avatar Changed")
    handler.request.sendall(res.to_data())
    return

def upload_vid(request,handler):
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    ret = parse_multipart(request)
    id = str(uuid.uuid4())
    os.makedirs('./public/uploaded_videos/'+id)
    filename = './public/uploaded_videos/'+id+'/'+id+'.mp4'
    video_part = ret.parts[2]
    current_time = str(datetime.now().isoformat())

    description_part = ret.parts[1]
    title_part = ret.parts[0]

    with open(filename,'wb') as f:
        f.write(video_part.content)
    unq_id=None
    probe = ffmpeg.probe(filename)
    duration = float(probe['format']['duration'])
    thumbnails=None
    thumbnail_URL = None
    try:
        if duration<=60.0:
            load_dotenv()
            url = 'https://transcription-api.nico.engineer/'
            AUTH = os.getenv('TRANSCRIBER_AUTH_TOKEN','changeMe')
            audio_file = './public/uploaded_videos/'+id+'/audio_'+id+'.mp3'
            ffmpeg.input(filename).output(audio_file).run()
            headers = {"Authorization":"Bearer "+AUTH}
            with open(audio_file,'rb') as f:
                files = {"file":(audio_file,f,'audio/mpeg')}
                res = requests.post(url=url+'transcribe',files=files, headers=headers)
            res=res.json()
            unq_id = res.get('unique_id')
    except:
        print("Exception During Transcription")
    try:
        second_frame_dur = duration*0.25
        middle_frame_dur = duration*0.5
        fourth_frame_dur = duration*0.75
        last_frame_dur = duration-0.2
        dire = './public/uploaded_videos/'+id+'/thumbnails'
        os.makedirs(dire)
        dire=dire+'/'
        ffmpeg.input(filename).output(dire+'first_frame.jpg',vframes=1).run()
        ffmpeg.input(filename,ss=second_frame_dur).output(dire+'second_frame.jpg', vframes=1).run() 
        ffmpeg.input(filename,ss=middle_frame_dur).output(dire+'mid_frame.jpg', vframes=1).run() 
        ffmpeg.input(filename,ss=fourth_frame_dur).output(dire+'fourth_frame.jpg', vframes=1).run() 
        ffmpeg.input(filename,ss=last_frame_dur).output(dire+'last_frame.jpg', vframes=1).run() 
        thumbnails = [dire+'first_frame.jpg',dire+'second_frame.jpg',dire+'mid_frame.jpg',dire+'fourth_frame.jpg',dire+'last_frame.jpg']
        thumbnail_URL=dire+'first_frame.jpg'
    except:
        print("Exception occured while generating thumbnails")
    hls_path=None
    try:
        ffmpeg.input(filename).output('./public/uploaded_videos/'+id+'/480p.m3u8',format='hls',hls_list_size=0,video_bitrate='800k').run()
        ffmpeg.input(filename).output('./public/uploaded_videos/'+id+'/720p.m3u8',format='hls',hls_list_size=0,video_bitrate='2800k').run()
        ffmpeg.input(filename).output('./public/uploaded_videos/'+id+'/144p.m3u8',format='hls',hls_list_size=0,video_bitrate='150k').run()
        with open('./public/uploaded_videos/'+id+'/index.m3u8', 'w') as f:
            f.write('#EXTM3U\n')
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=854x480\n')
            f.write('480p.m3u8\n')
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720\n')
            f.write('720p.m3u8\n')
            f.write('#EXT-X-STREAM-INF:BANDWIDTH=150000,RESOLUTION=256x144')
            f.write('144p.m3u8')
        hls_path='./public/uploaded_videos/'+id+'/index.m3u8'
    except:
        print("Error at hls")


    vid = {
        'author_id':user.get('username'),
        'title':(title_part.content).decode(),
        'description':(description_part.content).decode(),
        'video_path':filename,
        'created_at':current_time,
        'id':id,
        'transcription_id':unq_id,
        'thumbnails':thumbnails,
        'thumbnailURL':thumbnail_URL,
        'hls_path':hls_path
    }

    videos.insert_one(vid)

    r = {'id':id}
    res=Response()
    res.json(r)
    handler.request.sendall(res.to_data())
    return
    
def getvideos(request,handler):
    video_list = list(videos.find({},{'_id':0}))
    res=Response()
    resp={'videos':video_list}
    res.json(resp)
    handler.request.sendall(res.to_data())
    return

def getonevid(request,handler):
    vid_id = (request.path).split('/api/videos/')[1]
    video = videos.find_one({'id':vid_id},{'_id':0})
    resp={'video':video}
    res=Response()
    res.json(resp)
    handler.request.sendall(res.to_data())
    return

def transcribe(request,handler):
    vid_id = (request.path).split('/api/transcriptions/')[1]
    video = videos.find_one({'id':vid_id},{'_id':0})
    uniq_id = video.get('transcription_id',None)
    if uniq_id == None:
        res=Response()
        res.set_status(400,'Bad Request')
        handler.request.sendall(res.to_data())
        return
    url = 'https://transcription-api.nico.engineer/transcriptions/'+uniq_id
    transcr = './public/uploaded_videos/'+vid_id+'/transcript_'+vid_id+'.vtt'
    if os.path.exists(transcr):
        with open(transcr,'r') as f:
            vtt = f.read()
        res=Response()
        res.text(vtt)
        handler.request.sendall(res.to_data())
        return
    AUTH = os.getenv('TRANSCRIBER_AUTH_TOKEN')
    headers = {"Authorization":"Bearer "+AUTH}
    resp = requests.get(url,headers=headers)
    if resp.status_code != 200:
        res=Response()
        res.set_status(400,"Bad Request")
        handler.request.sendall(res.to_data())
        return
    url = resp.json().get('s3_url')
    resp = requests.get(url)
    with open(transcr, 'wb') as f:
        f.write(resp.content)
    res=Response()
    res.bytes(resp.content)
    handler.request.sendall(res.to_data())
    return

def set_thumbnail(request,handler):
    vid_id = (request.path).split('/api/thumbnails/')[1]
    url = (json.loads((request.body).decode())).get('thumbnailURL')
    updated = {'$set':{'thumbnailURL':url}}
    videos.update_one({'id':vid_id},updated)
    msg = {'message':'update succesfull'}
    res=Response()
    res.json(msg)
    handler.request.sendall(res.to_data())
    return


