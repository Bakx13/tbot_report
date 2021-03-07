import logging
import typing
import sys

import requests
import telegram
from sqlalchemy import Column, ForeignKey, UniqueConstraint, ARRAY
from sqlalchemy import Integer, BigInteger, String, Text, LargeBinary, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import relationship, backref
import sqlalchemy as sqla

import tbot_report.lib.utils as utils

if typing.TYPE_CHECKING:
    import worker

log = logging.getLogger(__name__)
current_module = sys.modules[__name__]
current_module_name = __name__

# Create a base class to define all the database subclasses
TableDeclarativeBase = declarative_base()


# Define all the database tables using the sqlalchemy declarative base
class User(DeferredReflection, TableDeclarativeBase):
    """A Telegram user who used the bot at least once."""

    # Telegram data
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    username = Column(String)
    language = Column(String, nullable=False)

    # Current wallet credit
    credit = Column(Integer, nullable=False)

    # Extra table parameters
    __tablename__ = "users"

    def __init__(self, w: "worker.Worker", **kwargs):
        # Initialize the super
        super().__init__()
        if w is not None:
            # Get the data from telegram
            self.user_id = w.telegram_user.id
            self.first_name = w.telegram_user.first_name
            self.last_name = w.telegram_user.last_name
            self.username = w.telegram_user.username
            if w.telegram_user.language_code:
                self.language = w.telegram_user.language_code
            else:
                self.language = w.cfg.language["default_language"]
        else:
            self.user_id = kwargs["user_id"]
            self.first_name = kwargs["first_name"]
            self.last_name = kwargs["last_name"]
            self.username = kwargs["username"]
            self.language = kwargs["language_code"]
        # The starting wallet value is 0
        self.credit = 0

    def __str__(self):
        """Describe the user in the best way possible given the available data."""
        if self.username is not None:
            return f"@{self.username}"
        elif self.last_name is not None:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name

    def identifiable_str(self):
        """Describe the user in the best way possible, ensuring a way back to the database record exists."""
        return f"user_{self.user_id} ({str(self)})"

    def mention(self):
        """Mention the user in the best way possible given the available data."""
        if self.username is not None:
            return f"@{self.username}"
        else:
            return f"[{self.first_name}](tg://user?id={self.user_id})"

    def recalculate_credit(self):
        """Recalculate the credit for this user by calculating the sum of the values of all their transactions."""
        '''
        valid_transactions: typing.List[Transaction] = [t for t in self.transactions if not t.refunded]
        self.credit = sum(map(lambda t: t.value, valid_transactions))
        '''

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.first_name

    def __repr__(self):
        return f"<User {self.mention()} having {self.credit} credit>"


'''
class Product(DeferredReflection, TableDeclarativeBase):
    """A purchasable product."""

    # Product id
    id = Column(Integer, primary_key=True)
    # Product name
    name = Column(String)
    # Product description
    description = Column(Text)
    # Product price, if null product is not for sale
    price = Column(Integer)
    # Image data
    image = Column(LargeBinary)
    # Product has been deleted
    deleted = Column(Boolean, nullable=False)

    # Extra table parameters
    __tablename__ = "products"

    # No __init__ is needed, the default one is sufficient

    def text(self, w: "worker.Worker", *, style: str = "full", cart_qty: int = None):
        """Return the product details formatted with Telegram HTML. The image is omitted."""
        if style == "short":
            return f"{cart_qty}x {utils.telegram_html_escape(self.name)} - {str(w.Price(self.price) * cart_qty)}"
        elif style == "full":
            if cart_qty is not None:
                cart = w.loc.get("in_cart_format_string", quantity=cart_qty)
            else:
                cart = ''
            return w.loc.get("product_format_string", name=utils.telegram_html_escape(self.name),
                             description=utils.telegram_html_escape(self.description),
                             price=str(w.Price(self.price)),
                             cart=cart)
        else:
            raise ValueError("style is not an accepted value")

    def __repr__(self):
        return f"<Product {self.name}>"

    def send_as_message(self, w: "worker.Worker", chat_id: int) -> dict:
        """Send a message containing the product data."""
        if self.image is None:
            r = requests.get(f"https://api.telegram.org/bot{w.cfg.telegram['token']}/sendMessage",
                             params={"chat_id": chat_id,
                                     "text": self.text(w),
                                     "parse_mode": "HTML"})
        else:
            r = requests.post(f"https://api.telegram.org/bot{w.cfg.telegram['token']}/sendPhoto",
                              files={"photo": self.image},
                              params={"chat_id": chat_id,
                                      "caption": self.text(w),
                                      "parse_mode": "HTML"})
        return r.json()

    def set_image(self, file: telegram.File):
        """Download an image from Telegram and store it in the image column.
        This is a slow blocking function. Try to avoid calling it directly, use a thread if possible."""
        # Download the photo through a get request
        r = requests.get(file.file_path)
        # Store the photo in the database record
        self.image = r.content


class Transaction(DeferredReflection, TableDeclarativeBase):
    """A greed wallet transaction.
    Wallet credit ISN'T calculated from these, but they can be used to recalculate it."""
    # TODO: split this into multiple tables

    # The internal transaction ID
    transaction_id = Column(Integer, primary_key=True)
    # The user whose credit is affected by this transaction
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    user = relationship("User", backref=backref("transactions"))
    # The value of this transaction. Can be both negative and positive.
    value = Column(Integer, nullable=False)
    # Refunded status: if True, ignore the value of this transaction when recalculating
    refunded = Column(Boolean, default=False)
    # Extra notes on the transaction
    notes = Column(Text)

    # Payment provider
    provider = Column(String)
    # Transaction ID supplied by Telegram
    telegram_charge_id = Column(String)
    # Transaction ID supplied by the payment provider
    provider_charge_id = Column(String)
    # Extra transaction data, may be required by the payment provider in case of a dispute
    payment_name = Column(String)
    payment_phone = Column(String)
    payment_email = Column(String)

    # Order ID
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    order = relationship("Order")

    # Extra table parameters
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("provider", "provider_charge_id"),)

    def text(self, w: "worker.Worker"):
        string = f"<b>T{self.transaction_id}</b> | {str(self.user)} | {w.Price(self.value)}"
        if self.refunded:
            string += f" | {w.loc.get('emoji_refunded')}"
        if self.provider:
            string += f" | {self.provider}"
        if self.notes:
            string += f" | {self.notes}"
        return string

    def __repr__(self):
        return f"<Transaction {self.transaction_id} for User {self.user_id}>"
'''


class Client(DeferredReflection, TableDeclarativeBase):
    """A greed administrator with his permissions."""

    # The telegram id
    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    user = relationship("User")

    id = Column(BigInteger, primary_key=False, autoincrement=True)
    timetable_id = Column(BigInteger, ForeignKey("timetable.client_id"), primary_key=True)
    timetable = relationship("TimeTable")  # Permissions
    coach_id = Column(BigInteger, ForeignKey("coachs.user_id"), primary_key=False)
    coach = relationship("Coach")
    deleted = Column(Boolean, nullable=False, default=False)

    # Extra table parameters
    __tablename__ = "client"


class Coach(DeferredReflection, TableDeclarativeBase):
    """A greed administrator with his permissions."""

    # The telegram id
    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    user = relationship("User")
    timetable_id = Column(BigInteger, ForeignKey("timetable.coach_id"), primary_key=True)
    timetable = relationship("TimeTable")  # Permissions

    id = Column(BigInteger, primary_key=False, autoincrement=True)
    about = Column(String, nullable=False)
    picture = Column(String)

    deleted = Column(Boolean, nullable=False, default=False)
    # Extra table parameters
    __tablename__ = "coachs"

    def __repr__(self):
        return f"<Coach {self.user_id}>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        return

    def create(self, w: "worker.Worker", user: User, **kwargs):
        # Initialize the super
        super().__init__(**kwargs)
        # Get the data from telegram
        self.user_id = w.telegram_user.id
        self.first_name = w.telegram_user.first_name
        self.last_name = w.telegram_user.last_name
        self.username = w.telegram_user.username
        if w.telegram_user.language_code:
            self.language = w.telegram_user.language_code
        else:
            self.language = w.cfg.language["default_language"]
        # The starting wallet value is 0
        self.credit = 0


class Admin(DeferredReflection, TableDeclarativeBase):
    """Описание класса для работы с таблицей бассейнов"""

    # The telegram id
    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    user = relationship("User")

    id = Column(BigInteger, primary_key=False, autoincrement=True)
    # Permissions

    edit_products = Column(Boolean, default=False)
    receive_orders = Column(Boolean, default=False)
    create_transactions = Column(Boolean, default=False)
    display_on_help = Column(Boolean, default=False)
    is_owner = Column(Boolean, default=False)
    # Live mode enabled
    live_mode = Column(Boolean, default=False)

    # Extra table parameters
    __tablename__ = "admins"

    def __repr__(self):
        return f"<Admin {self.user_id}>"


class TimeTable(DeferredReflection, TableDeclarativeBase):
    """An order which has been placed by an user.
    It may include multiple products, available in the OrderItem table."""

    # The unique order id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Date of creation
    creation_date = Column(DateTime, nullable=False)

    #  Связь с тренером
    coach_id = Column(Integer, nullable=False)

    #  Связь с бассейном
    swimpool_id = Column(Integer, nullable=False)

    #связь с клиентом
    client_id = Column(Integer, nullable=False)



    # Date of delivery
    # delivery_date = Column(DateTime)
    # Date of refund: if null, product hasn't been refunded
    # refund_date = Column(DateTime)
    # Refund reason: if null, product hasn't been refunded
    # refund_reason = Column(Text)
    # List of items in the order
    # Extra details specified by the purchasing user
    notes = Column(Text)

    # Extra table parameters
    __tablename__ = "timetable"

    def __repr__(self):
        return f"<TimeTable('%s','%s', '%s',)>" % (self.id, self.client_id, self.coach_id)

    def text(self, w: "worker.Worker", session, user=False):
        '''
        joined_self = session.query(Order).filter_by(order_id=self.order_id).join(Transaction).one()
        items = ""
        for item in self.items:
            items += item.text(w) + "\n"
        if self.delivery_date is not None:
            status_emoji = w.loc.get("emoji_completed")
            status_text = w.loc.get("text_completed")
        elif self.refund_date is not None:
            status_emoji = w.loc.get("emoji_refunded")
            status_text = w.loc.get("text_refunded")
        else:
            status_emoji = w.loc.get("emoji_not_processed")
            status_text = w.loc.get("text_not_processed")
        if user and w.cfg.appearance["full_order_info"] == "no":
            return w.loc.get("user_order_format_string",
                             status_emoji=status_emoji,
                             status_text=status_text,
                             items=items,
                             notes=self.notes,
                             value=str(w.Price(-joined_self.transaction.value))) + \
                   (w.loc.get("refund_reason", reason=self.refund_reason) if self.refund_date is not None else "")
        else:
            return status_emoji + " " + \
                   w.loc.get("order_number", id=self.order_id) + "\n" + \
                   w.loc.get("order_format_string",
                             user=self.user.mention(),
                             date=self.creation_date.isoformat(),
                             items=items,
                             notes=self.notes if self.notes is not None else "",
                             value=str(w.Price(-joined_self.transaction.value))) + \
                   (w.loc.get("refund_reason", reason=self.refund_reason) if self.refund_date is not None else "")
        '''


class TimeTableItem(DeferredReflection, TableDeclarativeBase):
    """Одна строчка из расписания занятий"""

    # The unique item id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # The product that is being ordered
    item = Column(String, nullable=False)

    #День недели
    day_of_week = Column(String)

    #Признак повторения
    prop = Column(String)

    # Время начала периода
    start_time = Column(DateTime, nullable=False)

    #Время окончания периода
    end_time = Column(DateTime, nullable=False)

    timetable_id = Column(Integer, ForeignKey("timetable.id"), nullable=False)



    # Extra table parameters
    __tablename__ = "timetableitems"

    def text(self):
        return f""

    def __repr__(self):
        return f"<TimeTableItem {self.id}>"


class District(DeferredReflection, TableDeclarativeBase):
    """Район города"""

    # The unique item id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Ссылка на город, в котором расположен район
    city_id = Column(BigInteger, ForeignKey("city.id"), primary_key=False)
    city = relationship("City")

    # Название района
    name = Column(String, nullable=False)
    # краткое описание, может быть пустым
    description = Column(String)

    # Extra table parameters
    __tablename__ = "district"

    def text(self):
        return f""

    def __repr__(self):
        return f"<TimeTableItem {self.id}>"


class City(DeferredReflection, TableDeclarativeBase):
    """Города страны, в которых мы предоставляем услугу"""

    # The unique item id
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Название города
    name = Column(String, nullable=False)

    description = Column(String)

    # Extra table parameters
    __tablename__ = "city"

    def text(self):
        return f""

    def __repr__(self):
        return f"<city {self.id}>"


# ---- swimbot tables


class SwimPool(DeferredReflection, TableDeclarativeBase):
    """Бассейн, в который можно записаться"""
    # Product id
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ссылка на таблицы с районами города
    distict_id = Column(BigInteger, ForeignKey("district.id"), primary_key=False)
    district = relationship("District")

    # ссылка на таблицу с расписанием занятий
    timetable_id = Column(BigInteger, ForeignKey("timetable.swimpool_id"), primary_key=False)
    timetable = relationship("TimeTable")  # Permissions

    # фото бассейна
    image = Column(LargeBinary)

    # адрес бассейна
    address = Column(String, nullable=False)

    # Название бассейна
    name = Column(String, nullable=False)

    # Описание бассейна
    description = Column(Text)

    # Стоимость разового посещения
    price = Column(Integer)

    # Product has been deleted
    deleted = Column(Boolean, nullable=False, default=False)
    # Extra table parameters
    __tablename__ = "swimpool"

    # Get all list jf swimpool

    def get_all_swimpool(self, SwimPool: list):
        swimpool = session.query(SwimPool).all()
        return swimpool

    # No __init__ is needed, the default one is sufficient

    def text(self, w: "worker.Worker", *, style: str = "full", cart_qty: int = None):
        """Return the product details formatted with Telegram HTML. The image is omitted."""
        if style == "short":
            return f"x {utils.telegram_html_escape(self.name)} - {str(w.Price(self.price))}"
        elif style == "full":
            return w.loc.get("swimpool_format_string", name=utils.telegram_html_escape(self.name),
                             description=utils.telegram_html_escape(self.description),
                             price=str(w.Price(self.price)))
        else:
            raise ValueError("style is not an accepted value")

    def __repr__(self):
        return f"<Product {self.name}>"

    def send_as_message(self, w: "worker.Worker", chat_id: int) -> dict:
        """Send a message containing the product data."""
        if self.image is None:
            r = requests.get(f"https://api.telegram.org/bot{w.cfg.telegram['token']}/sendMessage",
                             params={"chat_id": chat_id,
                                     "text": self.text(w),
                                     "parse_mode": "HTML"})
        else:
            r = requests.post(f"https://api.telegram.org/bot{w.cfg.telegram['token']}/sendPhoto",
                              files={"photo": self.image},
                              params={"chat_id": chat_id,
                                      "caption": self.text(w),
                                      "parse_mode": "HTML"})
        return r.json()

    def set_image(self, file: telegram):
        """Download an image from Telegram and store it in the image column.
        This is a slow blocking function. Try to avoid calling it directly, use a thread if possible.
        :type file: object"""
        # Download the photo through a get request
        r = requests.get(file.file_path)
        # Store the photo in the database record
        self.image = r.content
