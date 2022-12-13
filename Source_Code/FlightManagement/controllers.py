from flask import render_template, request, redirect, session, jsonify, url_for
from FlightManagement import app, dao, utils, db
from flask_login import login_user, logout_user, login_required
from FlightManagement.decorators import anonymous_user
from FlightManagement.models import *
import cloudinary.uploader


def index():
    airports = dao.load_airports()
    flight = dao.load_flights()
    return render_template('index.html', airports=airports, flight=flight)


def login_my_user():
    err_msg = ""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            if user.user_role == UserRole.ADMIN:
                return redirect('/admin')
            if user.user_role == UserRole.EMPLOYEE:
                return redirect('/staff')

            return redirect(url_for("index"))
        else:
            err_msg = "ĐĂNG NHẬP THẤT BẠI!!!"

    return render_template("index.html", err_msg=err_msg)


def login_staff():
    username = request.form['username']
    password = request.form['password']

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/staff')


def logout_my_user():
    logout_user()
    return redirect(url_for("index"))


def register():
    err_msg = ''
    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm']
        if password.__eq__(confirm):
            try:
                utils.register(name=request.form['name'],
                               password=password,
                               username=request.form['username'])

                return redirect('/')
            except:
                err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau!'
        else:
            err_msg = 'Mật khẩu KHÔNG khớp!'

    return render_template('register.html', err_msg=err_msg)


def booking():
    session['ticket'] = {
        "1": {
            "from": "Hồ Chí Minh",
            "to": "Thái Lan",
            "rank": "1",
            "fdate": "11/12/2022",
            "price": 3000000
        },
        "2": {
            "from": "Hà Nội",
            "to": "Nhật Bản",
            "rank": "2",
            "fdate": "11/12/2022",
            "price": 1500000
        },
        "3": {
            "from": "Hồ Chí Minh",
            "to": "Bình Định",
            "rank": "2",
            "fdate": "11/12/2022",
            "price": 500000
        }
    }
    airports = dao.load_airports()
    flights = []
    for f in dao.load_flights():
        flights.append(f)
    flights_num = len(flights)

    return render_template('booking.html', airports=airports, flights=flights, flights_num=flights_num)


# def search_result():
#     if request.method == 'POST':
#         password = request.form['password']
#         confirm = request.form['confirm']
#         if password.__eq__(confirm):
#             try:
#                 utils.register(name=request.form['name'],
#                                password=password,
#                                username=request.form['username'])
#
#                 return redirect('/')
#             except:
#                 err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau!'
#         else:
#             err_msg = 'Mật khẩu KHÔNG khớp!'
#
#     return render_template('confirm_booking.html')


def booking_staff():
    session['ticket'] = {
        "1": {
            "from": "Hồ Chí Minh",
            "to": "Thái Lan",
            "rank": "1",
            "fdate": "11/12/2022",
            "price": 3000000
        },
        "2": {
            "from": "Hà Nội",
            "to": "Nhật Bản",
            "rank": "2",
            "fdate": "11/12/2022",
            "price": 1500000
        },
        "3": {
            "from": "Hồ Chí Minh",
            "to": "Bình Định",
            "rank": "2",
            "fdate": "11/12/2022",
            "price": 500000
        }
    }
    airports = dao.load_airports()
    # from_airports = dao.load_from_airlines(airport_id=request.args.get("airport_id"),
    #                                        kw=request.args.get('keyword'))
    return render_template('booking_staff.html', airports=airports)


def from_airport(from_airport_id):
    f = dao.get_from_airport_by_id(from_airport_id)
    return render_template('index.html', airline=f)


def search_booking():
    airports = dao.load_airports()
    airlines = dao.load_airlines()
    airplanes = dao.load_airplanes()
    flights = dao.load_flights()
    tickets = dao.load_tickets()
    return render_template('confirm_booking.html', airports=airports, airlines=airlines,
                           airplanes=airplanes, flights=flights, tickets=tickets)


# def booking_ticket(airline_id):
#     a = dao.get_airline_by_id(airline_id)
#     return render_template('details.html', airline=a)


def details(flight_id):
    f = dao.get_flight_by_id(flight_id)
    m = utils.get_apm_by_flight_id(flight_id)
    return render_template('detail.html', flight=f, Flight_AirportMedium=m)


def confirm(flight_id):
    f = dao.get_flight_by_id(flight_id)
    m = utils.get_apm_by_flight_id(flight_id)
    r = int(request.form.get('rank'))
    infant = int(request.form.get('infant'))
    amount = 0
    seats = []
    try:
        adult = int(request.form.get('adult'))
        children = int(request.form.get('children'))
        amount = adult+children+infant
    except:
        adult = children = 0
    if amount >= dao.ts(flight_id):
        for i in range(amount):
            seats.append(dao.seat(flight_id))


    return render_template('confirm_booking.html', flight=f, Flight_AirportMedium=m,seats=seats)


def cart():
    # session['cart'] = {
    #     "1": {
    #         "id": "1",
    #         "name": "Saki Guen",
    #         "from": "Hà Nội",
    #         "to": "Nhật Bản",
    #         "rank": "2",
    #         "fdate": "11/12/2022",
    #         "price": 1500000,
    #         "seat": "G1"
    #     },
    #     "2": {
    #         "id": "2",
    #         "name": "Nhi Nguyen",
    #         "from": "Hồ Chí Minh",
    #         "to": "Thái Lan",
    #         "rank": "1",
    #         "fdate": "11/12/2022",
    #         "price": 1500000,
    #         "seat": "G2"
    #     }
    # }

    return render_template('cart.html')


def add_to_cart():
    data = request.json

    id = str(data['id'])
    name = data['name']
    price = data['price']

    key = app.config['CART_KEY']
    cart = session.get(key, {})

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


# def update_cart(product_id):
#     key = app.config['CART_KEY']
#     cart = session.get(key)
#     if cart and product_id in cart:
#         quantity = int(request.json['quantity'])
#         cart[product_id]['quantity'] = quantity
#
#     session[key] = cart
#
#     return jsonify(utils.cart_stats(cart))


# def delete_cart(product_id):
#     key = app.config['CART_KEY']
#     cart = session.get(key)
#     if cart and product_id in cart:
#         del cart[product_id]
#
#     session[key] = cart
#
#     return jsonify(utils.cart_stats(cart))


def load_flights():
    data = []

    for a in dao.load_flights():
        data.append({
            'departing_at': a.departing_at,
            'arriving_at': a.arriving_at,
            'plane_id': a.plane_id,
            'airlines': {
                'name': a.airlines.name
            }
        })

    return jsonify(data)


def airports():
    data = []

    for a in utils.load_airports():
        data.append({
            'id': a.id,
            'name': a.name
        })

    return jsonify(data)


@login_required
def pay():
    key = app.config['CART_KEY']
    cart = session.get(key)

    try:
        dao.save_receipt(cart)
    except:
        return jsonify({'status': 500})
    else:
        return jsonify({'status': 200})
