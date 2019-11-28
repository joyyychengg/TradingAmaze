from requests_oauthlib import OAuth2Session
from flask import Flask, render_template, redirect, url_for, request, session
from requests.auth import HTTPBasicAuth
import requests
import json
import hashlib
import mysql.connector
from mysql.connector import Error
from newsapi import NewsApiClient


app=Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = "fa85582d5f84f3ccb1023d3d2a1a0f85"

client_id = "5ba593eb4cc1417c"
client_secret = "fa85582d5f84f3ccb1023d3d2a1a0f85"

authorization_base_url = 'https://apm.tp.sandbox.fidor.com/oauth/authorize'
token_url = 'https://apm.tp.sandbox.fidor.com/oauth/token'
redirect_uri = 'http://localhost:5000/callback'

newsapi = NewsApiClient(api_key='8bc6779b465e45d19b1f0ab0d8e7db1a')


urlNQUSHEI = "https://www.quandl.com/api/v3/datasets/NASDAQOMX/NQUSHEI.json"
querystring = {"api_key":"w-zmuZcjFD5yEtgr8MCC"}

headers = {
    'User-Agent': "PostmanRuntime/7.20.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "e1a18a55-3497-44e8-89ec-70cdfa39e107,34c0009c-ccf0-425a-8caa-c014f937aef0",
    'Host': "www.quandl.com",
    'Accept-Encoding': "gzip, deflate",
    'Cookie': "__cfduid=d0cb0b7291ba0944b10dfdeb22a985fa51571887386",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response1 = requests.request("GET", urlNQUSHEI, headers=headers, params=querystring)



urlNASDAQOMX = "https://www.quandl.com/api/v3/datasets/NASDAQOMX/NQUSB8980.json"
querystring = {"api_key":"w-zmuZcjFD5yEtgr8MCC"}

headers = {
    'User-Agent': "PostmanRuntime/7.20.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "fde2d101-9ea2-42bf-ac66-bcd949206d46,668f8aa5-3cf9-49bb-802f-47991a762b45",
    'Host': "www.quandl.com",
    'Accept-Encoding': "gzip, deflate",
    'Cookie': "__cfduid=d0cb0b7291ba0944b10dfdeb22a985fa51571887386",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", urlNASDAQOMX, headers=headers, params=querystring)





@app.route('/', methods=['GET'])
def default():
    return render_template('mainpage.html')

@app.route('/LoginRegister', methods=['GET'])
def LoginRegister():
    return render_template('LoginRegister.html')

@app.route('/SingaporeEquity', methods=['GET'])
def SingaporeEquity():
    return render_template('SingaporeEquity.html')

@app.route('/UnitedStatesEquity', methods=['GET'])
def UnitedStatesEquity():
    return render_template('USEquity.html')

@app.route('/CrudeOils', methods=['GET'])
def CrudeOils():
    return render_template('CrudeOils.html')

@app.route('/CryptoCurrency', methods=['GET'])
def CryptoCurrency():
    return render_template('CryptoCurrency.html')

@app.route('/ForeignExchange', methods=['GET'])
def ForeignExchange():
    return render_template('ForeignExchange.html')

@app.route('/PreciousMetals', methods=['GET'])
def PreciousMetals():
    return render_template('PreciousMetals.html')


@app.route('/account',methods=['POST'])
def account():

    if request.method == "POST":
        user_mail = request.form['inputmailh']
        user_password = request.form['inputpasswordh']

        rec = select_customer(user_mail,user_password)
        if rec == None:
            print("Record is null")
        else:
            print("rec="+str(rec))
            print("\nPrinting each customer record")
            for row in rec:
                print("name = ", row[1])
       
    return render_template('account.html', tName=row[1])


def select_customer(email, passwordsalt):
    query = "SELECT * FROM customertable WHERE email = %s AND passwordsalt =%s"
    print("query="+query)
    args = (email, passwordsalt)

    try:
        conn = mysql.connector.connect(host='localhost', database='tradingamazedb', user='root', password='')

        cursor = conn.cursor()
        cursor.execute(query,args)
        records = cursor.fetchall()
        print("total number of rows in customer is: ", cursor.rowcount)
  
        print("Row Count = " + str(cursor.rowcount))
        if cursor.rowcount == 0:
            records = None
    
    except Error as e:
        print("Error reading data from MySQL Table", e)
    
    finally:
        if(conn.is_connected()):
            conn.close()
            cursor.close()
            print("MySQL connection is closed")
        return records


@app.route('/FidorBank', methods=['GET'])
def FidorBank():
    fidor = OAuth2Session(client_id,redirect_uri=redirect_uri)
    authorization_url, state = fidor.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    print("authorization URL is =" +authorization_url)
    return redirect(authorization_url)


@app.route("/callback", methods=["GET"])
def callback():
    fidor = OAuth2Session(state=session['oauth_state'])
    authorizationCode = request.args.get('code')
    body = 'grant_type="authorization_code&code=' +authorizationCode + '&redirect_uri=' + redirect_uri+ '&client_id=' +client_id
    auth = HTTPBasicAuth(client_id, client_secret)
    token = fidor.fetch_token(token_url, auth=auth,code=authorizationCode,body=body,method='POST')

    session['oauth_token'] = token
    return  redirect(url_for('.services'))

@app.route("/services", methods=["GET"])
def services():
    try:
        token = session['oauth_token']
        url = "https://api.tp.sandbox.fidor.com/accounts"

        payload =""
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Authorization': "Bearer " +token["access_token"],
            'cache-control': "no-cache",
            'Postman-Token': "2beeaf6812fdd3fe3851b6213f9da41a"
        }

        response = requests.request("GET", url, data=payload, headers=headers)
        print("services=" + response.text)
        customersAccount = json.loads(response.text)
        customerDetails = customersAccount['data'][0]
        customerInformation = customerDetails['customers'][0]
        session['fidor_customer'] = customersAccount

        return render_template('services.html', fID=customerInformation["id"],
            fFirstName=customerInformation["first_name"], fLastName=customerInformation["last_name"],
            fAccountNumber=customerDetails["account_number"],fBalance=(customerDetails["balance"]/100))

    except KeyError:
        print("Key error in services to return back to index")
        return redirect(url_for('FidorBank'))


@app.route('/NQUSHEI', methods=['GET'])
def NQUSHEI():
    return response1.text


@app.route('/NASDAQOMX',methods=['GET'])
def NASDAQOMX():
    return response.text

@app.route("/bank_transfer", methods=["GET"])
def transfer():
    try:
        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]

        return render_template('internal_transfer.html', fFIDOR=customerDetails["id"],
            fAccountNo=customerDetails["account_number"], fBalance=(customerDetails["balance"]/100))
        
    except KeyError:
        print("Key error in bank_transfer to return back to services")
        return redirect(url_for('.services'))

@app.route("/process", methods=["POST"])
def process():
    if request.method == "POST":
        token = session['oauth_token']
        customersAccount = session['fidor_customer']
        customerDetails = customersAccount['data'][0]

        fidorID = customerDetails['id']
        custEmail = request.form['customerEmailAdd']
        transfersAmt = int(float(request.form['transferAmount'])*100)
        transferRemarks = request.form[ 'transferRemarks']
        transactionID = request.form[ 'transactionID']

        url = "https://api.tp.sandbox.fidor.com/internal_transfers"

        payload = "{\n\t\"account_id\":\""+fidorID+"\",\n\t\"receiver\":\""+custEmail+"\",\n\t\"external_uid\":\""+transactionID+"\",\n\t\"amount\": \""+str(transfersAmt)+"\",\n\t\"subject\":\""+transferRemarks+"\"\n}"
        headers = {
            'Accept': "application/vnd.fidor.de;version=1;text/json",
            'Content-Type': "application/json",
            'Authorization': "Bearer "+token["access_token"],
            'Cache-Control': "no-cache",
            'Postman-Token': "c288cd82-5222-4003-933c-7e7db20d2bc9,343b2cf6-ba61-4521-9078-fc0bb584f4a6"
            }

        response = requests.request("POST", url, data=payload, headers=headers)

        print("process="+response.text)

        transactionDetails = json.loads(response.text)
        return render_template('transfer_result.html', fTransactionID=transactionDetails["id"],
            custEmail=transactionDetails["receiver"], fRemarks=transactionDetails["subject"],
            famount=(float(transactionDetails["amount"])/100),
            fRecipientName=transactionDetails["recipient_name"])
    





