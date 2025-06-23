from flask import Flask, request, url_for, render_template, redirect, flash, make_response,session, abort
from rollData import ROLLS_DATA
from forms import signupForm, loginForm, ChangePasswordForm


app = Flask(__name__)
app.config.update(
    SECRET_KEY="change-this-in-prod",
)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title="BiteMyRoll: Rolling Happiness to Your Doorstep")


@app.route('/menu')
def menu():
    return render_template('menu.html', title="Today's menu")


@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact Us")


@app.route('/about')
def about():
    return render_template('about.html', title="About Us")


@app.route('/detail/<type>')
def detail(type):
    return render_template('roll_detail.html', roll=ROLLS_DATA[type], title=f"BiteMyRole - {ROLLS_DATA[type]["name"]}", roll_key=type)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = signupForm()
    if form.validate_on_submit():
            flash("Signed up successfully!", "success")
            return redirect(url_for("menu"))
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        pass
    return render_template("login.html", form=form)


@app.route("/orders")
def orders():
    results = []
    return render_template("orders.html", orders=results)



@app.route("/cart")
def cart():
    rows, total = [] 
    return render_template("cart.html", rows=rows, total=total)



if __name__ == '__main__':
    app.run(debug=True)

