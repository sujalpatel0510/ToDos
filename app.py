from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd3db32e0a068e13d6846c4d9c5cfc913'  # Change to a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    todos = db.relationship('Todo', backref='owner', lazy=True)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please login.', 'error')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('hello'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def hello():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, desc=desc, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', allTodo=allTodo, user=current_user)

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
@login_required
def update(sno):
    todo = Todo.query.get_or_404(sno)
    if todo.owner != current_user:
        flash('You cannot update this todo.', 'error')
        return redirect(url_for('hello'))
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect(url_for('hello'))
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
@login_required
def delete_todo(sno):
    todo = Todo.query.get_or_404(sno)
    if todo.owner != current_user:
        flash('You cannot delete this todo.', 'error')
        return redirect(url_for('hello'))
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('hello'))

@app.route('/about')
def about():
    return render_template('about.html')

# Create tables and run app
# Create tables on app startup (every time)
with app.app_context():
    db.create_all()

# Run app only if called directly
if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)

