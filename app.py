from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = "smart_lender_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


with app.app_context():
    db.create_all()
# Load the trained model
model = joblib.load(
    r"C:\Users\shaik\OneDrive\Desktop\AIML Project\Epic 5 Application Building\Random_Forest_Model.pkl"
)

print("Features expected:", model.n_features_in_)

try:
    print("Feature names:", model.feature_names_in_)
except:
    print("No feature names stored.")


# Home Page
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user"] = email
            return redirect("/home")

        else:
            return "Invalid Email or Password"

    return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered"

        hashed_password = generate_password_hash(password)

        new_user = User(
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/home")
def home():
    return render_template("index.html")

# Prediction Page
@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


# Predict Route
@app.route("/predict", methods=["POST"])
def predict():
    try:
        applicant_income = float(request.form["ApplicantIncome"])
        coapplicant_income = float(request.form["CoapplicantIncome"])
        loan_amount = float(request.form["LoanAmount"])
        loan_amount_term = float(request.form["Loan_Amount_Term"])
        credit_history = float(request.form["Credit_History"])

        features = pd.DataFrame({
            "ApplicantIncome": [applicant_income],
            "CoapplicantIncome": [coapplicant_income],
            "LoanAmount": [loan_amount],
            "Loan_Amount_Term": [loan_amount_term],
            "Credit_History": [credit_history]
        })

        prediction = model.predict(features)

        if prediction[0] == 1:
            result = "Loan Approved"
        else:
            result = "Loan Rejected"

        return render_template(
            "result.html",
            prediction_text=result
        )

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)