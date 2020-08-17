from flask import Flask, render_template, request
from recipe_scrapers import scrape_me
import sqlite3
app = Flask(__name__)  # create  app instance


@app.route("/")
def index():  # Home page of the KitchenCompanion app
    return render_template('index.html', title = 'Home')

@app.route("/view")  # Connects to database, fetches all records, and returns view.html to display list
def view():
    con = sqlite3.connect("test.db")  #Open Connection to DB
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from recipes")  
    rows = cur.fetchall()  
    return render_template('view.html', rows = rows, title = 'View Recipes')
    
@app.route("/add",methods = ["POST","GET"])  # Form page to input recipe URL to be added to DB
def add():
    con = sqlite3.connect("test.db")  #Open Connection to DB
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from sources")  
    webrows = cur.fetchall()  
    return render_template('add.html', webrows = webrows, title = 'Add Recipes')

@app.route("/save",methods = ["POST","GET"])  # Accepts add.html form URL, uses recipe_scrapers package, returns recipe strings. Adds each to DB
def save():
    msg = "msg"      # For displaying status message if recipe was added    
    if request.method == "POST":
        try:  
            recipe = request.form["recipe"]  
            scraper = scrape_me(recipe) # url as a string, it can be url from any site listed in the README
            title = scraper.title() #returned as str
            totalTime = scraper.total_time() #returned as int
            yields = scraper.yields() #returned as str
            ingredientsList = scraper.ingredients() #returned as list
            seperator = ', ' #For ingredients returned as list
            ingredientsString = seperator.join(ingredientsList)   # Ingredients list to string
            instructions = scraper.instructions() #returned as str
                
            with sqlite3.connect("test.db") as con:   #Open Connection to DB, inserts above recipe strings
                cur = con.cursor()  
                cur.execute("INSERT into recipes (title, totaltime,yields,ingredients,instructions) values (?,?,?,?,?)",(title,totalTime,yields,ingredientsString,instructions,))  
                con.commit()  
                msg = "Recipe successfully added!"
                pagetitle = 'Success!'

        except:  
            con.rollback()  
            msg = "Unable to add recipe :(" 
            pagetitle = 'Error' 
            
        finally:  
            con.close()
            return render_template("save.html",title = pagetitle, msg = msg)  


@app.route("/delete",methods = ["POST","GET"]) # Presents delete.html form, user inputs recipe ID to delete from DB. Not really needed....
def delete():  # call method  & return html template
        return render_template('delete.html', title = 'Delete Recipe')
        
@app.route("/deletestatus",methods = ["POST","GET"])  # Delete recipe from DB with input from /delete method input
def deletestatus(): 
    id = request.form["id"]   # Unique recipe ID from VIEW to be used for deletion
    with sqlite3.connect("test.db") as con:  
        try:  
            cur = con.cursor()  
            cur.execute("delete from recipes where id = ??",id)  
            msg = "Recipe successfully deleted"
            pagetitle = 'Success!'
            return render_template("deletestatus.html",title = pagetitle, msg = msg)    
        except:  
            msg = "Unable to delete recipe :("
            pagetitle = 'Error'

        finally:  
            return render_template("deletestatus.html",title = pagetitle, msg = msg)  

@app.route("/recipe",methods = ["POST","GET"])  # Page to view single recipe chosen from view.html page
def recipe():
        if request.method == "POST":
            try:  
                id = request.form["recipeid"]  #
                with sqlite3.connect("test.db") as con:  

                    cur = con.cursor()  
                    sqlite_select_query = """SELECT * from recipes where id = ?"""
                    cur.execute(sqlite_select_query, (id, ))
                    singlerow = cur.fetchall()
                    print(type(singlerow))
                    title = singlerow[1]
                    print(title[1])
                
            except:
                title = 'Recipe'     

            finally:
                return render_template('recipe.html', singlerow = singlerow, title = title)
    
if __name__ == "__main__":  # on running python app.py
    app.run(debug=True)  # run the flask app

#TODO Actual CSS styling, bug fixes in app.py, refactoring, code indentation, recipe presentation, grid & flexbox layouts, search, toasts for add/deletions, unit conversions, much much more