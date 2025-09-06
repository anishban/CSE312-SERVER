import requests


def picture(userid):
    url = 'https://api.dicebear.com/9.x/pixel-art/svg?seed='+userid
    res = requests.get(url)
    file ='./public/imgs/profile-pics/'+userid+'.svg'
    with open(file,'wb') as f:
        f.write(res.content)
