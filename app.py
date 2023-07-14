import time

from flask import Flask
from urllib import request
import http.client
import json
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/devendra.choudhary/Downloads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','wav'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif','wav']
app.config['UPLOAD_PATH'] = 'uploads'

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_audio_text(filename):
    print("received request for test")
    audio_text = ""
    conn = http.client.HTTPSConnection("eastasia.stt.speech.microsoft.com")
    file_path = "/Users/devendra.choudhary/Downloads/Suryavamsam - Amitabh Bachchan Dialogue.wav"
    with open(file_path, 'rb') as file:
        payload = file.read()
        headers = {
            'Ocp-Apim-Subscription-Key': 'b2e7cf685d92496e95f0a310e0642883',
            'Content-Type': 'audio/wav'
        }
        conn.request("POST", "/speech/recognition/conversation/cognitiveservices/v1?language=en-IN", payload, headers)
        res = conn.getresponse()
        data = res.read()
        audio_text = data.decode("utf-8")
    print(audio_text)
    return audio_text

def get_search_query(audio_text):
    conn = http.client.HTTPSConnection("hackmee1-fc.openai.azure.com")
    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": "You are a shopping assistant. Reply in the language of the user. Reply like ShahRukhKhan would in Dilwale"
            },
            {
                "role": "system",
                "content": audio_text
            },
            {
                "role": "user",
                "content": "generate a product search query as small as possible"
            }
        ],
        "max_tokens": 800,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
        "stop": None
    })
    headers = {
        'Content-Type': 'application/json',
        'api-key': 'a2f35be0feb04e2187945ef2e7c03b0b'
    }
    conn.request("POST", "/openai/deployments/MonkSquadGPT35/chat/completions?api-version=2023-03-15-preview", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    response_data = json.loads(data.decode("utf-8"))
    return response_data["choices"][0]['message']['content']


def get_catalog_id_from_search_query(search_query):
    payload = json.dumps({
        "query": search_query,
        "limit": 5,
        "session": "ctx_1_uid_79065197_txt_-1_t_1674650882778",
        "sort_by": "most_relevant",
        "feed_params": {
            "preprocessor": {
                "is_did_you_mean": False
            },
            "search": {
                "is_internal_admin": False,
                "is_voice_search": False,
                "is_autocorrect_reverted": False
            }
        },
        "sort_order": "desc",
        "feed_filters": [
            [
                {
                    "field": "catalog_scheduling_status",
                    "op": "in",
                    "values": [
                        "1",
                        "7",
                        "8",
                        "19",
                        "11",
                        "16",
                        "3",
                        "18",
                        "9",
                        "15",
                        "6",
                        "10",
                        "14",
                        "17",
                        "5",
                        "12"
                    ]
                }
            ]
        ],
        "applied_filters": [],
        "catalog_ranking_exp": "NONE"
    })
    headers = {
        'Content-Type': 'application/json',
        'APP-USER-ID': '429120',
        'MEESHO-ISO-COUNTRY-CODE': 'IN',
        'MEESHO-CLIENT-ID': 'android',
        'ANONYMOUS-USER-ID': 'abc',
        'ACCESS-TOKEN': '738a10520fb5219615358e85e6dee3cc479510f0'
    }
    conn = http.client.HTTPConnection("172.19.88.68:80")
    conn.request("POST", "/api/v2/catalog/text-search/get", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    taxo_resp = data.decode("utf-8")
    response_data = json.loads(taxo_resp)
    catalog_id = response_data["data"]["catalogs"][0]["catalog_id"]

    return catalog_id



def get_product_attribute_with_desc(catalog_id):
    conn = http.client.HTTPConnection("bac-p-taxonomy-admin.meeshoint.in")
    payload = json.dumps({
        "catalog_ids": [
            catalog_id
        ],
        "request_flags": {
            "fetch_taxonomy_attributes": True,
            "fetch_serving_data": True,
            "fetch_psm_attributes": True,
            "fetch_variations": True,
            "fetch_collage": True,
            "fetch_old_sscat_details": True,
            "fetch_catalog_management_details": True
        }
    })
    headers = {
        'Authorization': 'Token 9d45fde2a565471ea2caa1ec8f49b7ee',
        'Content-Type': 'application/json',
        'MEESHO-ISO-COUNTRY-CODE': 'IN'
    }
    conn.request("POST", "/api/v1/catalog/aggregation", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    taxo_resp = data.decode("utf-8")
    response_data = json.loads(taxo_resp)

    first_product = response_data['catalogs'][0]['products'][0]
    product_attributes = first_product['taxonomy_attributes']
    category = first_product['new_category']['sub_sub_category_name']
    # product_description = first_product['description']
    product_name = first_product['name']
    text = product_name + " having the category of " + category + " and have the following attributes: " + str(product_attributes)
    return text



@app.route('/test')
def test():
    print("received request for test")
    folder = "/Users/devendra.choudhary/IdeaProjects/monkai/"
    file_path = "/Users/devendra.choudhary/Downloads/Suryavamsam - Amitabh Bachchan Dialogue.wav"
    # audio_text = get_audio_text(file_path)
    audio_text = "This is Designed as per the latest trends to keep you in sync with high fashion and with wedding and other occasion, it will keep you comfortable all day long. The lovely design forms a substantial feature of this wear.It looks stunning every time you match it with accessories.This attractive kurti will surely fetch you compliments for your rich sense of style.Stow away your old stuff when you wear this kurti. Light in weight Daily Wear, Working Wear kurtis will be soft against your skin. Its Simple and unique design and beautiful colours, prints and patterns. Stitched in regular fit, this kurti for women will keep you comfortable all day long. Front Design Looks perfect in this Kurtis. It can be perfect for get together, evening Functions,occasion and party wear as well. We believe in better clothing products cause helping women's to look pretty, feel comfortable is our ultimate goal. If you are not 100% happy, contact to us. before return your Kurti . We don't. We are committed to provide extremely durable readymade kurtis. Pair this kurti with a pair of stylish heels and a matching clutch for a complete casual look for a casual event, a party or an evening with friends. Our collection includes different styles of Kurtis that cater to a wide variety of the wardrobe requirements of the Indian woman. Make a fine addition to your wardrobe by adding this Festive kurti Suits from Bae's Wardrobe. This Kurti Will Give You A Trendy Look With its Beautiful Design coveRed White With Eye-Catching Patterns. Please check size chart in image section to get detailed measurement for choosing perfect size for you."
    search_query = get_search_query(audio_text)
    catalog_id = get_catalog_id_from_search_query(search_query)
    get_product_attribute_with_desc(catalog_id)
    return "test"


def do_processing_of_audio_file(audio_file_name):
    print("received request for do_processing_of_audio_file")
    folder = "/Users/devendra.choudhary/IdeaProjects/monkai/"
    file_path = folder + audio_file_name
    audio_text = get_audio_text(file_path)
    search_query = get_search_query(audio_text)
    catalog_id = get_catalog_id_from_search_query(search_query)
    text_for_voice = get_product_attribute_with_desc(catalog_id)
    return text_for_voice


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        filename = file.filename
        current_time_str = time.asctime( time.localtime(time.time()))
        full_file_name = str(current_time_str) + filename
        file.save(full_file_name)
        print('File saved successfully.')
        audio_text = do_processing_of_audio_file(full_file_name)
        return audio_text


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadv2', methods=['GET', 'POST'])
def upload_fileV2():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return ''

if __name__ == '__main__':
    # ssl._create_default_https_context = ssl._create_unverified_context
    app.run(host='0.0.0.0', port=8080)
