
from __future__ import print_function
import aiohttp
import asyncio
import uvicorn
import gzip
import requests
from math import sqrt
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
export_file_url = 'https://docs.google.com/uc?export=download&id=1PlgZ5G9xYpYCdAfg7DHrfVKgh6QtsPtF'
export_file_name = 'beatslandmark-52c5550189c6.json'
export_file_id = '1PlgZ5G9xYpYCdAfg7DHrfVKgh6QtsPtF'
import os
import io
# Imports Credential File:
imageurl  =  "https://images.unsplash.com/photo-1619537903549-0981d6bca911?crop=entropy&cs=tinysrgb&fm=jpg&ixlib=rb-1.2.1&q=80&raw_url=true&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1740"#@param {type:"string"}

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))



def emotionsUrl(url):
  client = vision.ImageAnnotatorClient()
  image = vision.Image()
  image.source.image_uri = url
  response = client.face_detection(image=image)
  emoList = []
  for face in response.face_annotations:
      joylikelihood = vision.Likelihood(face.joy_likelihood)
      surpriselikelihood = vision.Likelihood(face.surprise_likelihood)
      angerlikelihood = vision.Likelihood(face.anger_likelihood)
      emoList.append((joylikelihood.name,surpriselikelihood.name,angerlikelihood.name))
  return emoList
def emotionsUpload(img):
  
  from google.cloud import vision
  client = vision.ImageAnnotatorClient()
#   with io.open(img, 'rb') as image_file:
#     content = image_file.read()
  
  image= vision.Image(content=img)

  response = client.face_detection(image=image)
  emoList = []
  for face in response.face_annotations:
      joylikelihood = vision.Likelihood(face.joy_likelihood)
      surpriselikelihood = vision.Likelihood(face.surprise_likelihood)
      angerlikelihood = vision.Likelihood(face.anger_likelihood)
      emoList.append((joylikelihood.name,surpriselikelihood.name,angerlikelihood.name))
  return emoList
def labellerUpload(img):
  from google.cloud import vision
  labelList = []
  client = vision.ImageAnnotatorClient()
  image= vision.Image(content=img)

  response = client.label_detection(image=image)
  for label in response.label_annotations:
    if label.score>0.75:
        labelList.append(label.description)
  return labelList
def colorinfoUpload(img):
  from google.cloud import vision

  client = vision.ImageAnnotatorClient()
  image= vision.Image(content=img)
  response = client.image_properties(image=image)
  props = response.image_properties_annotation
  colorDict = {}
  for color in props.dominant_colors.colors:

      
      colorDict[(color.color.red,color.color.green,color.color.blue)]= color.score
      
  return colorDict
def rgbgenreDict():
    rgbgenre = {
    (181,104,12):"country",
    (240,180,181):"new-age",
    (161,124,100):"reggae",
    (208,173,96):"classical",
    (22,172,176):"pop",
    (177,124,101):"electro",
    (208,173,96):"folk",
    (215,127,125):"hip-hop",
    (40,40,40):"industrial",
    (82,241,127):"techno",
    (135,206,250):"jazz",
    (0,58,18):"metal",
    (97,0,97):"punk",
    (105,136,162):"r-n-b",
    (129,0,41):"edm",
    (135,192,149):"rock"
    }
    return rgbgenre
def genrePrediction(img):
    rgbgenre=rgbgenreDict()
    colorDict = colorinfoUpload(img)
    top3 = sorted(colorDict, key=colorDict.get, reverse=True)[:3]
    autoGenre = []
    def closest_color(rgb,COLORS):
        r, g, b = rgb
        color_diffs = []
        for color in COLORS:
            cr, cg, cb = color
            color_diff = sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]
    for x in top3:
        autoGenre.append(closest_color(x,list(rgbgenre.keys())))

    genreselection = [rgbgenre[x]for x in autoGenre]
    return genreselection
    p
def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    download_file_from_google_drive(export_file_id, path / export_file_name)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path) +"/"+ export_file_name



loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())

@app.route('/spotify', methods=['POST'])
async def login_spotify(request):
    html_file = path / 'spotify-login' / 'authorization_code'/'public'/'index.html'

    
    return HTMLResponse(html_file.open().read())
@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    genreselection = genrePrediction(img_bytes)
    genrestring = "%2C".join(genreselection)
    
    topgenre = genreselection[0]
    
    return JSONResponse({'result': str(genrePrediction(img_bytes))})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
