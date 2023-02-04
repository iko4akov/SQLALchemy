import json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import data_file
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(10))
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(250))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.drop_all()
    db.create_all()

    users = [User(**user) for user in data_file.users]
    db.session.add_all(users)

    for order in data_file.orders:
        order['start_date'] = datetime.strptime(order['start_date'], '%m/%d/%Y').date()
        order['end_date'] = datetime.strptime(order['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**order))

    offers = [Offer(**offer) for offer in data_file.offers]
    db.session.add_all(offers)

    db.session.commit()


@app.route('/users', methods=['POST', 'GET'])
def page_users():
    if request.method == "GET":
        query = User.query.all()
        result = [User.to_dict(user) for user in query]
        return jsonify(result)
    elif request.method == "POST":
        data = request.json
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify(User.to_dict(user))

@app.route('/users/<int:id>', methods=['DELETE', 'PUT', "GET"])
def users_page(id):
    user = User.query.get(id)
    if request.method == "DELETE":
        db.session.delete(user)
        db.session.commit()
        return "User deleted"

    elif request.method == "PUT":
        user_request = json.loads(request.data)
        user.first_name = user_request['first_name']
        user.last_name = user_request['last_name']
        user.age = user_request['age']
        user.email = user_request['email']
        user.role = user_request['role']
        user.phone = user_request['phone']
        db.session.add(user)
        db.session.commit()
        return f"Edited User number {id}"

    elif request.method == "GET":
        result = User.to_dict(user)
        return jsonify(result)



@app.route('/orders', methods=['GET', 'POST'])
def page_orders():
    if request.method == "GET":
        query = Order.query.all()
        result = []
        for order in query:
            order_dict = order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            result.append(order_dict)
        return jsonify(result)

    elif request.method == 'POST':
        data = request.json
        order_add = Order(**data)
        db.session.add(order_add)
        db.session.commit()
        return jsonify(Order.to_dict(order_add))

@app.route('/orders/<int:id>', methods=['DELETE', 'PUT', 'GET'])
def orders_page(id):
    order_add = Order.query.get(id)
    if request.method == "DELETE":
        db.session.delete(order_add)
        db.session.commit()
        return "Order deleted"

    elif request.method == "PUT":
        order_request = json.loads(request.data)
        order_request['start_date'] = datetime.strptime(order_request['start_date'], '%Y-%m-%d').date()
        order_request['end_date'] = datetime.strptime(order_request['end_date'], '%Y-%m-%d').date()
        order_add.name = order_request['name']
        order_add.description = order_request['description']
        order_add.start_date = order_request['start_date']
        order_add.end_date = order_request['end_date']
        order_add.address = order_request['address']
        order_add.price = order_request['address']
        order_add.customer_id = order_request['customer_id']
        order_add.executor_id = order_request['executor_id']
        db.session.add(order_add)
        db.session.commit()
        return f"Edited Order number {id}"

    elif request.method == "GET":
        result = order_add.to_dict()
        result['start_date'] = str(result['start_date'])
        result['end_date'] = str(result['end_date'])

        # result = Order.to_dict(order_add)
        return jsonify(result)


@app.route('/offers', methods=['POST', 'GET'])
def page_offers():
    if request.method == "GET":
        query = Offer.query.all()
        result = [Offer.to_dict(offer) for offer in query]
        return jsonify(result)

    elif request.method == "POST":
        data = request.json
        offer = Offer(**data)
        db.session.add(offer)
        db.session.commit()
        return jsonify(User.to_dict(offer))


@app.route('/offers/<int:pk>', methods=['DELETE', 'PUT', 'GET'])
def offers_page(pk):
    offer_add = Offer.query.get(pk)
    if request.method == "DELETE":
        db.session.delete(offer_add)
        db.session.commit()
        return "Offer deleted"

    elif request.method == "PUT":
        offer_data = json.loads(request.data)
        offer_add.order_id = offer_data['order_id']
        offer_add.executor_id = offer_data['executor_id']
        db.session.add(offer_add)
        db.session.commit()
        return f"Edited Offer number {pk}"

    elif request.method == "GET":
        result = Offer.to_dict(offer_add)
        return jsonify(result)

if __name__ == '__main__':
    app.run()
