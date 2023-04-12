from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import csv

logging.basicConfig(filename= "scrapper.log", level= logging.INFO)

application = Flask(__name__)
app = application

@app.route('/', methods = ['GET'])
#@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review', methods = ['POST', 'GET'])
#@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipcart_url = "https://www.flipkart.com/search?q=" + searchString 
            uclient = uReq(flipcart_url)
            flipkartPage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartPage ,"html.parser")
            bigboxes = flipkart_html.findAll("div" , {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productlink = "https://www.flipkart.com"+box.div.div.div.a['href']
            productreq = requests.get(productlink)
            productreq.encoding = 'utf-8'
            prod_html = bs(productreq.text,"html.parser")
            print(prod_html)
            comment_box = prod_html.find_all("div", {"class" : "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            
            for commentbox in comment_box:
                try:
                    #name.encode(encoding = 'utf-8')
                    name = commentbox.div.div.find_all("p" ,{"class" :"_2sc7ZR _2V5EHH"})[0].text
                except:
                    name = "No name"
                    logging.info(name)

                try:
                    #rating.encode(encoding = 'utf-8')
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = "No rating"
                    logging.info(rating)
                
                try:
                    #rating.encode(encoding = 'utf-8')
                    comment_head = commentbox.div.div.div.p.text
                except:
                    comment_head = "No comment heading"
                    logging.info(comment_head)

                try:
                    comtag = commentbox.div.div.find_all("div", {"class" :" "})
                    #custComment.encode(encoding = 'utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary:" ,e)
                
                mydict = {"Product": searchString, "Name": name, "Rating": rating,
                    "CommentHead": comment_head, "Comment": custComment}
                reviews.append(mydict)
            logging.info("Log my final result {}".format(reviews))
            return render_template('result.html', reviews = reviews[0:(len(reviews)-1)])

        except Exception as e:
            logging.info(e)
            return "Something is wrong"
    #return render_template("result.html")

    else:
        return render_template("index.html")

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8000)
