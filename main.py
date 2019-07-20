from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://final-project:final-project@localhost:8889/final-project'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hnfoy123&fnbg@f4'

class Customer(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    genre = db.Column(db.String(120))
    platform = db.Column(db.String(120))
    price = db.Column(db.String(10))
    stock = db.Column(db.Integer, default=0)
    amount_sold = db.Column(db.Integer, default=0)

    def __init__(self, title, genre, platform, price):
        self.title = title
        self.genre = genre
        self.platform = platform
        self.price = price

    def __repr__(self):
        return '<Title: ' + self.title +'>'





#Checks if password is bewteen 3 - 20 characters and has no spaces.
def validate_field(field):
    if len(field) < 21 and len(field) > 2:
        for letter in field:
            if letter == ' ':
                return False
        return True
    else:
        return False

#Checks if email is valid
def validate_email(email):
    if email.find('@') > 0:
        if email.rfind('.') > 0:
            if email.find('@') < email.rfind('.'):
                return True
    return False







@app.before_request
def require_login():
    allowed_routes = ['login','register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


    


#Register Account
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verified']


        #Error message for invalid email
        if not validate_email(email):
            flash('Invlaid Email!', 'error')

        #Error message for invalid password
        if not validate_field(password):
            flash('Invalid Password!', 'error')

        #Error message for mismatching password and verification password
        if verify != password:
            flash('Passwords do not match!', 'error')

        existing_customer = Customer.query.filter_by(email=email).first()
        if validate_email(email) and validate_field(password) and verify == password:
            if not existing_customer:
                new_customer = Customer(email, password)
                db.session.add(new_customer)
                db.session.commit()
                session['email'] = email
                return redirect('/stock')
            flash('Email already in use!', 'error')
            return render_template('register.html', title='Register')
    return render_template('register.html',title='Register')




#Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        customer = Customer.query.filter_by(email=email).first()
        if customer and customer.password == password:
            session['email'] = email
            session['flip'] = 0
            return redirect('/stock')
        else:
            flash("Incorrect password, or user doesn't exist.", 'error')
    return render_template('login.html', title='Login')



#Logout route
@app.route('/logout')
def logout():
    del session['email']
    if 'flip' in session:
        del session['flip']
    return redirect('/login')

#Route to the stock page
@app.route('/stock', methods=['POST', 'GET'])
def stock():
    try:
        if request.method == 'POST':
            if session['flip'] % 2 == 0:
                order = True
                session['flip'] += 1
            else:
                order = False 
                session['flip'] += 1
        games = Game.query.all()
        return render_template('stock.html', title="Stock", games=games, order=order)

    except UnboundLocalError:
        order = False
        games = Game.query.all()
        return render_template('stock.html', title="Stock", games=games, order=order)


#Form to add game to the database
@app.route('/addgame', methods=['POST', 'GET'])
def add_game():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        platform = request.form['platform']
        price = request.form['price']

        new_game = Game(title, genre, platform, price)
        db.session.add(new_game)
        db.session.commit()
        return redirect('/stock')

    return render_template('addgame.html',title='Add Game to Database')

@app.route('/order', methods=['POST'])
def order():
    games = Game.query.all()
    items = list()

    for game in games:
        id = str(game.id)
        amount_ordered = request.form[id]
        items.append(amount_ordered)

    display_items = list()
    for game in games:
        amount = str(items.pop(0))
        if amount != '0' and amount != '':
            
            display_items.append(game.title + ': ' + amount)

    return render_template('order.html', title='Game Order', games=games, items=display_items)




if __name__ == '__main__':
    app.run()