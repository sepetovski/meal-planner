from flask import Flask, render_template, request, redirect
from models import db, Meal, WeekPlan, PlanMeal
from datetime import date, timedelta

app = Flask(__name__)
import os

database_url = os.environ.get('postgresql://meal_planner_db_xqb4_user:4Qr6aEh4nfW0zOqpklUdgOTsG27LbT79@dpg-d74kn18gjchc73b9h6dg-a/meal_planner_db_xqb4')

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'


db.init_app(app)

with app.app_context():
    db.create_all()

# Home redirect
@app.route('/')
def home():
    return redirect('/meals')

# List meals
@app.route('/meals')
def meals():
    meals = Meal.query.all()
    return render_template('meals.html', meals=meals)

# Add meal
@app.route('/meals/add', methods=['GET', 'POST'])
def add_meal():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']

        meal = Meal(name=name, category=category)
        db.session.add(meal)
        db.session.commit()

        return redirect('/meals')

    return render_template('add_meal.html')

# Delete meal
@app.route('/meals/delete/<int:id>')
def delete_meal(id):
    meal = db.session.get(Meal, id)
    if meal:
        db.session.delete(meal)
        db.session.commit()
    return redirect('/meals')

def get_monday():
    today = date.today()
    return today - timedelta(days=today.weekday())



@app.route('/planner', methods=['GET', 'POST'])
def planner():
    week_param = request.args.get('week')

    if week_param:
        monday = date.fromisoformat(week_param)
    else:
        monday = get_monday()

    week = WeekPlan.query.filter_by(start_date=monday).first()

    if not week:
        week = WeekPlan(start_date=monday)
        db.session.add(week)
        db.session.commit()

    if request.method == 'POST':
        PlanMeal.query.filter_by(week_id=week.id).delete()

        for day in range(7):
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                field_name = f"{day}_{meal_type}"
                meal_id = request.form.get(field_name)

                if meal_id:
                    plan_meal = PlanMeal(
                        week_id=week.id,
                        day_of_week=day,
                        meal_type=meal_type,
                        meal_id=int(meal_id)
                    )
                    db.session.add(plan_meal)

        db.session.commit()
        return redirect(f'/planner?week={monday}')

    meals = Meal.query.all()
    plan_meals = PlanMeal.query.filter_by(week_id=week.id).all()

    plan_dict = {(pm.day_of_week, pm.meal_type): pm.meal_id for pm in plan_meals}

    # Calculate prev/next weeks
    prev_week = monday - timedelta(days=7)
    next_week = monday + timedelta(days=7)

    return render_template(
        'planner.html',
        meals=meals,
        plan=plan_dict,
        monday=monday,
        prev_week=prev_week,
        next_week=next_week,
        timedelta=timedelta
    )


if __name__ == '__main__':
    app.run()