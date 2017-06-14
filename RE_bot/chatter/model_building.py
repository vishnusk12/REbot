
from config_updated import preprocess
from config_updated import digits
from config_updated import get_state
from config_updated import get_area
from config_updated import get_property_subtype
from config_updated import get_zip
from config_updated import top_classifier
from config_updated import get_streetaddr
from config_updated import get_email
#from config_updated import digits_area
#from config_updated import digits_price
from random import shuffle
from _random import Random
import random
import requests
from appos import *


def get_city_api(state):
    state = state.lower()
    city = ''
    number_of_city = 0
    expansion = ''
    url = 'http://192.168.0.217:82/GraphService/graph/graphInterface/getResult'
    try:
        r = requests.post(url, state)
        expansion = r.json()[0]['nodeName']
        list_cities = r.json()[0]['outGoingNodeList'].keys()
        print 'dcfvgbhjkl', list_cities
        number_of_city = len(list_cities)
        for i in list_cities:
            if city == '':
                city = city + i
            else:
                city = city + ',' + i
    except:
        print 'filed to fetch results from db'
    return city, number_of_city, expansion, list_cities


def get_state_api(city):
    city = city.lower()
    state = ''
    number_of_states = 0
    url = 'http://192.168.0.217:82/GraphService/graph/graphInterface/getResult'
    try:
        r = requests.post(url, city)
        list_states = r.json()[0]['incomingNodeList'].keys()
        number_of_states = len(list_states)
        for i in list_states:
            if state == '':
                state = state + i
            else:
                state = state + ',' + i
    except:
        print 'filed to fetch results from db'
    return state, number_of_states, list_states


def generate_reply_for_cities_buy(reply, state):
    city, number_of_city, expansion, list_cities = get_city_api(state)
    first_reply = 'Ok, the state ' + expansion +' includes a total of ' + str(number_of_city) + ' number of cities including \
' + ','.join(list_cities[:10]) +' ..,etc.'
    second_reply = 'Tell me the city you are interested in state, ' + expansion
    reply['messageText'] = [[first_reply], [second_reply]]
    reply["plugin"] = {'name': 'autofill', 'type': 'City', 'data': list_cities}
    return reply


def generate_reply_for_cities_sell(reply, state):
    city, number_of_city, expansion, list_cities = get_city_api(state)
    first_reply = 'Ok, the state ' + expansion +' includes a total of ' + str(number_of_city) + ' number of cities including \
' + ','.join(list_cities[:10]) +' ..,etc.'
    second_reply = 'Tell me the city in which your property is located in state, ' + expansion
    reply['messageText'] = [[first_reply], [second_reply]]
    reply["plugin"] = {'name': 'autofill', 'type': 'City', 'data': list_cities}
    return reply


def generate_reply_buy(entity, reply, entity_list_available):
    if entity == 'PropertySubType':
        city = [i['City'] for i in reply['property'] if 'City' in i]
        if len(city) == 0:
            city = ''
        else:
            city = city[0]
        first_reply = ['choosing city, ' + city.title() + ' is a good option.', city.title() + '\
 is a nice place you can look into.', city.title() + ' is a nice choice', 'That definitely seems like ' + city.title() + ' is a lovely place to settle']
        if city != '':
            reply['messageText'] = [[random.choice(first_reply)], [random.choice(property_question)]]
            reply["plugin"] = {'name': 'autofill', 'type': 'PropertyType', 'data': ['Condominium', 'Duplex', 'Farm', 'Manufactured Home', 'Manufactured on Land', 'Mobile Home', 'Multi Family > 4', 'Multi Family > 5', 'Multi Family > 6', 'Quadruplex', 'Residential', 'Single Family Residence', 'Stock Cooperative', 'Timeshare', 'Townhouse', 'Triplex']}
        else:
            reply['messageText'] = [[random.choice(fillers_buy)], [random.choice(property_question)]]
            reply["plugin"] = {'name': 'autofill', 'type': 'PropertyType', 'data': ['Condominium', 'Duplex', 'Farm', 'Manufactured Home', 'Manufactured on Land', 'Mobile Home', 'Multi Family > 4', 'Multi Family > 5', 'Multi Family > 6', 'Quadruplex', 'Residential', 'Single Family Residence', 'Stock Cooperative', 'Timeshare', 'Townhouse', 'Triplex']}
        return reply
    elif entity == 'City':
        state = [i['State'] for i in reply['property'] if 'State' in i]
        if len(state) == 0:
            state = ''
        else:
            state = state[0]
        if state != '':
            reply = generate_reply_for_cities_buy(reply, state)
            return reply
        else:
            reply['messageText'] = ['In which city you are interested to look into?']
            reply["plugin"] = {'name': 'autofill', 'type': 'City', 'data': available_region}
            return reply
    elif entity == 'BedroomsTotal':
        reply['messageText'] = [random.choice(bed_rooms)]
        reply["plugin"] = {'name': 'counter', 'type': 'bed', 'default': '5'}
        return reply
    elif entity == 'LivingArea':
        reply['messageText'] = [[random.choice(fillers_buy)], [random.choice(living_area)]]
        reply["plugin"] = {'name': 'range', 'type': 'area_range', 'data': [{"minarea": "500", "maxarea": "2500"}, {"minarea": "2501", "maxarea": "5000"}, {"minarea": "5001", "maxarea": "7500"}, {"minarea": "7501", "maxarea": "9999"}]}
        return reply
    elif entity == 'ListPrice':
        reply['messageText'] = [[random.choice(fillers_buy)], [random.choice(list_price)]]
        reply["plugin"] = {'name': 'range', 'type': 'price_range', 'data': [{"minprice": "10000", "maxprice": "300000"}, {"minprice": "300001", "maxprice": "500000"}, {"minprice": "500000", "maxprice": "1000000"}, {"minprice": "1000001", "maxprice": "2000000"}, {"minprice": "2000001", "maxprice": "3000000"}, {"minprice": "3000001", "maxprice": "5000000"}, {"minprice": "5000001", "maxprice": "10000000"}]}
        return reply


def generate_reply_sell(entity, reply, entity_list_available):
    if entity == 'City':
        state = [i['State'] for i in reply['property'] if 'State' in i]
        if len(state) == 0:
            state = ''
        else:
            state = state[0]
        if state != '':
            reply = generate_reply_for_cities_sell(reply, state)
            return reply
        else:
            reply['messageText'] = ['Please enter the city in which your property is located?']
            reply["plugin"] = {'name': 'autofill', 'type': 'City', 'data': available_region}
            return reply
    elif entity == 'UnparsedAddress':
        reply['messageText'] = [[random.choice(fillers_sell)], [random.choice(street)]]
        return reply
    elif entity == 'PostalCode':
        reply['messageText'] = [random.choice(post)]
        return reply
    elif entity == 'Email':
        reply['messageText'] = [[random.choice(fillers_sell)], [random.choice(mail)]]
        return reply


def build_model(question, kern_medical, symp_list):
    input = question['messageText']
    cleaned_user_input = preprocess(question['messageText'])
    question['messageText'] = cleaned_user_input
    kernel_reply = kern_medical.respond(question['messageText'])
    if not "Sorry, I didn't get you.." in kernel_reply:
        response = {}
        response['property'] = []
        response['messageText'] = [kernel_reply]
        return response
    response = {}
    response['property'] = []
    response['property'].extend(symp_list)
    t_label = top_classifier(question['messageText'])
    if t_label == 1 and question['messageSource'] == 'messageFromUser':
        response['property'] = get_state(question['messageText'], response['property'])
        response['property'] = get_area(question['messageText'], response['property'])
        response['property'] = get_property_subtype(question['messageText'], response['property'])
        response['property'] = digits(question['messageText'], response['property'])
        #response['property'] = digits_area(question['messageText'], response['property'])
        #response['property'] = digits_price(question['messageText'], response['property'])
        entity_list_buy = ['State', 'City', 'PropertySubType', 'BedroomsTotal', 'LivingArea', 'ListPrice']
        #entity_list_buy = ['State', 'City', 'PropertySubType', 'BedroomsTotal', 'minarea', 'maxarea', 'minprice', 'maxprice']
        entity_list_available_buy = [i.keys()[0] for i in response['property']]
        #shuffle(entity_list_buy)
        entity_list_buy = [i for i in entity_list_buy if i not in entity_list_available_buy]
        for i in entity_list_buy:
            if i == 'State':
                city = [i['City'] for i in response['property'] if 'City' in i]
                if len(city) != 0:
                    states, number_of_states, list_states = get_state_api(city[0])
                    if number_of_states >= 2:
                        response['messageText'] = [['City like ' +  city[0].title() +  ' are there in ' +  str(number_of_states) +  ' states including '+  states +'..,etc.'], ['Please tell me the exact state']] 
                        response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': list_states}
                    else:
                        response['messageText'] = [random.choice(state)]
                        response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': list_states}
                    return response
                else:
                    response['messageText'] = [random.choice(state)]
                    response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'district of columbia', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',  'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']}
                return response
            elif i not in entity_list_available_buy:
                response = generate_reply_buy(i, response, entity_list_available_buy)
                print response
                return response
            else:
                continue
        return response
    elif t_label == 2 or question['messageSource'] == 'sellerFlag':
        if question['messageSource'] == 'messageFromUser':
            response = {}
            response['property'] = []
            response['messageText'] = [['Ohh..Great..This is the right time to sell your property.'], [street_address]]
            response['messageSource'] = 'sellerFlag'
            return response
        elif question['messageSource'] == 'sellerFlag':
            response['property'] = get_state(question['messageText'], response['property'])
            response['property'] = get_area(question['messageText'], response['property'])
            response['property'] = get_zip(question['messageText'], response['property'])
            response['property'] = get_streetaddr(input, response['property'])
            response['property'] = get_email(input, response['property'])
            entity_list_sell = ['UnparsedAddress', 'City', 'State', 'PostalCode', 'Email']
            entity_list_available_sell = [j.keys()[0] for j in response['property']]
            entity_list_sell = [j for j in entity_list_sell if j not in entity_list_available_sell]
            for j in entity_list_sell:
                if j == 'State':
                    city = [j['City'] for j in response['property'] if 'City' in j]
                    if len(city) != 0:
                        states, number_of_states, list_states = get_state_api(city[0])
                        if number_of_states >= 2:
                            response['messageText'] = [['City like ' +  city[0].title() +  ' are there in ' +  str(number_of_states) +  ' states including '+  states +'..,etc.'], ['Please tell me the exact state']] 
                            response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': list_states}
                            response['messageSource'] = 'sellerFlag'
                        else:
                            response['messageText'] = ['Tell me the exact State']
                            response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': list_states}
                            response['messageSource'] = 'sellerFlag'
                        return response
                    else:
                        response['messageText'] = ['Tell me the exact State']
                        response["plugin"] = {'name': 'autofill', 'type': 'State', 'data': ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'district of columbia', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',  'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']}
                        response['messageSource'] = 'sellerFlag'
                    return response
                elif j not in entity_list_available_sell:
                    response = generate_reply_sell(j, response, entity_list_available_sell)
                    response['messageSource'] = 'sellerFlag'
                    return response
                else:
                    continue
            return response
        return response
    elif t_label == 3 and "Sorry, I didn't get you.." in kernel_reply:
        response['messageText'] = ['Please Ask Something related to Real Estate domain']
        return response
