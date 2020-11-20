# GoogleのOCR解析

import io
import os
import json

# ラベル抽出
def label_detection(filepath):
    # Google Cloud client libraryをインポート
    from google.cloud import vision

    # visionAPIのクライアントインスタンス
    client = vision.ImageAnnotatorClient()

    # 認識する画像ファイルのパスを設定
    # ex : file_name = os.path.abspath('resources/wakeupcat.jpg')
    file_name = os.path.abspath(filepath)

    # 画像をメモリにロード
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # 画像ファイルからラベルを抽出
    response = client.label_detection(image=image)
    labels = response.label_annotations

    print('Labels:')
    for label in labels:
        print(label.description)

# 画像中の文字を検出
def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

# 文章の読み取り
def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        # バイナリ化した画像をcontentに代入
        content = image_file.read()

    image = vision.Image(content=content)

    # GoogleCloudからの認識結果を受け取る
    response = client.document_text_detection(image=image)

    # レスポンスの中身を確認
    print(response.text_annotations[0].description)

    """
    # 認識結果をjsonファイルに保存
    with open('test.json', 'w') as f:
        texts = proto.Message.to_json(response.full_text_annotation.pages[0].blocks[0].paragraphs[0].words[0])
        json.dump(texts, f, indent=2, ensure_ascii=False)
    """

    """
    # 書き込み用jsonを開く
    with open('test.json') as f:
        d_update = json.load(f, object_pairs_hook=OrderedDict)
    """

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

detect_document('catch_data/IMG_2056.jpeg')
