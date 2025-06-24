from flask import Flask, request, url_for, render_template, redirect, flash, make_response,session, abort
from data import ROLLS_DATA, BEVERAGE_DATA
from forms import signupForm, loginForm, ChangePasswordForm, buildRollForm
from datetime import datetime

PRODUCTS_DATA = {**ROLLS_DATA, **BEVERAGE_DATA}

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this",
 

user_email="" 
user_password = ""
user_cart = {}
user_orders = []

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="BiteMyRoll: Rolling Happiness to Your Doorstep", cred = user_email)


@app.route('/menu')
def menu():
    return render_template('menu.html', title="Today's menu", cred = user_email)


@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us", cred = user_email)


@app.route('/about')
def about():
    return render_template('about.html', title="About Us", cred = user_email)



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
                cred=user_email,
                title=f"BiteMyRole - {ROLLS_DATA[type]['name']}"
            )   

        if qty_regular and qty_regular > 0:
            qty["Regular"] = qty_regular  # Capital R

        if qty_large and qty_large > 0:
            qty["Large"] = qty_large      # Capital L

        if qty_mega and qty_mega > 0:
            qty["Mega"] = qty_mega        # Capital M

        
        if not user_email:
            return redirect(url_for("login", next=type))

        user_cart[type.strip()] = {  # ✅ Strip whitespace from key
            "name": roll["name"],   
            "size": qty,
            "note": form.note.data
        }

        flash("Added to cart!", "success")
        print(user_cart)

    return render_template(
        "roll_detail.html",
        form=form,
        roll=roll,
        roll_key=type.strip(),  # ✅ Pass stripped version too
        cred=user_email,
        title=f"BiteMyRole - {ROLLS_DATA[type]['name']}"
    )





@app.route('/drinks')
def drinksMenu():
    return render_template("drinksMenu.html", title="Drinks", cred=user_email)


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

            if not user_email:
                return redirect(url_for("login", next=type))

            user_cart[type.strip()] = {
                "name": drink["name"],
                "size": qty,
                "note": form.note.data
            }

            flash("Added to cart!", "success")
            print(user_cart)

    return render_template(
        "drinks_detail.html",
        form=form,
        roll=drink,
        roll_key=type.strip(),
        cred=user_email,
        title=f"BiteMyRoll - {drink['name']}"
    )




@app.route("/login", methods=["GET", "POST"])
def login():
    global user_email, user_password 
    form = loginForm()
    next = request.args.get("next")
    if form.validate_on_submit():
        flash("Signed up successfully!", "success")
        user_email = form.email.data
        user_password = form.password.data
        if next:
            return redirect(url_for("detail",type=next,title=f"BiteMyRole - {next}"))
        return redirect(url_for("menu"))
    return render_template("login.html", form=form, title="Login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = signupForm()
    if form.validate_on_submit():
            flash("Signed up successfully!", "success")
            return redirect(url_for("menu"))
    return render_template("signup.html", form=form)


@app.route("/orders")
def orders():
    return render_template("orders.html", orders=user_orders, ROLLS_DATA=PRODUCTS_DATA,cred= user_email, title="Orders")



@app.route("/cart")
def cart():
    global ROLLS_DATA, user_cart
    return render_template("cart.html",data = user_cart, ROLLS_DATA=PRODUCTS_DATA, cred = user_email, title="Cart")

@app.route('/logout')
def logout():
    global user_email, user_password, user_cart
    user_email = ""
    user_password = ""
    user_cart = {}
    return render_template('menu.html', title="Today's menu", cred = user_email)


@app.route('/changePassword', methods=["GET","POST"])
def changePassword():
    global user_password
    form = ChangePasswordForm()
    if form.validate_on_submit and form.current_password.data == user_password:
        flash("Your Password has been changed successfully","success")
        user_password = form.current_password.data
        return render_template('menu.html', title="Today's menu", cred = user_email)
    else:
        flash("Your old credential did not match","error")
    return  render_template('change_password.html',title = "Change Password", cred = user_email,form=form)



@app.route('/checkout', methods=["POST"])
def checkout():
    global user_cart, user_orders, user_email
    total = request.args.get("total")
    if not user_email:
        flash("Please log in to complete checkout.", "error")
        return redirect(url_for("login"))

    if not user_cart:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("cart"))

    order_data = {
        "items": user_cart.copy(),
        "total": total,
        "timestamp": datetime.now(),
    }

    user_orders.append(order_data)

    user_cart.clear()

    flash("Your order has been placed successfully!", "success")
    print(user_orders)
    return redirect(url_for("menu"))



@app.route('/updatecart', methods=["POST"])
def update_cart():
    roll_key = request.args.get("roll_key")
    size     = request.args.get("size")
    op       = request.form.get("op")  

    if not roll_key or not size or not op:
        flash("Invalid update request", "error")
        return redirect(url_for("cart"))

    if roll_key not in user_cart:
        flash("Item not found in cart", "error")
        return redirect(url_for("cart"))

    if size not in user_cart[roll_key]["size"]:
        flash("Size not found for item", "error")
        return redirect(url_for("cart"))

    current_qty = user_cart[roll_key]["size"][size]
    if op == "inc" and current_qty < 10:
        user_cart[roll_key]["size"][size] += 1
    elif op == "dec":
        if current_qty > 1:
            user_cart[roll_key]["size"][size] -= 1
        else:
            del user_cart[roll_key]["size"][size]
            if not user_cart[roll_key]["size"]:
                del user_cart[roll_key]

    return redirect(url_for("cart"))


@app.route('/cancel_order/<int:index>', methods=["POST"])
def cancel_order(index):
    global user_orders
    if 0 <= index < len(user_orders):
        del user_orders[index]
        flash("Order canceled successfully!", "success")
    else:
        flash("Invalid order index.", "error")
    return redirect(url_for("orders"))



if __name__ == '__main__':
    app.run(debug=True)

