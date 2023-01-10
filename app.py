import os
from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MY_SQL_PWD = os.getenv('MY_SQL_PWD')
conn = mysql.connector.connect(
    user='root', password=MY_SQL_PWD, host='localhost', database='inventory')
mycursor = conn.cursor()
now = datetime.now()
dts = now.strftime('%y-%m-%d %H:%M:%S')


@app.route('/')
def home():
	return render_template('index.html')


@app.route('/additem', methods=['POST', 'GET'])
def Add():
	if request.method == 'GET':
		return render_template('additem.html')
	else:
		id = request.form['pid']
		name = request.form['pname']
		price = float(request.form['pprice'])
		quantity = int(request.form['pquantity'])
		itype = request.form['ptype']
		cname = request.form['cname']
		cmobile = request.form['cmobile']
		if len(cmobile) != 10:
			return 'Error!!, Mobile Number should have 10 digits only'
			# ecmob.delete(0, END)
			# return
		mycursor.execute('SELECT iid FROM inventory WHERE iproductid = ' + id)
		row = mycursor.fetchone()
		if row is not None:
			return 'Warning!!, The Product already Exists\nNote: Go to Stocking!!'
			# clear_text()
			# return
		sql = """INSERT INTO register(
				dt, productid, productname, price, stockquant, issuequant, onhandquant, batches, process, cname, cmobile)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
		val = (
			dts,
			id,
			name,
			price,
			quantity,
			0,
			quantity,
			1,
			'Stock',
			cname,
			cmobile,
			)
		try:
			mycursor.execute(sql, val)
			# conn.commit()
		except:
			conn.rollback()
			return 'Error!!, Error during Inserting Register!!'

		cursor = conn.cursor()
		sql = """INSERT INTO inventory(
			iproductid, iname, ibatch, iprice, iquantity, itype, cname, cmobile)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
		val = (
			id,
			name,
			1,
			price,
			quantity,
			itype,
			cname,
			cmobile,
			)
		try:
			cursor.execute(sql, val)
			conn.commit()
			msg = 'Successfully!! Added ' + str(quantity) + ' units of ' + name
			return msg
			# messagebox.showinfo('Stocked Successfully', msg)
			# clear_text()
		except:
			conn.rollback()
			return 'Error!!, Error during Transaction!!'
	# return (id, name, price, quantity, itype, cname, cmobile)


@app.route('/editprice', methods=['POST', 'GET'])
def EditPrice():
	if request.method == 'GET':
		return render_template('edititem.html')
	cmobile = request.form['cmobile']
	id = request.form['pid']
	price = request.form['pprice']
	if len(cmobile) != 10:
		return 'Error!!', 'Mobile Number should have 10 digits only'

	mycursor.execute('SELECT iid FROM inventory WHERE iproductid = ' +
	                 id + ' AND cmobile = ' + cmobile)
	test = mycursor.fetchall()
	try:
		t = test[0][0]
	except:
		return 'Error!!', 'Product Doesn\'t Exist in Inventory!'
	try:
		mycursor.execute('UPDATE inventory SET iprice = ' + price +
		                 ' WHERE iproductid = ' + id + ' AND cmobile = ' + cmobile)
		conn.commit()
		return 'Success!!', 'Edited Successfully!!'
	except:
		conn.rollback()
		return 'Error!!', 'Error During Transaction!!'


@app.route('/editquantity', methods=['POST', 'GET'])
def EditQuantity():
	if request.method == 'GET':
		return render_template('edititem.html')
	cmobile = request.form['cmobile']
	id = request.form['pid']
	quantity = request.form['pquantity']
	ibatch = request.form['pbatch']

	if len(cmobile) != 10:
		return 'Error!!', 'Mobile Number should have 10 digits only'
	mycursor.execute('SELECT iid FROM inventory WHERE iproductid = ' +
	                 id + ' AND cmobile = ' + cmobile + ' AND ibatch = ' + ibatch)
	test = mycursor.fetchall()
	if test is None:
		return 'Error!!', 'Product Doesn\'t Exist in Inventory!'
	try:
		mycursor.execute('UPDATE inventory SET iquantity = ' + quantity +
		                 ' WHERE iproductid = ' + id + ' AND cmobile = ' + cmobile + ' AND ibatch = ' + ibatch)
	except:
		conn.rollback()
		return 'Error!!', 'Error During Transaction!!'
	conn.commit()
	return 'Success!!', 'Edited Successfully!!'


def getBatch(id):
	mycursor.execute('SELECT max(ibatch) FROM inventory WHERE iproductid = ' + id)
	myresult = mycursor.fetchall()
	if myresult[0][0] is None:
		return 0
	return myresult[0][0]


@app.route('/stock', methods=['POST', 'GET'])
def Stock():
	if request.method == 'GET':
		return render_template('stock.html')

	id = request.form['pid']
	get = int(getBatch(id))
	cmobile = request.form['cmobile']
	if len(cmobile) != 10:
		return 'Error!!', 'Mobile Number should have 10 digits only'
	batch = get + 1
	quantity = int(request.form['pquantity'])
	try:
		mycursor.execute('SELECT itype,iname,iprice,sum(iquantity),cname FROM inventory WHERE iproductid = '
							+ id + ' AND cmobile = ' + cmobile)
		myresult = mycursor.fetchall()
		type = myresult[0][0]
		name = myresult[0][1]
		price = myresult[0][2]
		total = myresult[0][3] + quantity
		cname = myresult[0][4]
	except:
		return 'Error!!', 'Product Does not Exist!!'

	sql = """INSERT INTO register(
                   dt, productid, productname, price, stockquant, issuequant, onhandquant, batches, process, cname, cmobile)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
	val = (
        dts,
        id,
        name,
        price,
        quantity,
        0,
        total,
        batch,
        'Stock',
        cname,
        cmobile,
        )
	try:
		mycursor.execute(sql, val)
		conn.commit()
	except:
		conn.rollback()
		return 'Error!!', 'Error during Stocking!!'

	cursor = conn.cursor()
	sql = """INSERT INTO inventory(
       iproductid, iname, ibatch, iprice, iquantity, itype, cname, cmobile)
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
	val = (
        id,
        name,
        batch,
        price,
        quantity,
        type,
        cname,
        cmobile,
        )
	try:
		cursor.execute(sql, val)
		msg = 'Successfully!! Added ' + str(quantity) + ' units of ' + name
		conn.commit()
		return msg
	except:
		conn.rollback()
		return 'Error!!', 'Error during Registering!!'


@app.route('/issue', methods=['POST', 'GET'])
def Issue():
	if request.method == 'GET':
		return render_template('issue.html')

	id = request.form['pid']
	quantity = int(request.form['pquantity'])
	cmobile = request.form['cmobile']
	if len(cmobile) != 10:
		return 'Error!!, Mobile Number should have 10 digits only'
	tempquant = quantity
	name = ''
	price = 0
	cname = ''
	doregister = True
	while 1:
		try:
			mycursor.execute('SELECT iid,iquantity,iname,iprice,cname FROM inventory WHERE iproductid = '
								+ id +' AND ibatch = (SELECT MIN(ibatch) FROM inventory WHERE iproductid = '+id+') AND cmobile = '
								+ cmobile)
			myresult = mycursor.fetchall()
			gid = myresult[0][0]
			getquant = myresult[0][1]
			name = myresult[0][2]
			price = int(myresult[0][3])
			cname = myresult[0][4]
		except:
			doregister = False
			conn.rollback()
			return 'Error!!, Stock Not Available!!'
		if quantity < getquant:
			newquantity = getquant - quantity
			mycursor.execute('UPDATE inventory SET iquantity = ' + str(newquantity) + ' WHERE iid = ' + str(gid))
			break
		elif quantity == getquant:
			mycursor.execute('DELETE FROM inventory WHERE iid = ' + str(gid))
			mycursor.execute('UPDATE inventory SET ibatch = ibatch - 1 WHERE iproductid = ' + str(id))
			break
		else:
			newquantity = quantity - getquant
			quantity = newquantity
			mycursor.execute('DELETE FROM inventory WHERE iid = ' + str(gid))
			mycursor.execute('UPDATE inventory SET ibatch = ibatch - 1 WHERE iproductid = ' + str(id))
	if doregister:
		try:
			mycursor.execute('SELECT sum(iquantity), max(ibatch) FROM inventory WHERE iproductid = ' + str(id))
			myresult = mycursor.fetchall()
			if myresult[0][0] is None:
				total = 0
				batch = 0
			else:
				total = int(myresult[0][0])
				batch = int(myresult[0][1])
			sql = """INSERT INTO register(dt, productid, productname, price, stockquant, issuequant, onhandquant, batches, process, cname, cmobile)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
			val = (
                dts,
                id,
                name,
                price,
                0,
                tempquant,
                total,
                batch,
                'Issue',
                cname,
                cmobile
                )
			mycursor.execute(sql, val)
			msg = 'Successfully!! Issued ' + str(tempquant) + ' units of ' + name
			conn.commit()
			return msg
		except:
			conn.rollback()
			return 'Error!!, Error during Transaction!!'

@app.route('/display')
def Display():
	mycursor.execute('SELECT iproductid,iname,sum(iquantity),max(ibatch),iprice FROM inventory GROUP BY iproductid')
	result = mycursor.fetchall()
	return render_template('display.html', data = result)

if __name__ == '__main__':
	app.run()
