from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from datetime import timedelta


app = Flask(__name__)

app.secret_key = 'XlmfYVd5zq78lm9pzzD6x6jWBMNZIV4W'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:vilvic009@localhost/postgres'
                                      # 'protocol://username:password@host/database_name'

db = SQLAlchemy(app)

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


@app.before_request
def make_session_permanent():
    session.permanent = True


class Employee(db.Model):
    __tablename__ = 'employee'
    emp_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    leaves_alloted = db.Column(db.Integer, default=18)
    is_admin = db.Column(db.Boolean, default=False)


class Leave(db.Model):
    __tablename__ = 'leave'
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    till_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    is_approved = db.Column(db.Integer)
    approved_by = db.Column(db.Integer)
    comment = db.Column(db.Text)


def get_current_user():
    if 'emp_id' in session:
        return Employee.query.filter_by(emp_id=session['emp_id']).first()

    return None



@app.route('/', methods=['GET', 'POST'])
def employee_home():
    user = get_current_user()

    if user:
        if user.is_admin:
            return redirect(url_for('admin_page'))

        if request.method == 'POST':
            from_date = request.form['from-date']
            till_date = request.form['till-date']
            total_days = request.form['total-days']
            reason = request.form['reason']

            new_leave = Leave(emp_id=user.emp_id, from_date=from_date, till_date=till_date,
                              total_days=total_days, reason=reason, is_approved=-1)
            db.session.add(new_leave)
            db.session.commit()

            return redirect(url_for('employee_home'))


        total_days_leaves = db.session.query(func.sum(Leave.total_days)).filter(Leave.emp_id == user.emp_id).scalar()
        if not total_days_leaves:
            total_days_leaves = 0

        balance_leaves = user.leaves_alloted - total_days_leaves

        leaves_days = {
            'total_days_leaves': total_days_leaves,
            'balance_leaves': balance_leaves
        }

        leaves = Leave.query.filter_by(emp_id=user.emp_id).all()

        return render_template('employee_page.html', user=user, leaves_days=leaves_days, leaves=leaves)

    return redirect(url_for('login'))



@app.route('/admin')
def admin_page():
    return render_template('admin_page.html')


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

        if full_name and username and password:
            if not Employee.query.filter_by(username=username).first():
                new_user = Employee(full_name=full_name, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('emp_id', None)
    return redirect(url_for('employee_home'))


if __name__ == '__main__':
    app.run(debug=True)

