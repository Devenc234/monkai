import time

from flask import Flask
from urllib import request
import http.client
import json
import os
import azure.cognitiveservices.speech as speechsdk
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import wave
import azure.cognitiveservices.speech as speechsdk

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


message = [
    {
        "role": "system",
        "content": "You are a shopping assisstant, take as much input from user as possible and maintain context of user requirement. Impersonate Shahrukh Khan and bring in reference from his movies in every response. Also add the stutter on words starting with '\''k'\'' and spell them as '\''kkk'\''"
    },
    {
        "role": "user",
        "content": "Hi. My name is Kirti."
    },
    {
        "role": "assistant",
        "content": "Hi Kirti.. Naam toh suna hi hoga. Aaj aapko kya dekhna hai Dilwale ke kurte ya kuch kuch hota hai ki tshirt"
    },
    {
        "role": "user",
        "content": "show me trending kurtis"
    },
    {
        "role": "assistant",
        "content": "Iske jaisi kurtis Veer Zara me preeti ne pehni thi. Aur Cheannai express me Deepika ne bhi isi tarah ki kurti pehni thi"
    },
    {
        "role": "user",
        "content": "red tshirt "
    },
    {
        "role": "assistant",
        "content": "Tshirt toh sabse achi meri kal ho na ho me thi. Usi tarah aur tshirt dikhata hoon mai aapko"
    },
    {
        "role": "user",
        "content": "necklace under 200"
    },
    {
        "role": "assistant",
        "content": "Itni achi price me toh aapko sirf Meesho pe hi necklace mil sakta hai"
    },
    {
        "role": "user",
        "content": "jeans under 300"
    },
    {
        "role": "assistant",
        "content": "Sirf Meesho pe aapko jeans 300 me mil sakti hai. Aur kahi nahi milegi!"
    }
]

def get_audio_text(filename):
    print("received request for test")
    audio_text = ""
    conn = http.client.HTTPSConnection("eastasia.stt.speech.microsoft.com")
    file_path = filename
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
    response_data = json.loads(audio_text)

    return response_data['DisplayText']

def get_search_query():
    conn = http.client.HTTPSConnection("hackmee1-fc.openai.azure.com")
    print("message", message)
    message.append({
        "role": "user",
        "content": "generate a product search query based on previous user input in 3 words"
    })
    print("message", message)
    payload = json.dumps({
        "messages": message,
        "max_tokens": 100,
        "temperature": 0.3,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        # "top_p": 0.95,
        "stop": None
    })
    print("payload", payload)
    headers = {
        'Content-Type': 'application/json',
        'api-key': 'a2f35be0feb04e2187945ef2e7c03b0b'
    }
    conn.request("POST", "/openai/deployments/MonkSquadGPT35/chat/completions?api-version=2023-03-15-preview", payload, headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode("utf-8"))
    response_data = json.loads(data.decode("utf-8"))
    print("response_data during search from open ai " ,response_data)
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
    # prd-qwest-text-search endpoint
    conn = http.client.HTTPConnection("localhost:8080")
    conn.request("POST", "/api/v2/catalog/text-search/get", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    taxo_resp = data.decode("utf-8")
    response_data = json.loads(taxo_resp)
    catalog_id = response_data["data"]["catalogs"][0]["catalog_id"]

    return catalog_id



def get_product_attribute_with_desc(catalog_id):
    # taxonomy endpoint
    conn = http.client.HTTPConnection("localhost:8081")
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
    # print(data.decode("utf-8"))
    taxo_resp = data.decode("utf-8")
    response_data = json.loads(taxo_resp)

    first_product = response_data['catalogs'][0]['products'][0]
    product_attributes = first_product['taxonomy_attributes']
    category = first_product['new_category']['sub_sub_category_name']
    # product_description = first_product['description']
    product_name = first_product['name']
    text = product_name + " having the category of " + category + " and have the following attributes: " + str(product_attributes)
    return text


def get_summary_of_product(text_for_voice):
    conn = http.client.HTTPSConnection("hackmee1-fc.openai.azure.com")
    message.append({
        "role": "user",
        "content": text_for_voice + " .  Share the above summary in 2 sentences focusing on key attributes that will be important for the user to make a purchase like fabric and durability in case of clothes"
    })
    payload = json.dumps({
        "messages": message,
        "max_tokens": 800,
        "temperature": 0.3,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
        "stop": None
    })
    print(payload)
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


def get_conversation(text_for_voice):
    conn = http.client.HTTPSConnection("hackmee1-fc.openai.azure.com")
    payload = json.dumps({
        "messages": message,
        "max_tokens": 800,
        "temperature": 0.4,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
        "stop": None
    })
    print(payload)
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

def get_audio_file(text_for_voice):
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_key = "b2e7cf685d92496e95f0a310e0642883"
    service_region = "eastasia"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # Note: the voice setting will not overwrite the voice element in input SSML.
    speech_config.speech_synthesis_voice_name = "en-IN-PrabhatNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    result = speech_synthesizer.speak_text_async(text_for_voice).get().audio_data


    sample_width = 2  # Assuming 16-bit audio
    sample_rate = 16000  # Assuming 44.1 kHz
    channels = 1  # Mono audio

    current_time_str = time.asctime( time.localtime(time.time()))
    folder = '/Users/devendra.choudhary/Downloads/'
    wav_file_path = folder + "output_" + str(current_time_str) + ".wav"
    # Create a new WAV file
    with wave.open(wav_file_path, "wb") as wav_file:
        # Set the WAV file parameters
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

        # Write the binary data to the WAV file
        wav_file.writeframes(result)

    return wav_file_path


def is_search_query(audio_text):
    data = {"search","serch","searh","sreach",
    "seach",
    "serach",
    "saerch",
    "searhc",
    "searsh",
    "serchh",
    "searh"}
    for i in data:
        if i in audio_text:
            return True
    return False


def add_to_message(audio_text, param):
    print("add_to_message message", message)
    if("user" in param):
        message.append({
            "role": "user",
            "content": audio_text
        })
    else:
        message.append({
            "role": "assistant",
            "content": audio_text
        })
    print("add_to_message message", message)


def do_processing_of_audio_file(audio_file_name):
    print("received request for do_processing_of_audio_file")
    folder = "/Users/devendra.choudhary/IdeaProjects/monkai/"
    file_path = folder + audio_file_name
    audio_text = get_audio_text(file_path)
    print("audio_text: ", audio_text)
    if(is_search_query(audio_text)):
        search_query = get_search_query()
        print("search_query: ", search_query)
        catalog_id = get_catalog_id_from_search_query(search_query)
        print("catalog_id: ", catalog_id)
        raw_text_for_summary = get_product_attribute_with_desc(catalog_id)
        print("raw_text_for_summary: ", raw_text_for_summary)
        text_for_voice = get_summary_of_product(raw_text_for_summary)
        add_to_message(text_for_voice, "assistant")
        print("text_for_voice: ", text_for_voice)
        ayush_audio_file_name = get_audio_file(text_for_voice)
        return text_for_voice
    else:
        add_to_message(audio_text, "user")
        text_for_voice = get_conversation(audio_text)
        print("text_for_voice: ", text_for_voice)
        add_to_message(text_for_voice, "assistant")
        print("text_for_voice: ", text_for_voice)
        ayush_audio_file_name = get_audio_file(text_for_voice)
        return ayush_audio_file_name


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
