from flask import Flask, request, url_for, render_template, redirect, flash, make_response,session, abort, jsonify
from data import ROLLS_DATA, BEVERAGE_DATA, database
from forms import signupForm, loginForm, ChangePasswordForm, buildRollForm
from datetime import datetime

PRODUCTS_DATA = {**ROLLS_DATA, **BEVERAGE_DATA}

app = Flask(__name__)
app.secret_key = 'some_secret_key'

user_info = {}
#user_email = "rajesh@gmail.com"
#database[user_email] = {"info": user_info, "cart": {}, "orders": [], "visited_drinks": False, "location":""}

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="BiteMyRoll: Rolling Happiness to Your Doorstep", cred = session.get("User_email")
 , database = database)


@app.route('/menu')
def menu():
    print(database[session.get("User_email")]["location"])
    return render_template('menu.html', title="Today's menu", cred = session.get("User_email"), database = database)


@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us", cred = session.get("User_email"), database = database)


@app.route('/about')
def about():
    return render_template('about.html', title="About Us", cred = session.get("User_email"), database = database)



@app.route('/detail/<type>', methods=["GET", "POST"])
def detail(type):
    roll = ROLLS_DATA[type]
    form = buildRollForm(roll)

    if form.validate_on_submit():
        qty = {}

        qty_regular = form.Regular.data
        qty_large   = form.Large.data
        qty_mega    = form.Mega.data
        
        if qty_regular <= 0 and qty_large <= 0 and qty_mega <= 0:
            flash("Please select at least one item to add to cart.", "warning")
            return render_template(
                "roll_detail.html",
                form=form,
                roll=roll,
                roll_key=type.strip(),  # ✅ Pass stripped version too
                cred=session.get("User_email"),
                title=f"BiteMyRole - {ROLLS_DATA[type]['name']}", 
                database = database
            )   

        if qty_regular and qty_regular > 0:
            qty["Regular"] = qty_regular  # Capital R

        if qty_large and qty_large > 0:
            qty["Large"] = qty_large      # Capital L

        if qty_mega and qty_mega > 0:
            qty["Mega"] = qty_mega        # Capital M

        
        if not session.get("User_email"):
            return redirect(url_for("login", next=type))

        database[session.get("User_email")]["cart"][type.strip()] = {  # ✅ Strip whitespace from key
            "name": roll["name"],   
            "size": qty,
            "note": form.note.data
        }

        flash("Added to cart!", "success")
        print(database[session.get("User_email")]["cart"])

    return render_template(
        "roll_detail.html",
        form=form,
        roll=roll,
        roll_key=type.strip(),  # ✅ Pass stripped version too
        cred=session.get("User_email"),
        title=f"BiteMyRole - {ROLLS_DATA[type]['name']}", 
        database = database
    )





@app.route('/drinks')
def drinksMenu():
    database[session.get("User_email")]["visited_drinks"] = True
    return render_template("drinksMenu.html", title="Drinks", cred=session.get("User_email"), database = database)


@app.route('/drinksDetail/<type>', methods=["GET", "POST"])
def drinksDetail(type):
    drink = BEVERAGE_DATA.get(type.strip())
    if not drink:
        flash("Drink not found.", "error")
        return redirect(url_for("drinksMenu"))

    form = buildRollForm(drink)

    if form.validate_on_submit():
        qty = {}

        qty_regular = form.Regular.data or 0
        qty_large   = form.Large.data or 0
        qty_mega    = form.Mega.data or 0

        if qty_regular <= 0 and qty_large <= 0 and qty_mega <= 0:
            flash("Please select at least one item to add to cart.", "warning")
        else:
            if qty_regular > 0:
                qty[drink["sizes"][0]["label"]] = qty_regular
            if qty_large > 0:
                qty[drink["sizes"][1]["label"]] = qty_large
            if qty_mega > 0:
                qty[drink["sizes"][2]["label"]] = qty_mega

            if not session.get("User_email"):
                return redirect(url_for("login", next=type))

            database[session.get("User_email")]["cart"][type.strip()] = {
                "name": drink["name"],
                "size": qty,
                "note": form.note.data
            }

            flash("Added to cart!", "success")
            print(database[session.get("User_email")]["cart"])

    return render_template(
        "drinks_detail.html",
        form=form,
        roll=drink,
        roll_key=type.strip(),
        cred=session.get("User_email"),
        title=f"BiteMyRoll - {drink['name']}", 
        database = database
    )




@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()
    next = request.args.get("next")

    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        if email in database and password == database[email]["info"]["password"]:
            session["User_email"] = email
            flash("Login successfully!", "success")
            if next == "orders":
                return redirect(url_for("orders", title="orders"))
            elif next:
                return redirect(url_for("detail", type=next, title=f"BiteMyRole - {next}"))
            
            return redirect(url_for("menu"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html", form=form, title="Login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = signupForm()
    if form.validate_on_submit():
        if form.email.data in database:
            flash("Email already registered.", "danger")
            return redirect(url_for("signup"))

        global user_info,user
        user_info = {
            "username": form.username.data,
            "gender": form.gender.data,
            "dob": form.dob.data,
            "age": form.age.data,
            "password": form.password.data
        }
        database[form.email.data] ={"info": user_info, "cart": {}, "orders": [], "visited_drinks": False,"location":""}
        session["User_email"] = form.email.data
        session["user_password"] = form.password.data
        print(session.get("User_email"))
        flash("Signed up successfully!", "success")
        return redirect(url_for("menu"))
    return render_template("signup.html", form=form)


@app.route("/orders")
def orders():
    if not session.get("User_email"):
        return redirect(url_for("login", next="orders"))
    return render_template("orders.html", orders=database[session.get("User_email")]["orders"], ROLLS_DATA=PRODUCTS_DATA,cred= session.get("User_email"), title="Orders", database = database)



@app.route("/cart")
def cart():
    global ROLLS_DATA
    return render_template("cart.html",data = database[session.get("User_email")]["cart"], ROLLS_DATA=PRODUCTS_DATA, cred = session.get("User_email"), title="Cart",visited_drinks=database[session.get("User_email")]["visited_drinks"], database = database)

@app.route('/logout')
def logout():
    session["User_email"] = ""
    return render_template('menu.html', title="Today's menu", cred = session.get("User_email"), database = database)


@app.route('/changePassword', methods=["GET","POST"])
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit() and form.current_password.data == session["user_password"]:
        flash("Your Password has been changed successfully","success")
        session["user_password"] = form.current_password.data
        return render_template('menu.html', title="Today's menu", cred = session.get("User_email"), database = database)
    else:
        flash("Your old credential did not match","error")
    return  render_template('change_password.html',title = "Change Password", cred = session.get("User_email"),form=form, database = database)



@app.route('/checkout', methods=["POST"])
def checkout():
    total = request.args.get("total")
    if not session.get("User_email"):
        flash("Please log in to complete checkout.", "error")
        return redirect(url_for("login"))

    if not database[session.get("User_email")]["cart"]:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("cart"))

    order_data = {
        "items": database[session.get("User_email")]["cart"].copy(),
        "total": total,
        "timestamp": datetime.now(),
    }

    database[session.get("User_email")]["orders"].append(order_data)

    database[session.get("User_email")]["cart"].clear()

    flash("Your order has been placed successfully!", "success")
    database[session.get("User_email")]["visited_drinks"] = False
    print(database[session.get("User_email")]["orders"])
    return redirect(url_for("menu"))



@app.route('/updatecart', methods=["POST"])
def update_cart():
    roll_key = request.args.get("roll_key")
    size     = request.args.get("size")
    op       = request.form.get("op")  

    if not roll_key or not size or not op:
        flash("Invalid update request", "error")
        return redirect(url_for("cart"))

    if roll_key not in database[session.get("User_email")]["cart"]:
        flash("Item not found in cart", "error")
        return redirect(url_for("cart"))

    if size not in database[session.get("User_email")]["cart"][roll_key]["size"]:
        flash("Size not found for item", "error")
        return redirect(url_for("cart"))

    current_qty = database[session.get("User_email")]["cart"][roll_key]["size"][size]
    if op == "inc" and current_qty < 10:
        database[session.get("User_email")]["cart"][roll_key]["size"][size] += 1
    elif op == "dec":
        if current_qty > 1:
            database[session.get("User_email")]["cart"][roll_key]["size"][size] -= 1
        else:
            del database[session.get("User_email")]["cart"][roll_key]["size"][size]
            if not database[session.get("User_email")]["cart"][roll_key]["size"]:
                del database[session.get("User_email")]["cart"][roll_key]

    return redirect(url_for("cart"))


@app.route('/cancel_order/<int:index>', methods=["POST"])
def cancel_order(index):
    if 0 <= index < len(database[session.get("User_email")]["orders"]):
        del database[session.get("User_email")]["orders"][index]
        flash("Order canceled successfully!", "success")
    else:
        flash("Invalid order index.", "error")
    return redirect(url_for("orders"))



@app.route("/set_location/<location>")
def set_location(location):
    print(location)
    user_email = session.get("User_email")
    if user_email and user_email in database:
        database[user_email]["location"] = location
    return redirect(url_for("menu"))




if __name__ == '__main__':
    app.run(debug=True)

