import os
import time
import random
import requests
import json
from flask import Flask, request, jsonify, render_template, url_for, redirect
app = Flask(__name__)

#Setup some globals 
speciesName = ""
infoLink = ""
scientificName = ""
certainty = 0

#URL ROUTES

#Index page
@app.route("/")
def fileFrontPage():
    return render_template('view.html')

#Upload handler
@app.route("/handleUpload", methods=['POST'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':    
            split_file = photo.filename.split(".")
            file_extension = split_file[1].lower()
            accepted_filetypes = ["jpg", "jpeg", "ping", "png", "gif", "tif"]

            if file_extension in accepted_filetypes:
                filename = generateRandomFileName() + "." + file_extension
                photo.save(os.path.join('/home/trisivaw/public_html/isd_images/', filename))
                
                data = callImageRecognition(filename)
                
                if(data):
                    species = data["species"]
                    score = data["score"]
                    score = int(round(score, 2) * 100)
                
                    global speciesName 
                    global infoLink
                    global scientificName
                    global certainty
                    
                    certainty = score
                    
                    if(species == "PurpleLoosestrife"):
                        speciesName = "Purple Loosestrife"
                        scientificName = "Lythrum salicaria"
                        infoLink = "https://www.invasivespeciesinfo.gov/profile/purple-loosestrife"
                        
                    if(species == "BurmesePython"):
                        speciesName = "Burmese Python"
                        scientificName = "Python molurus bivittatus"
                        infoLink = "https://www.invasivespeciesinfo.gov/profile/burmese-python"
                        
                    if(species == "BrownMarmoratedStinkBug"):
                        speciesName = "Brown Marmorated Stink Bug"
                        scientificName = "Halyomorpha halys"
                        infoLink = "https://www.invasivespeciesinfo.gov/profile/brown-marmorated-stink-bug"
                        
                    return redirect(url_for('foundSpecies'))
                    
                return redirect(url_for('noSpeciesFound'))
            
    return redirect(url_for('uploadError'))
    
#Default error route
@app.route("/uploadError")
def uploadError():
    return render_template('error.html')

#Positive detection route
@app.route("/found")
def foundSpecies():
    species = speciesName
    return render_template('found.html', species = speciesName, info = infoLink, sciName = scientificName, score = certainty)
    
#Negative detection route
@app.route("/notFound")
def noSpeciesFound():
    return render_template('not_found.html')
    

#HELPER FUNCTIONS

#Give us a random filename to avoid conflicting names
def generateRandomFileName():
    return str(int(time.time()))
   
#call Watson visual recognition API @return: dict if true, False if no species found
def callImageRecognition(filename):

    #Setup POST parameters
    params = (('version', '2019-02-11'),)
    files = {
        'features': (None, 'objects'),
        'collection_ids': (None, '62ce6a8f-e933-4661-8e39-65382f07cd77'),
        'image_url': (None, 'https://tristan-scott.com/isd_images/' + filename),    
    }
    #POST the query data and get the response
    response = requests.post('https://gateway.watsonplatform.net/visual-recognition/api/v4/analyze', params=params, files=files, auth=('apikey', 'ZAaVKCnk1Ka1zhEi6LJ5pDF0fFv2hhmCZzTU3Fyr7ghb'))
    
    #Parse the response 
    #There's definitely a better way to do this but it works -\('-')/-
    resp = json.dumps(response.json())
    resp2 = json.loads(resp)

    #Check if the AI found anything and return the object 
    if 'collections' in resp2['images'][0]['objects']:
        species = resp2['images'][0]['objects']['collections'][0]['objects'][0]['object']
        score = resp2['images'][0]['objects']['collections'][0]['objects'][0]['score']
        returnable = {"species":species,"score":score}
        return returnable
    #Fallthrough if the AI failed to find anything
    return False
   

if __name__ == "__main__":
    app.run()
