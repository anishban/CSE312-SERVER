import ffmpeg
import os
filename = './public/uploaded_videos/30+s/30+sec.mp4'
output_path = './public/uploaded_videos/30+s/'


resolutions = {
            '480p': {'scale': '854:480', 'bitrate': '800k'},
            '720p': {'scale': '1280:720', 'bitrate': '2800k'}
        }
ffmpeg.input(filename).output(output_path+'480p.m3u8',format='hls',hls_list_size=0,video_bitrate='800k').run()
ffmpeg.input(filename).output(output_path+'720p.m3u8',format='hls',hls_list_size=0,video_bitrate='2800k').run()

with open(output_path + 'index.m3u8', 'w') as f:
    f.write('#EXTM3U\n')
    f.write('#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=854x480\n')
    f.write('480p.m3u8\n')
    f.write('#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720\n')
    f.write('720p.m3u8\n')