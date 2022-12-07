from flask import Flask, request, redirect, render_template, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)
client = MongoClient("localhost", 27017)
plants = client.plants_database.plants
harvests = client.plants_database.harvests

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        name = request.form.get("plant_name")
        variety = request.form.get("variety")
        photo = request.form.get("photo")
        date_planted = request.form.get("date_planted")

        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo,
            'date_planted': date_planted
        }
        insert_plant_id = plants.insert_one(new_plant).inserted_id

        return redirect(url_for('detail', plant_id=insert_plant_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""
    plant_to_show = plants.find_one({"_id": ObjectId(plant_id)})

    harvests_to_find = harvests.find()

    context = {
        'plant': plant_to_show,
        'harvests': harvests_to_find
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    quantity = request.form.get("harvested_amount")
    date = request.form.get("date_planted")

    new_harvest = {
        'quantity': quantity, # e.g. '3 tomatoes'
        'date': date,
        'plant_id': plant_id
    }

    harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """
    Shows the edit page and accepts a POST request with edited data.
    """
    name = request.form.get("plant_name")
    variety = request.form.get("variety")
    photo_url = request.form.get("photo")
    date_planted = request.form.get("date_planted")

    if request.method == 'POST':
        edit_plant = {
            "name": name,
            "variety": variety,
            "photo_url": photo_url,
            "date_planted": date_planted
        }
        new_edit = {"$set": edit_plant}
        plants.update_one({"_id": ObjectId(plant_id)}, new_edit)
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = plants.find_one({"_id": ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }
        
        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    """
    Removes specific plant and all harvest data for plant
    """
    plants.delete_one({"_id": ObjectId(plant_id)})

    delete_all_harvests = harvests.find({"plant_id": (plant_id)})
    for item in delete_all_harvests:
        harvests.delete_one(item)

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

