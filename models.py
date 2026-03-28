from flask_sqlalchemy import SQLAlchemy
from datetime import date
db = SQLAlchemy()

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(20))  # breakfast/lunch/dinner


class WeekPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)  # Monday


class PlanMeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('week_plan.id'))
    day_of_week = db.Column(db.Integer)  # 0 = Monday
    meal_type = db.Column(db.String(20))  # breakfast/lunch/dinner
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'))