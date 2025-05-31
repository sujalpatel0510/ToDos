from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title,desc=desc)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

@app.route('/show')
def products():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'this is product page'

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.get_or_404(sno)
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect('/')
    todo = Todo.query.get_or_404(sno)
    return render_template('update.html', todo=todo)  # ✅ RETURN is required


@app.route('/delete/<int:sno>')
def delete_todo(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

# if __name__ == '__main__':
#     # Make sure the tables are created inside the app context
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, port=8000)

if __name__ == '__main__':
    from os import environ
    port = int(environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

