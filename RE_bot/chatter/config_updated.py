
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.externals import joblib
#import MySQLdb
from .models import RequestCache
import dill
import aiml
from appos import *
from nltk.tokenize import word_tokenize
import random
import requests
import string
import re
import os
from nltk.tag.stanford import StanfordNERTagger
from chatter.models import UserCache

exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
brain_file_medical = "standard_RE.brn"


# def write_to_db(user_input, reply, date_time, user_id):
#     try:
#         db = MySQLdb.connect("192.168.0.28", "user", "kreara@1", "ggc")
#         cursor = db.cursor()
#         user_input = user_input.encode('utf-8').translate(None, string.punctuation)
#         reply = reply['messageText'][0].encode('utf-8').translate(None, string.punctuation)
#         sql = """INSERT INTO ggc.chat_logs_re(user_input,bot_response,date_time,\
# user_id) VALUES ('%s','%s', '%s', '%s')""" % (
#                                               user_input,
#                                               reply,
#                                               date_time,
#                                               user_id
#                                               )
#         cursor.execute(sql)
#         db.commit()
#     except Exception as e:
#         print e
#         print 'Db is not getting connected'
#         pass

def preprocess(text):
    text = text.replace(',', ' ')
    words = text.split()
    reformed = [appos[word] if word in appos else word for word in words]
    reformed = " ".join(reformed)
    tokens = word_tokenize(reformed)
    punc_free = [ch for ch in tokens if ch not in exclude]
    normalized = [lemma.lemmatize(word).lower() for word in punc_free]
    reformed = " ".join(normalized)
    return reformed


def digits(text, cache_list):
    list_ = re.findall(r'(\d{1,9})', text)
    dict_ = {}
    if len(list_) != 0:
        for i in list_:
            if len(str(i)) <= 2:
                dict_ = {}
                dict_['BedroomsTotal'] = i
                cache_list = remove_duplicate(cache_list, 'BedroomsTotal')
                cache_list.append(dict_)
            elif len(str(i)) > 2 and len(str(i)) < 5:
                dict_ = {}
                dict_['LivingArea'] = i
                cache_list = remove_duplicate(cache_list, 'LivingArea')
                cache_list.append(dict_)
            else:
                dict_ = {}
                dict_['ListPrice'] = i
                cache_list = remove_duplicate(cache_list, 'ListPrice')
                cache_list.append(dict_)
    else:
        for key, value in bed.items():
            for j in value:
                match = re.compile(r"\b%s\b"%(j))
                num = match.findall(text)
                if len(num) != 0:
                    dict_ = {}
                    dict_['BedroomsTotal'] = key
                    cache_list = remove_duplicate(cache_list, 'BedroomsTotal')
                    cache_list.append(dict_)
    return cache_list

# def digits_area(text, cache_list):
#     try:
#         list_ = re.findall(r'(\d{1,9})', text)
#         if len(list) != 0:
#             l = []
#             for i in list_:
#                 if len(str(i)) > 2 and len(str(i)) < 5:
#                     l.append(i)
#             dict = {}
#             if len(l) == 2:
#                 dict['minarea'] = float(l[0])
#                 dict['maxarea'] = float(l[1])
#             else:
#                 dict['minarea'] = float(l[0])/2
#                 dict['maxarea'] = float(l[0])
#             cache_list = remove_duplicate(cache_list, 'minarea')
#             cache_list = remove_duplicate(cache_list, 'maxarea')
#             cache_list.append(dict)
#             return cache_list
#         else:
#             return cache_list
#     except:
#         return cache_list
#
#
# def digits_price(text, cache_list):
#     try:
#         list_ = re.findall(r'(\d{1,9})', text)
#         if len(list) != 0:
#             l = []
#             for i in list_:
#                 if len(str(i)) >= 5:
#                     l.append(i)
#             dict = {}
#             if len(l) == 2:
#                 dict['minprice'] = float(l[0])
#                 dict['maxprice'] = float(l[1])
#             else:
#                 dict['minprice'] = float(l[0])/2
#                 dict['maxprice'] = float(l[0])
#             cache_list = remove_duplicate(cache_list, 'minprice')
#             cache_list = remove_duplicate(cache_list, 'maxprice')
#             cache_list.append(dict)
#             return cache_list
#         else:
#             return cache_list
#     except:
#         return cache_list



def create_cache(CACHE_ID):
    import base64
    try:
        req_cache = RequestCache.objects.get(cache_id=CACHE_ID)
    except RequestCache.DoesNotExist: 
        kern_medical = aiml.Kernel()
        kern_medical.bootstrap(brainFile=brain_file_medical)
        kernel_str = dill.dumps(kern_medical)
        kernel_str = base64.b64encode(kernel_str)
        req_cache = RequestCache.objects.create(cache_id=CACHE_ID, cache=[],
                                                user=UserCache.objects
                                                .create(aiml_kernel=kernel_str)
                                                )
    return req_cache


def get_state(text, cache_list):
    dict_state = {}
    text = text.lower()
    text = re.sub(r'\bin\b', 'near', text)
    text = re.sub(r'\bme\b', 'myself', text)
    text = re.sub(r'\bor\b', 'near', text)
    text = re.sub(r'\bhi\b', 'hai', text)
    #text = text.split()
    for key, value in available_state.items():
        for i in value:
            #if i in text:
            match = re.compile(r"\b%s\b"%(i))
            area_name = match.findall(text)
            if len(area_name) != 0:
                dict_state['State'] = key
                print dict_state['State']
                cache_list = remove_duplicate(cache_list, 'State')
                cache_list.append(dict_state)
            else:
                pass
    return cache_list


def get_area(text, cache_list):
    dict_area_name = {}
    text = text.lower()
    for i in available_region:
        match = re.compile(r"\b%s\b"%(i))
        area_name = match.findall(text)
        if len(area_name) != 0:
            dict_area_name['City'] = area_name[0]
            cache_list = remove_duplicate(cache_list, 'City')
            cache_list.append(dict_area_name)
            return cache_list
#     if not dict_area_name.has_key('City'):
#         if not {key: value for d in cache_list for key, value in d.iteritems()}.has_key('City'):
#             java_path = 'C:\Program Files (x86)\Java\jdk1.8.0_05\\bin\java.exe'
#             os.environ['JAVAHOME'] = java_path
#             st = StanfordNERTagger('C:/Users/vishnu.sk/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser','C:/Users/vishnu.sk/Downloads/stanford-ner-2014-06-16/stanford-ner-3.4.jar')
#             if 'near' in text:
#                 text = re.sub(r'\bnear\b', 'in', text)
#             elif len(text.split()) == 1:
#                 text = 'in' + ' ' + text
#             else:
#                 text = text
#             tagged_text = st.tag(text.title().split())
#             print tagged_text
#             area = []
#             for location in tagged_text:
#                 if location[1] == 'LOCATION':
#                     cache_list = remove_duplicate(cache_list, 'City')
#                     area.append(location[0])
#             if len(area) != 0:
#                 print len(area)
#                 print cache_list
#                 dict_area_name['City'] = " ".join(area)
#                 cache_list.append(dict_area_name)
#                 print cache_list
    return cache_list



def get_property_subtype(text, cache_list):
    text = text.lower()
    for key, value in property_subtype.items():
        for i in value:
            match = re.compile(r"\b%s\b"%(i))
            prop = match.findall(text)
            if len(prop) != 0:
                dict_property = {}
                dict_property['PropertySubType'] = key
                cache_list = remove_duplicate(cache_list, 'PropertySubType')
                cache_list.append(dict_property)
    return cache_list


def get_streetaddr(input, cache_list):
    dict_addr = {}
    try:
        list_ = re.search(r'(\b\d{0,9}(?:\s[a-zA-Z\u00C0-\u017F]+)+|([a-zA-Z\u00C0-\u017F]+\s[a-zA-Z\u00C0-\u017F]+\s+\d{0,9})|([a-zA-Z\u00C0-\u017F]\s+\d{0,9}[a-zA-Z\u00C0-\u017F]+))', input).group(0)
        if list_ is not None:
            dict_addr['UnparsedAddress'] = list_
            print dict_addr
            cache_list = remove_duplicate(cache_list, 'UnparsedAddress')
            cache_list.append(dict_addr)
            return cache_list
        else:
            return cache_list
    except:
        return cache_list


def get_zip(text, cache_list):
    dict_zip = {}
    list_ = re.findall(r'(\d{1,9}\s{0,})', text)
    if len(list_) != 0:
        for i in list_:
            if len(str(i)) == 5 or len(str(i)) == 6:
                dict_zip['PostalCode'] = i
                cache_list = remove_duplicate(cache_list, 'PostalCode')
                cache_list.append(dict_zip)
    return cache_list


def get_email(input, cache_list):
    dict_email = {}
    try:
        res = re.search("([^@|\s]+@[^@]+\.[^@|\s]+)", input, re.I)
        if res is not None:
            dict_email['Email'] = res.group(1)
            cache_list = remove_duplicate(cache_list, 'Email')
            cache_list.append(dict_email)
            return cache_list
        else:
            return cache_list
    except:
        return cache_list


def top_classifier(text):
    text_list = []
    text_list.append(str(text))
    clf = joblib.load('C:/Users/vishnu.sk/workspace/RE_bot/model_files/model_top.pkl')
    t_label = clf.predict(text_list)
    return t_label[0]


def buy_classifier(text):
    text_list = []
    text_list.append(str(text))
    clf = joblib.load('C:/Users/vishnu.sk/workspace/RE_bot/model_files/model.pkl')
    b_label = clf.predict(text_list)
    return b_label[0]


def remove_duplicate(list_, key_name):
    if len(list_) != 0:
        for dicts in list_:
            if dicts.has_key(key_name):
                list_.remove(dicts)
    return list_
