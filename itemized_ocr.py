import cv2
import matplotlib.pyplot as plt
import matplotlib
import io

from enum import Enum
from google.cloud import vision

input_file = 'catch_data/IMG_2176.jpeg'


client = vision.ImageAnnotatorClient()
with io.open(input_file, 'rb') as image_file:
    content = image_file.read()
image = vision.Image(content=content)
response = client.document_text_detection(image=image)
# print(response.text_annotations[0].description)

class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

# テキストを認識した場所に矩形を描く
def draw_boxes(input_file, bounds):
    img = cv2.imread(input_file, cv2.IMREAD_COLOR)
    for bound in bounds:
      p1 = (bound.vertices[0].x, bound.vertices[0].y) # top left
      p2 = (bound.vertices[1].x, bound.vertices[1].y) # top right
      p3 = (bound.vertices[2].x, bound.vertices[2].y) # bottom right
      p4 = (bound.vertices[3].x, bound.vertices[3].y) # bottom left
      cv2.line(img, p1, p2, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
      cv2.line(img, p2, p3, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
      cv2.line(img, p3, p4, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
      cv2.line(img, p4, p1, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    return img

# OCR結果の境界情報bounds（リスト）を返す
def get_document_bounds(response, feature):
    document = response.full_text_annotation
    bounds = []
    # 特定された特徴の境界情報を，全て数え上げてbounds.append
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                          bounds.append(symbol.bounding_box)
                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)
                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)
            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)
    # boundsは境界の座標情報を持つ
    return bounds

# 行ごとに情報をまとめる
def get_sorted_lines(response):
    document = response.full_text_annotation
    # boundsにシンボルの境界情報のリストをappendする
    bounds = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        #シンボルの境界ボックスの頂点のx, y座標
                        x = symbol.bounding_box.vertices[0].x
                        y = symbol.bounding_box.vertices[0].y
                        text = symbol.text
                        bounds.append([x, y, text, symbol.bounding_box])
    # シンボルのy座標に基づいてソート（昇順）
    bounds.sort(key=lambda x: x[1])
    for i in range(0,len(bounds)):
        print(bounds[i])
    old_y = -1
    line = []
    lines = []
    threshold = 1
    for bound in bounds:
        x = bound[0]
        y = bound[1]
        if old_y == -1:
            old_y = y
        elif old_y-threshold <= y <= old_y+threshold:
            old_y = y
        else:
            old_y = -1
            line.sort(key=lambda x: x[0])
            lines.append(line)
            line = []
        line.append(bound)
    line.sort(key=lambda x: x[0])
    lines.append(line)
    return lines

img = cv2.imread(input_file, cv2.IMREAD_COLOR)

lines = get_sorted_lines(response)
for line in lines:
  texts = [i[2] for i in line]
  texts = ''.join(texts)
  bounds = [i[3] for i in line]
  #print(texts)
  for bound in bounds:
    p1 = (bounds[0].vertices[0].x, bounds[0].vertices[0].y)   # top left
    p2 = (bounds[-1].vertices[1].x, bounds[-1].vertices[1].y) # top right
    p3 = (bounds[-1].vertices[2].x, bounds[-1].vertices[2].y) # bottom right
    p4 = (bounds[0].vertices[3].x, bounds[0].vertices[3].y)   # bottom left
    cv2.line(img, p1, p2, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    cv2.line(img, p2, p3, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    cv2.line(img, p3, p4, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    cv2.line(img, p4, p1, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)

fig = plt.figure(figsize=[10,10])
plt.axis('off')
plt.imshow(img[:,:,::-1]);plt.title("img_by_line")
fig.savefig('img2.png')


"""
bounds = get_document_bounds(response, FeatureType.BLOCK)
img_block = draw_boxes(input_file, bounds)

bounds = get_document_bounds(response, FeatureType.PARA)
img_para = draw_boxes(input_file, bounds)

bounds = get_document_bounds(response, FeatureType.WORD)
img_word = draw_boxes(input_file, bounds)

bounds = get_document_bounds(response, FeatureType.SYMBOL)
img_symbol = draw_boxes(input_file, bounds)

fig = plt.figure(figsize=[40,40])
plt.subplot(141);plt.imshow(img_block[:,:,::-1]);plt.title("img_block")
plt.subplot(142);plt.imshow(img_para[:,:,::-1]);plt.title("img_para")
plt.subplot(143);plt.imshow(img_word[:,:,::-1]);plt.title("img_word")
plt.subplot(144);plt.imshow(img_symbol[:,:,::-1]);plt.title("img_symbol")
fig.savefig('img.png')

"""

