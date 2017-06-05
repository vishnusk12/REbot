from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from config_updated import create_cache
from config_updated import top_classifier
#from config_updated import write_to_db
from model_building import build_model
from appos import welcome_note
from datetime import datetime
import dill
import base64
import json, requests
from pymongo import MongoClient
from dbauth import DATABASE_ACCESS
from dbauth_new import DATABASE_ACCESS

db_client = MongoClient("mongo-master.propmix.io", port=33017)
db_client.MLSLite.authenticate(**DATABASE_ACCESS)
db_client.chatbot.authenticate(**DATABASE_ACCESS)


@permission_classes((permissions.AllowAny,))
class Bot(viewsets.ViewSet):

    def create(self, request):
        CACHE_ID = 'CONSTANT5'
        question = request.data
        if 'user_id' in question:
            CACHE_ID = question['user_id']
        req_cache = create_cache(CACHE_ID)
        user_input = question['messageText']
        if question['messageSource'] == 'userInitiatedReset':
            req_cache.delete()
            question['messageSource'] = 'messageFromBot'
            question['messageText'] = welcome_note
            return Response(question)

        kern_RE = dill.loads(base64.b64decode(req_cache.user.aiml_kernel))
        question = build_model(question, kern_RE, req_cache.cache)
        if 'property' in question:
            req_cache.cache = question['property']
            req_cache.user.aiml_kernel = \
                base64.b64encode(dill.dumps(kern_RE))
            req_cache.user.save()
            req_cache.save()
        if len(question['property']) == 6:
        #if len(question['property']) == 8:
            try:
                URL = 'https://staging-api.propmix.io/mlslite/val/v1/GetListingsByGeo?access_token=863cccdf69e051a686e606a937550e88d7f502c3469eef12f736642f5ea678fb&EffectiveDate=2017-03-21&PropertySubType=%s&MlsStatus=Active&City=%s&State=%s&MaxBed=%s&MinArea=%s&MaxArea=%s&MinPrice=%s&MaxPrice=%s&MonthsBack=12&imagesON=1'%(str({key: value for d in req_cache.cache for key, value in d.iteritems()}['PropertySubType']).title(), str({key: value for d in req_cache.cache for key, value in d.iteritems()}['City']).title(), str({key: value for d in req_cache.cache for key, value in d.iteritems()}['State']).upper(), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['BedroomsTotal']), .5*float({key: value for d in req_cache.cache for key, value in d.iteritems()}['LivingArea']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['LivingArea']), .5*float({key: value for d in req_cache.cache for key, value in d.iteritems()}['ListPrice']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['ListPrice'])) 
                #URL = 'https://staging-api.propmix.io/mlslite/val/v1/GetListingsByGeo?access_token=863cccdf69e051a686e606a937550e88d7f502c3469eef12f736642f5ea678fb&EffectiveDate=2017-03-21&PropertySubType=%s&MlsStatus=Active&City=%s&State=%s&MaxBed=%s&MinArea=%s&MaxArea=%s&MinPrice=%s&MaxPrice=%s&MonthsBack=12&imagesON=1'%(str({key: value for d in req_cache.cache for key, value in d.iteritems()}['PropertySubType']).title(), str({key: value for d in req_cache.cache for key, value in d.iteritems()}['City']).title(), str({key: value for d in req_cache.cache for key, value in d.iteritems()}['State']).upper(), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['BedroomsTotal']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['minarea']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['maxarea']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['minprice']), float({key: value for d in req_cache.cache for key, value in d.iteritems()}['maxprice'])) 
                resp = requests.get(url=URL)
                data = json.loads(resp.text)
                result = []
                for i in data['Listings']:
                    dict_ = {}
                    dict_["ListPrice"] = i["ListPrice"]
                    dict_["SI_Address"] = i["Address"]
                    dict_["BedroomsTotal"] = i["BedroomsTotal"]
                    dict_["PropertySubType"] = i["PropertySubType"]
                    dict_["BathroomsTotalInteger"] = i["BathroomsTotalInteger"]
                    dict_["LivingArea"] = i["LivingArea"]
                    dict_["DaysOnMarket"] = i["DaysOnMarket"]
                    dict_['ImageURLs'] = i['ImageURLs']
                    result.append(dict_)
                newresult = sorted(result, key=lambda k: k['ListPrice'], reverse=True)
                newresult_ = sorted(newresult, key=lambda k: k['LivingArea'], reverse=True)
                print newresult_
                if len(result) != 0:
                    question['ResultBuyer'] = newresult_
                    question['messageText'] = ['Please find the search results I could gather']
                else:
                    question['messageText'] = ['No Matches found. For more details, you can log on to ']
                    question['link'] = ['http://icmalive.com/#/']
            except:
                question['messageText'] = ['No Matches found. For more details, you can log on to ']
                question['link'] = ['http://icmalive.com/#/']
            reply = question
            req_cache.delete()
            return Response(reply)
        elif len(question['property']) == 5 and {key: value for d in question["property"] for key, value in d.items()}.has_key('Email'):
            question['messageText'] = [['Thank You for your Valuable time.'], ['The CMA Report will be mailed to your Email ID.']]
            question['messageSource'] = 'messageFromUser'
            reply = question
            req_cache.delete()
            new_data = {'UnparsedAddress': str({key: value for d in reply["property"] for key, value in d.items()}['UnparsedAddress']).title(), 'City': str({key: value for d in reply["property"] for key, value in d.items()}['City']).title(), 'State': str({key: value for d in reply["property"] for key, value in d.items()}['State']).upper(), 'PostalCode': str({key: value for d in reply["property"] for key, value in d.items()}['PostalCode']), 'Email': str({key: value for d in reply["property"] for key, value in d.items()}['Email']), 'Address': str({key: value for d in reply["property"] for key, value in d.items()}['UnparsedAddress']).title() + ',' + ' ' + str({key: value for d in reply["property"] for key, value in d.items()}['City']).title() + ',' + ' ' + str({key: value for d in reply["property"] for key, value in d.items()}['State']).upper() + ' ' + str({key: value for d in reply["property"] for key, value in d.items()}['PostalCode']) + ',' + ' ' + 'USA'}
            db_client.chatbot.sellerinfo.update({'_id': {'UnparsedAddress': str({key: value for d in reply["property"] for key, value in d.items()}['UnparsedAddress']).title()}}, new_data, upsert=True)
#             date_time = str(datetime.now())
#             write_to_db(user_input, reply, date_time, CACHE_ID)
            return Response(reply)
        else:
            reply = question
#         date_time = str(datetime.now())
#         write_to_db(user_input, reply, date_time, CACHE_ID)
        return Response(reply)
