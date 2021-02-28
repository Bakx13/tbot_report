import logging

log = logging.getLogger(__name__)

ROLES = ["USER", "COACH", "ADMIN"]


def telegram_html_escape(string: str):
    return string.replace("<", "&lt;") \
        .replace(">", "&gt;") \
        .replace("&", "&amp;") \
        .replace('"', "&quot;")


def get_key(d, value):
    for k, v in d:
        if v == value:
            return k
    return None


def mkinst(cls, *args, **kwargs):
    try:
        return globals()[cls](*args, **kwargs)
    except:
        raise NameError("Class %s is not defined" % cls)


def IsAdmin(role):
    return True if ROLES.count(role) > 0 else False


def IsCoach(role):
    return True if ROLES.count(role) > 0 else False


def IsRegisterUser(role):
    return True if ROLES.count(role) > 0 else False
