@app.route('/additem')
def hello_world():
	return render_template('additem.html')

@app.route('/edititem')
def hello_world():
	return render_template('edititem.html')

@app.route('/stock')
def hello_world():
	return render_template('stock.html')

@app.route('/issue')
def hello_world():
	return render_template('issue.html')

@app.route('/display')
def hello_world():
	return render_template('display.html')

@app.route('/bill')
def hello_world():
	return render_template('bill.html')