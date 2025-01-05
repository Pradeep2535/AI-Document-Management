from flask import Flask, request, jsonify, render_template
from parameters_extract import analyze_keywords, identify_document,load_document, chatbot_answer,reset_memory
from mongo_db_backend import MongoDB
from bson.binary import Binary
import os
import mimetypes
from pdf2image import convert_from_bytes
import pytesseract
from pdf2image import convert_from_path,convert_from_bytes
from PIL import Image
import magic
from io import BytesIO
from tempfile import NamedTemporaryFile
from drive import upload_file_to_folder, create_nested_folders, create_or_get_folder
import io
import random
import base64
from langchain.memory import ConversationBufferMemory
from worker import celery_init_app
from flask_caching import Cache

cache=Cache()

app = Flask(__name__,template_folder='templates', static_folder='static')
app.config['CACHE_TYPE'] = "RedisCache"
app.config['CACHE_REDIS_HOST'] = "localhost"
app.config['CACHE_REDIS_PORT'] = 6379
app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost:6379/1",
        result_backend="redis://localhost:6379/2",
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
    ),
)
app.config['CELERY_TIMEZONE'] = 'Asia/Kolkata'
cache.init_app(app)
celery_app = celery_init_app(app)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
pytesseract.pytesseract.tesseract_cmd = r"C:\\Tesseract\\Tesseract-OCR\\tesseract.exe"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Encoding
def encode_base64(text):
    encoded = base64.b64encode(text.encode('utf-8'))
    return encoded.decode('utf-8')

# Decoding
def decode_base64(encoded_text):
    decoded = base64.b64decode(encoded_text)
    return decoded.decode('utf-8')


def detect_file_type(uploaded_file):
    
    mime = magic.Magic(mime=True)
    
    file_type = mime.from_buffer(uploaded_file)

    if 'pdf' in file_type:
        return 'pdf'
    elif 'image' in file_type:
        return 'image'
    else:
        return 'unknown'


def extract_text_with_ocr(uploaded_file):
    text = ""
    try:
        # Read the uploaded file into a BytesIO object
        file_bytes = BytesIO(uploaded_file)
       #print("------------------")
        #print(uploaded_file)
        # Convert PDF to images using the correct Poppler path
        images = convert_from_bytes(file_bytes.getvalue(), poppler_path=r'C:\\Users\\malap\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin')
        
        # Perform OCR on each image and extract text
        for image in images:
            text += pytesseract.image_to_string(image, lang='eng+hin+tam')  # Adding Tamil language
        #print(text)
    except Exception as e:
        print(f"Error performing OCR: {e}")
    #print(text)
    finally:
        return text


# def extract_text_from_pdf(pdf_path):
#     """
#     Extract text from a PDF using PyMuPDF, fallback to OCR.
#     """
#     text = extract_text_with_pymupdf(pdf_path)
#     if not text.strip():
#         print("No text found with PyMuPDF. Using OCR...")
#         text = extract_text_with_ocr(pdf_path)
#     return text


def extract_text_from_image(uploaded_file):
   
    text = ""
    try:
        # Read the uploaded file into a BytesIO object
        image_bytes = BytesIO(uploaded_file)
        
        # Open the image from the BytesIO object
        image = Image.open('aadhar_backside.png')
        
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image, lang='tam+eng+hin')
    except Exception as e:
        print(f"Error extracting text from image: {e}")
    
    return text


# --- Document Classification ---
def classify_document(text):
    """
    Classify the document as Aadhaar, PAN, or Voter ID based on keywords.
    """
    aadhaar_keywords = ["aadhaar", "uidai"]

    pan_keywords = ["permanent account number", "income tax department"]

    voter_keywords = ["election commission of india", "epic number", "electoral photo identity card"]

    text_lower = text.lower()

    if all(keyword in text_lower for keyword in aadhaar_keywords):
        return "aadhaar"
    elif all(keyword in text_lower for keyword in pan_keywords):
        return "pan"
    elif all(keyword in text_lower for keyword in voter_keywords):
        return "voter"
    else:

        #if not able to identify then using gemini model

        identified_document_type = identify_document(text=text)

        return identified_document_type.lower()
    
def generate_12_digit_number():
    return random.randint(10**11, 10**12 - 1)



@app.route('/')
def index():
    """
    Renders the main landing page of the application.
    """
    
    return render_template("index.html") 


@app.route('/customer')
def about():
    return render_template('/customer.html')

@app.route('/transaction')
def transaction():
    return render_template('/transaction_history.html')

@app.route('/upload')
def upload():
    return render_template('/upload.html')

@app.route('/test')
def test():
    return render_template('/test.html')


@app.route("/upload_file",methods = ["POST"])
def upload_file():

    if 'file' not in request.files:
        return jsonify({"upload_status" : 'not_uploaded' })
        
    
    file = request.files['file']
    #print("-"*100)
    #print(file,file.filename)
    if file.filename == '':
        return jsonify({"upload_status" : 'not_uploaded' })

    if file and allowed_file(file.filename):
        
        file_bytes = file.read()
        file_io = io.BytesIO(file_bytes)

    
    
        file_type = detect_file_type(file_bytes)

        extracted_text = ""
        #print("-"*10)
        #print(file_bytes,file_type)

        if file_type == 'pdf':
            extracted_text = extract_text_with_ocr(file_bytes)
            #print(extracted_text)
        elif file_type == 'image':
            extracted_text = extract_text_from_image(file_bytes)
        else:
            status = "unsupported"

        document_type = classify_document(extracted_text)
        
        print(document_type)
        name, dob, address = analyze_keywords(text=extracted_text)
        print(name,dob,address)
        if name is None:
            status = 'upload_different_document'
            print(status)
        else:
            name=name.lower()
            
            mongo_client = MongoDB()
            print("-"*200)
            account_status, accounts = mongo_client.person_id(name=name,dob=dob,address=address)
            print("ppppp")
            for i in accounts:
                print(type(i))
            #print(accounts,account_status)
            if account_status is None:
                status = 'upload_different_document'
                return jsonify({
                    "upload_status":status
                })
            else:
               
                if account_status == "found":
                    account = accounts[0]
                    account_no = account['acc_no']

                    file_type = document_type
                    file_name = str(document_type)
                    # file_data = file_io
                    base64_file_data = encode_base64(extracted_text)

                    file_document = { 
                        'file_type' : file_type,
                        'file_name' : str(account_no) +"_"+file_name,
                        'file_data' : base64_file_data
                        
                    }

                    result = mongo_client.insert_document(account,file_document,document_type)

                    if result:
                        upload_status = 'success'
                        
                        
                    else:
                        upload_status = 'network_error'

                    folder_name1 = "Documents"
            
                    internal_folder_name1 = document_type

                    folder_id1 = create_or_get_folder(folder_name1)
                    nested_folder_id1 = create_nested_folders(internal_folder_name1,folder_id1)
                    file.seek(0)
                    with NamedTemporaryFile(delete=False) as temp_file1:
                        temp_file1.write(file.read())
                        temp_file1.flush()
                        temp_file1_path = temp_file1.name

                    res1 = upload_file_to_folder(temp_file1, str(account_no) +"_"+name, nested_folder_id1)


                    #Person-wise Heirarchy in Drive
                    
                    file.seek(0)

                    folder_name2 = "Account_Holders"

                    internal_folder_name2 = name

                    folder_id2 = create_or_get_folder(folder_name2)
                    nested_folder_id2 = create_nested_folders(str(account_no)+'_'+internal_folder_name2,folder_id2)

                    with NamedTemporaryFile(delete=False) as temp_file2:
                        temp_file2.write(file.read())
                        temp_file2.flush()
                        temp_file2_path = temp_file2.name

                    res2 = upload_file_to_folder(temp_file2, document_type, nested_folder_id2)
                    
                    print(res1,res2)
                    return jsonify({
                        "upload_status" : upload_status
                    })


                elif account_status == "list_of_accounts":
                    file_type = document_type
                    base64_file_data = encode_base64(extracted_text)
                    file_document = { 
                        'file_type' : file_type,
                        'file_data' : base64_file_data
                    }
                    
                    
                    new_accounts = []
                    for i in accounts:
                        new_dict = dict()
                        name = i['name']
                        acc_no = i['acc_no']
                        new_dict['name'] = name
                        new_dict['acc_no'] = acc_no
                        new_accounts.append(new_dict)

                    accounts = dict(new_accounts)
                    
                    upload_status = "display_accounts"

                    return jsonify({
                        "upload_status" : upload_status,
                        "file_document" : file_document,
                        "document_type" : document_type,
                        "accounts" : accounts
                    })
                
@app.route("/upload_file_selected_account",methods = ['POST'])
def upload_file_for_selected_account():
    
    mongo_client = MongoDB()
    
    data = request.json 

    file_document = data.get("file_document")
    document_type = data.get("document_type")
    account = data.get("account")
    file_document['file_name'] = account["acc_no"]+"_"+ document_type
    result = mongo_client.insert_document(account,file_document,document_type)

    if result:
        upload_status = 'success'                   
    else:
        upload_status = 'network_error'
    
    return jsonify({
        "upload_status" : upload_status
    })

@app.route("/chatbot_acc_no", methods = ['POST'])
def chatbot_account_no_confirmation():

    data = request.json
    account_no = data.get("account_no")

    mongo_client = MongoDB
    base64_documents_list, obj = mongo_client.retrieve_documents(account_no=account_no)

    document_text = ""

    for single_document in base64_documents_list:
        document_text += decode_base64(single_document)
    
    
    
    

    if document_text == "":
        return jsonify({
            "response" : "Unable to find documents."
        })
    else:
        d = dict(obj)
        account_str = ""
        for i in d.keys():
            account_str += str(i+":")
            account_str += str(d[i])
        reset_memory()
        load_document(document_text, account_str)
        
        return jsonify({
            "response":"Ok, ask queries."
        })

@app.route("/chatbot_response",methods=["POST"])
def chatbot_response():
    data = request.json 
    query = data.get("query")
    
    response = chatbot_answer(query=query)

    return jsonify({
        "response" : response
    })


@app.get('/shared/<task_id>')
def shared_url(task_id):
    return render_template('shared.html', task_id=task_id)




    




                
    
    


        
if __name__ == '__main__':
    app.run(debug=True)