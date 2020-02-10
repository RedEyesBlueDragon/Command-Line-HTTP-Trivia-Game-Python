#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from random import shuffle
import json, random, re
import time 
from datetime import datetime  
from datetime import timedelta

class RequestHandler(BaseHTTPRequestHandler):

    question_number = 0
    
    i=0
    ID = 0
    amount = 0
    current_question = 0
    remain = 0
    correct_number = 0
    is_answer = False
    j=0

    def say_hello(self, query):
        """
        Send Hello Message with optional query
        """
        mes = "Hello"
        if "name" in query:
            # query is params are given as array to us
            mes += " " + "".join(query["name"])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str.encode(mes+"\n"))

    def do_GET(self):
        # Parse incoming request url
        url = urlparse(self.path)
        if url.path == "/hello":
            return self.say_hello(parse_qs(url.query))

        if url.path == "/answer":
            return self.say_answer(parse_qs(url.query))    

        if url.path == "/next":
            return self.say_question(parse_qs(url.query)) 

        if url.path == "/newGame":
            return self.new_game(parse_qs(url.query))

                    
        # return 404 code if path not found
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found!\n')


    def new_game(self, query):
        
        # if amount is given create new game
        if "amount" in query: 
            RequestHandler.i = random.randint(0,30)         # choose random number to use different part of json file
            RequestHandler.ID = random.randint(0,89)        # give random id for sesion

            # initialize some variable
            RequestHandler.question_number = 1  
            RequestHandler.amount = int(query['amount'][0]) 
            RequestHandler.remain = RequestHandler.amount   
            RequestHandler.current_question = 0
            RequestHandler.correct_number = 0

            self.send_response(200)
            self.end_headers()
                
             
            self.wfile.write(str.encode("New Trivia Game started" + "\n"))
            self.wfile.write(str.encode("Session ID = " + str(RequestHandler.ID )+ "\n"))

        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode("error: no amount" +"\n"))

        
    def say_question(self, query):    
        
        
        # open json file
        with open ('carz.json') as json_file:
            data = json.load(json_file)

            n = RequestHandler.i
            

            self.send_response(200)
            self.end_headers()
                
            # check id and remaining question number    
            if RequestHandler.remain == 0 and str(query['id'][0]) == str(RequestHandler.ID):
                self.wfile.write(str.encode("error: session over" + "\n"))

            elif RequestHandler.remain == 0:
                  self.wfile.write(str.encode("error: invalid session" + "\n"))

            elif str(query['id'][0]) == str(RequestHandler.ID):

                RequestHandler.j = datetime.now()   # start the time

                RequestHandler.is_answer = False
                RequestHandler.current_question = RequestHandler.current_question + 1                
                RequestHandler.remain = RequestHandler.remain - 1
                RequestHandler.i = RequestHandler.i + 1

                number = RequestHandler.question_number
                RequestHandler.question_number = RequestHandler.question_number + 1
                category = data["results"][n]["category"]
                question = data["results"][n]["question"]
                    
                array = []
                array.append ( data["results"][n]["incorrect_answers"][0] ) 
                array.append ( data["results"][n]["incorrect_answers"][1] ) 
                array.append ( data["results"][n]["incorrect_answers"][2] ) 
                array.append ( data["results"][n]["correct_answer"] )   

                answer = random.randint(0,3)
                
                # randomize orders of answers 
                shuffle(array)
                
                self.wfile.write(str.encode("Question :"+ str(number) + "\n"))
                self.wfile.write(str.encode("Category: "+ category +"\n"))
                self.wfile.write(str.encode("Question: "+ question +"\n"))
                self.wfile.write(str.encode("\n"))

                self.wfile.write(str.encode("Answers: " +"\n"))
                
                self.wfile.write(str.encode("- " + array[0] +"\n"))
                self.wfile.write(str.encode("- " + array[1] +"\n"))
                self.wfile.write(str.encode("- " + array[2] +"\n"))
                self.wfile.write(str.encode("- " + array[3] +"\n"))

                self.wfile.write(str.encode("\n"))
                self.wfile.write(str.encode("You have 15 seconds to answer!" + "\n"))
                
            else:
                self.wfile.write(str.encode("error: invalid session id" +"\n"))
                        
            
    def say_answer(self, query):


        n = RequestHandler.i -1 

        self.send_response(200)
        self.end_headers()

        ctime = datetime.now()   
        differce = RequestHandler.j + timedelta(seconds=15)     # check the time for answering  

         
        #check session id
        if str(query['id'][0]) == str(RequestHandler.ID):

            # if greater than 15 doesnt accept answer
            if ctime > differce:
                self.wfile.write(str.encode("time out" +"\n"))
                self.wfile.write(str.encode("\n"))
                self.wfile.write(str.encode(str(RequestHandler.correct_number) + " correct of " + str(RequestHandler.current_question) + " questions" +"\n"))
                self.wfile.write(str.encode("\n"))   
                self.wfile.write(str.encode("There are " + str(RequestHandler.remain) + " more questions" +"\n"))

            # check is already answered    
            elif RequestHandler.is_answer == True:
                self.wfile.write(str.encode("error: already answered" +"\n"))

            elif "answer" in query:

                # open json file take answer and compare with answer of the user
                with open ('carz.json') as json_file:
                    data = json.load(json_file)

                    RequestHandler.is_answer = True
                    
                    if str(query['answer'][0]) == data["results"][n]["correct_answer"]:
                        RequestHandler.correct_number = RequestHandler.correct_number + 1

                        self.wfile.write(str.encode("CORRECT ANSWER!!" +"\n"))  
                        self.wfile.write(str.encode("\n"))
                        self.wfile.write(str.encode(str(RequestHandler.correct_number) + " correct of " + str(RequestHandler.current_question) + " questions" +"\n"))
                        self.wfile.write(str.encode("\n"))   
                        self.wfile.write(str.encode("There are " + str(RequestHandler.remain) + " more questions" +"\n")) 

                    else:    
                        self.wfile.write(str.encode("INCORRECT ANSWER!!" +"\n")) 
                        self.wfile.write(str.encode("\n"))
                        self.wfile.write(str.encode("Answer: " + str(data["results"][n]["correct_answer"]) + "\n"))
                        self.wfile.write(str.encode("\n"))
                        self.wfile.write(str.encode(str(RequestHandler.correct_number) + " correct of " + str(RequestHandler.current_question) + " questions" +"\n"))
                        self.wfile.write(str.encode("\n"))   
                        self.wfile.write(str.encode("There are " + str(RequestHandler.remain) + " more questions" +"\n"))     

            else:
                self.wfile.write(str.encode("error: no answer" +"\n"))        
        else:
            self.wfile.write(str.encode("error: invalid session id" +"\n"))    





if __name__ == "__main__":
    port = 8080
    print('Listening on localhost:{port}')
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()
