
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.externals import joblib
import MySQLdb
# from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
import random
import requests
# from nltk.corpus import stopwords
import string
# from chatter.views import list_symptoms
# stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
# st = LancasterStemmer()
final_respnses = ['diseases_found']
from appos import *


def write_to_db(text):
    db = MySQLdb.connect("192.168.0.28","user","kreara@1","ggc" )
    cursor = db.cursor()
    try:
        sql = """INSERT INTO ggc.chat_logs(text,user_id) VALUES ('%s',%s)""" %(text,1)
        cursor.execute(sql)
    except:
        pass
    db.commit()


def preprocess(text):
    words = text.split()
    reformed = [appos[word] if word in appos else word for word in words]
    reformed = " ".join(reformed)
    # reformed = [appos[word] if word in appos else word for word in tokens]
    tokens = word_tokenize(reformed)
    print 'tokens', tokens
    # stop_free = [i for i in tokens if i not in stop]
    punc_free = [ch for ch in tokens if ch not in exclude]
    normalized = [lemma.lemmatize(word).lower() for word in punc_free]
    return normalized


def create_symptom_string(text_cleaned):
    symptom_string = ''
    for i in text_cleaned:
        if i in symptoms_from_db:
            if len(symptom_string) == 0:
                symptom_string = symptom_string + i
            else:
                symptom_string = symptom_string + ',' + i
    return symptom_string


# def create_disease_string(text_cleaned):
#     disease_string = ''
#     for i in text_cleaned:
#         if i in disease_from_db:
#             if len(disease_string) == 0:
#                 disease_string = disease_string + i
#             else:
#                 disease_string = disease_string + ',' + i
#     return disease_string


def filter_symptoms(text):
    symptom_list = []
    # print text
    for i in text:
        if i in symptoms_from_db:
            dic = {}
            dic['symptomName'] = i
            dic['symptomFlag'] = True
            symptom_list.append(dic)
    return symptom_list


def remove_duplicates(symptoms, symptom_list):
    list_symptoms = []
    for i in symptom_list:
        list_symptoms.append(i["symptomName"])
    symptoms = [i for i in symptoms if i not in list_symptoms]
    return symptoms


def find_other_symptoms(symptom_list):
    search_string = ''
    symptoms = []
    for symptom in symptom_list:
        if symptom['symptomFlag']:
            search_string = search_string+','+symptom['symptomName']
    # link = 'http://indhaler.kreara.net:81/IndhalerWeb/rest/indhalarservice/relatedSymtoms?symptoms='+search_string
    link = 'http://192.168.0.136:8084/IndhalerWebService/api/indhalarservice/relatedSymtoms?symptoms='+search_string
    # import time
    # start = time.clock()
    # print start
    try:
        resp = requests.get(link)
        # print 'time taken to finish just after the call', time.clock() - start
        symptom_from_url = resp.json()
    except Exception as e:
        symptom_from_url = []
        print(e)
    # print 'time taken to finish', time.clock() - start
    if len(symptom_from_url) != 0:
        symptoms.extend(symptom_from_url)
    else:
        return ''
    if len(symptoms) != 0:
        symptoms = remove_duplicates(symptoms, symptom_list)
        if len(symptoms) != 0:
            return symptoms[0]
        else:
            return ''
    else:
        return ''


def get_cure(dict):
    cures = ''
    cure_list = dict["remedyVo"]
    for elements in cure_list:
        if len(cures) == 0:
            cures = cures + elements['remedy']
        else:
            cures = cures + ',' + elements['remedy']
    return cures


def get_disease(symptom):
    disease_string = ''
    cure_string = ''
    link = 'http://indhaler.kreara.net:81/IndhalerWeb/rest/indhalarservice/cure?symptoms='+symptom
    try:
        responses = requests.get(link)
        diseases_from_url = responses.json()
    except Exception as e:
        diseases_from_url = []
        print(e)
    if len(diseases_from_url) != 0:
        for diseases in diseases_from_url:
            cure = get_cure(diseases)
            if len(cure_string) == 0:
                cure_string = cure_string + cure
            else:
                cure_string = cure_string + ',' + cure
            if len(disease_string) == 0:
                disease_string = disease_string + diseases['disease']
            else:
                disease_string = disease_string + ' or ' + diseases['disease']
    if len(disease_string) != 0:
        return disease_string, len(diseases_from_url), cure_string
    else:
        return disease_string, 0, cure_string


def create_respose(suggested_symptom, question, responses):
    # print suggested_symptom, len(question['Symptoms'])
    if suggested_symptom != '' and len(question['Symptoms']) <= 5:
        question['SuggestingSymptom'] = suggested_symptom
        resp = 'Is ' + question['SuggestingSymptom'] + ' also a symptom'
        responses.append(resp)
        resp_ask = random.choice(responses)
        if len(question['Symptoms']) == 1:
            resp_ask = question['Symptoms'][0]["symptomName"] + ' is common for many diseases, ' + resp_ask
        if resp_ask.endswith('symptom'):
            question['Question'] = resp_ask + '?'
        else:
            question['Question'] = resp_ask + suggested_symptom + '?'
        return question
    elif suggested_symptom != '' and len(question['Symptoms']) > 5 :
        question['Question'] = final_respnses[0]
        return question
    elif suggested_symptom == '':
        question['Question'] = final_respnses[0]
        return question


def create_response_cure(diseases, cure, num_of_diseases, symptoms_user):
    symptoms_list = symptoms_user.split(',')
    response_to_symptom =['From the symptoms you are given, you may be suffering from ', 'You may be suffering from']
    response_to_cure = ['. You can try using ']
    cure = cure.split(',')
    if len(cure) > 5:
        cure = cure[0:4]
    cure = ', '.join(cure)
    if len(symptoms_list) <= 2:
        if len(symptoms_list) == 1:
            string = symptoms_user + disease_suggesion[0] + diseases + response_to_cure[0] + cure + ' as medicines.'
            return string
        else:
            string = symptoms_user + disease_suggesion[1] + diseases + response_to_cure[0] + cure + ' as medicines.'
            return string
    resp = random.choice(response_to_symptom) + ' ' + diseases + response_to_cure[0] + cure + ' as medicines.'
    return resp


def classifier(text):
    text_list = []
    text_list.append(str(text))
    clf = joblib.load('C:/Users/aneesh.c/workspace/RE_bot/model_files/model.pkl')
    label = clf.predict(text_list)
    return label[0]

def check_for_polarity(cleaned_user_input):
    return True


def remove_duplicates_from_collected_symptoms(list_of_dict):
    list = []
    for elements in list_of_dict:
        if elements not in list:
            list.append(elements)
    list_of_dict = list
    return list_of_dict


def generate_response(messageText_medical, question, suggested_symptom):
    symptom = []
    dic = {}
    dic['symptomName'] = suggested_symptom
    if messageText_medical == 'True':
        dic['symptomFlag'] = True
    else:
        dic['symptomFlag'] = False
    symptom.append(dic)
    question['Symptoms'].extend(symptom)
    
    suggested_symptom = find_other_symptoms(question['Symptoms'])
    question['SuggestingSymptom'] = suggested_symptom
    question['Question'] = random.choice(responses)+ suggested_symptom
    return question

#def remove_suggested_symptom(suggested_symptom):

def build_model(question, kern, kern_medical):
    responses = ['Do you have ', 'Are you disturbed with ', 'Are you suffering from ']
    if question['messageSource'] == 'symptomSearch':
        aiml_flag = False
    else:
        aiml_flag = True
    cleaned_user_input = preprocess(question['messageText'])
    symptoms_string = create_symptom_string(cleaned_user_input)
    if (len(symptoms_string) == 0 and aiml_flag):
        response = {}
        messageText = kern.respond(str(question['messageText']))
        response['messageText'] = messageText
        response['messageSource'] = 'messengerBot'
        return response
    else:
        label = classifier(question['messageText'])
        messageText_medical = kern_medical.respond(str(question['messageText']))
        print label, symptoms_string,messageText_medical
        if label == 1 and len(symptoms_string) != 0:
            response = {}
            diseases, num_of_diseases, cure = get_disease(symptoms_string)
            messageText = create_response_cure(diseases, cure, num_of_diseases, symptoms_string)
#                 elif len(disease_string) != 0:
#                     cures = get_cure_disease(disease_string)
#                     messageText = create_response_cure_disease(disease_string, cures)
            response['messageText'] = messageText
            response['messageSource'] = 'messengerBot'
     
            return response
        else:
            question['messageSource'] = 'symptomSearch'
            print cleaned_user_input
            polarity = check_for_polarity(cleaned_user_input)
            if polarity and question['SuggestingSymptom'] != '':
                symptom = []
                dic = {}
                dic['symptomName'] = question['SuggestingSymptom']
                dic['symptomFlag'] = True
                symptom.append(dic)
                question['Symptoms'].extend(symptom)
            
            symptoms_user = filter_symptoms(cleaned_user_input)
            #print symptoms_user

            if question.has_key('Symptoms'):
                question['Symptoms'].extend(symptoms_user)
            else:
                question['Symptoms'] = symptoms_user
            question['Symptoms'] = remove_duplicates_from_collected_symptoms(question['Symptoms'])
            suggested_symptom = find_other_symptoms(question['Symptoms'])
            
            print 'suggested symptom', suggested_symptom
            question['Question'] = messageText_medical
            #print symptom_user_flag
            if 'Are you disturbed with' in messageText_medical:
                question['Question'] = random.choice(responses) + suggested_symptom
                question['SuggestingSymptom'] = suggested_symptom
                del question['messageText']
                return question
            #question['Symptoms'] = remove_suggested_symptom(suggested_symptom)
            print question
            if messageText_medical == 'True' or messageText_medical == 'False':
                question = generate_response(messageText_medical, question, suggested_symptom)


                #question = create_respose(suggested_symptom, question, responses)
     
            del question['messageText']
            return question
