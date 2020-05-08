from flask import Flask, redirect, render_template, abort, request, make_response, jsonify, url_for
from data import db_session
from data.Users import User
from data.Money import MoneyForm
from data.Offers import Offer
from data.OffersForm import OffersForm
from data.RegisterForm import RegisterForm
from data.LoginForm import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route("/")
def index():
    session = db_session.create_session()
    offers = session.query(Offer)
    return render_template("index.html", offers=offers)


@app.route("/hello")
def hello():
    return render_template("hello.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile')
def profile():
    session = db_session.create_session()
    offers = session.query(Offer).filter(Offer.user_id == current_user.id)
    return render_template('profile.html', offers=offers)


@app.route('/money', methods=['GET', 'POST'])
def money_add():
    form = MoneyForm()
    if form.submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if form.check.data:
            user.money += form.summa.data
            session.add(user)
            session.commit()
            return redirect("/")
        return render_template('money.html',
                               message="Точно?",
                               form=form)
    return render_template('money.html', form=form)


@app.route('/buy/<int:number>', methods=['GET', 'POST'])
def buy(number):
    form = MoneyForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        offer = session.query(Offer).filter(Offer.id == number).first()
        seller = session.query(User).filter(Offer.user_id == User.id).first()
        if user and user.check_password(form.password.data):
            if form.check.data:
                if not offer.is_selled:
                    if user.money >= offer.price:
                        user.money = user.money - offer.price
                        seller.money = seller.money + offer.price
                        offer.is_selled = True
                        offer.user = user
                        session.add(user)
                        session.add(seller)
                        session.add(offer)
                        session.commit()
                        return render_template('complete.html', item=offer, user=user)
                    return render_template('buy.html',
                                            message='Недостаточно рупиев',
                                            form=form)
                return render_template('buy.html',
                                       message='Это предложение уже продано.',
                                       form=form)
            return render_template('buy.html',
                                    message='Точно?',
                                    form=form)
        return render_template('buy.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('buy.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/offers',  methods=['GET', 'POST'])
@login_required
def add_offers():
    form = OffersForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = Offer()
        news.title = form.title.data
        news.content = form.content.data
        news.price = form.price.data
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('offers.html', title='Добавление предложения',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_offers(id):
    form = OffersForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(Offer).filter(Offer.id == id,
                                          Offer.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.price.data = news.price
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(Offer).filter(Offer.id == id,
                                           Offer.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.price = form.price.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('offers.html', title='Редактирование предложения', form=form)


@app.route('/resell/<int:id>', methods=['GET', 'POST'])
@login_required
def resell(id):
    form = OffersForm()
    if request.method == "GET":
        session = db_session.create_session()
        offer = session.query(Offer).filter(Offer.id == id,
                                          Offer.user == current_user).first()
        if offer:
            form.title.data = offer.title
            form.content.data = offer.content
            form.price.data = offer.price
            offer.is_selled = False
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        offer = session.query(Offer).filter(Offer.id == id,
                                           Offer.user == current_user).first()
        if offer:
            offer.title = form.title.data
            offer.content = form.content.data
            offer.price = form.price.data
            offer.is_selled = False
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('offers.html', title='Перепродажа', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def offers_delete(id):
    session = db_session.create_session()
    news = session.query(Offer).filter(Offer.id == id,
                                       Offer.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()