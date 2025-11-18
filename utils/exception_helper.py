from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST
import jdatetime
from math import radians, cos, sin, asin, sqrt
from requests import Session
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
import html
import re


class BadRequest(APIException):
    status_code = HTTP_400_BAD_REQUEST


def to_miladi(_date):
    eleman = _date[:5]
    eleman = eleman[-1:]
    _date = _date.split(eleman)
    _date = jdatetime.date(day=int(_date[2]), month=int(_date[1]), year=int(_date[0])).togregorian()
    return _date


def checknumber(serial):
    serial = serial.replace('۰', '0')
    serial = serial.replace('۱', '1')
    serial = serial.replace('۲', '2')
    serial = serial.replace('۳', '3')
    serial = serial.replace('۴', '4')
    serial = serial.replace('۵', '5')
    serial = serial.replace('۶', '6')
    serial = serial.replace('۷', '7')
    serial = serial.replace('۸', '8')
    serial = serial.replace('۹', '9')

    return serial


def SendSmS(phone_number, _message):
    message = _message.format(phone=phone_number)

    username = "sookht_75948"
    password = "KFZCrSjbGsOOmlRK"
    domain = "magfa"

    # session
    session = Session()
    # basic auth
    session.auth = HTTPBasicAuth(username + '/' + domain, password)

    # soap
    wsdl = 'https://sms.magfa.com/api/soap/sms/v2/server?wsdl'
    client = Client(wsdl=wsdl, transport=Transport(session=session))
    # data
    messages = client.get_type('ns1:stringArray')
    senders = client.get_type('ns1:stringArray')
    recipients = client.get_type('ns1:stringArray')
    uids = client.get_type('ns1:longArray')
    encodings = client.get_type('ns1:intArray')
    udhs = client.get_type('ns1:stringArray')
    priorities = client.get_type('ns1:intArray')

    # call
    try:
        resp = client.service.send(messages(item=[message, ]), senders(item=["300075948", ]),
                                   recipients(item=[phone_number, ]), uids(item=[]),
                                   encodings(item=[0]), udhs(item=[]), priorities(item=[]))

        if resp.status == 0:
            return 0
        else:
            return resp.status
    except Exception as e:
        pass


def zoneorarea(request):
    _roleid = 0
    if request.user.owner.role.role in ['zone', 'engin']:
        _roleid = request.user.owner.zone_id
    elif request.user.owner.role.role == 'area':
        _roleid = request.user.owner.area_id
    elif request.user.owner.role.role == 'tek':
        _roleid = request.user.owner.id
    elif request.user.owner.role.role == 'gs':
        _roleid = request.user.owner.id
    return _roleid


def checkxss(val):
    val = re.sub(r'<[^>]*>', '', val)
    return html.escape(val)


def distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result

    return (c * r * 1000)


# driver code
# lat1 = 35.536917
# lat2 = 35.536907
# lon1 = 51.197899
# lon2 =  51.197899
# print(distance(lat1, lat2, lon1, lon2)*1000, "K.M")


distance(31.497324, 31.497080, 50.812733, 50.812592)
