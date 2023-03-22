from flask import Flask, render_template, jsonify, request
from datetime import datetime
import csv, requests, json

app = Flask(__name__)

# Uitility functions
def read_predictions():
	reader = csv.reader(open('ai-model/checkpoints/predictions.csv', 'r'))
	preds = []
	i = 0
	for row in reader:
		if i != 0:
			preds.append(row[2])
		i += 1
	return preds

def date_days_diff(start_date, end_date, lowerbound=0, upperbound=9):
	date_format = "%d-%m-%Y"
	a = datetime.strptime(start_date, date_format)
	b = datetime.strptime(end_date, date_format)
	delta = b - a
	days = delta.days
	if days > upperbound:
		days = upperbound
	if  days < lowerbound:
		days = lowerbound
	return days

def live_currency():
	date_format = "%d-%m-%Y"
	old_data = json.load(open("static/currency_rate.json", "r+", encoding="utf-8"))
	old_date = old_data['date']
	current_date = datetime.today().strftime(date_format)
	if old_date == current_date:
		return old_data['rate']
	else:
		url = "https://openexchangerates.org/api/latest.json?app_id=060014fec8064901a7d9891bf0b281b2&base=USD&symbols=PKR&prettyprint=false&show_alternative=false"
		header = {"accept": "application/json"}
		response = requests.get(url, headers=header)
		result = response.json()
		data = {"date": current_date, "rate": result['rates']['PKR']}
		with open("static/currency_rate.json", "w+", encoding="utf-8") as f:
			json.dump(data, f, indent=4)
	return result['rates']['PKR']

@app.route("/")
@app.route("/index")
def index():
	date_format = "%d-%m-%Y"
	start_date = "22-03-2023"
	current_date = datetime.today().strftime(date_format)
	days = date_days_diff(start_date, current_date)
	pkr = round(float(read_predictions()[days]), 2)
	usd = round(1/pkr, 4)
	live_pkr = round(live_currency(), 2)
	live_usd = round(1/live_pkr, 4)
	return render_template("index.html", pred_usd=usd, pred_pkr=pkr, live_usd=live_usd, live_pkr=live_pkr)

@app.route("/api/predict", methods=["POST"])
def predict():
	start_date = "22-03-2023"
	current_date = request.form['date']
	conv_type = request.form['conversionType']
	if conv_type == "USD_TO_PKR":
		formPKR = float(request.form['currency2'])
	else:
		formPKR = float(request.form['currency1'])
	days = date_days_diff(start_date, current_date)
	pkr = float(read_predictions()[days])
	error_perc = (abs(pkr - formPKR)/formPKR) * 100
	error_perc = round(100 - error_perc, 2)
	if error_perc < 0:
		error_perc = 0
	return jsonify({"days": days, "accuracy": error_perc})

if __name__ == '__main__':
	app.run(debug=True)