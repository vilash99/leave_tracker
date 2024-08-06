from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'XlmfYVd5zq78lm9pzzD6x6jWBMNZIV4W'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:vilvic009@localhost/postgres'
db = SQLAlchemy(app)



class Employee(db.Model):
    __tablename__ = 'employee'
    emp_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    leaves_alloted = db.Column(db.Integer, default=18)
    is_admin = db.Column(db.Boolean, default=False)


def get_current_user():
    if 'emp_id' in session:
        return Employee.query.filter_by(emp_id=session['emp_id']).first()

    return None


@app.route('/')
def employee_home():
    user = get_current_user()

    if user:
        if user.is_admin:
            return redirect(url_for('admin_page'))

        return render_template('employee_page.html', user=user)

    return redirect(url_for('login'))



@app.route('/admin')
def admin_page():
    return 'Admin Page'


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect(url_for('employee_home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Employee.query.filter_by(username=username).first()

        if user and user.password == password:
            session['emp_id'] = user.emp_id

            return redirect(url_for('employee_home'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']

        if not Employee.query.filter_by(username=username).first():
            new_user = Employee(full_name=full_name, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)



# Home -> /

# if login in Session :
#     if admin:
#         goto admin page
#     else:
#         goto employee page
# else:
#     login page