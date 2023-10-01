from database import get_db, close_db
from actors import variety_class, user

# Functions for sql queries


def get_user_dict(user_id, mail=None, type=None):
    db = get_db()
    if type and mail:
        user_dict = db.execute("""SELECT * FROM users
        WHERE user_id = ? AND mail = ? AND user_type = ?;""", (user_id, mail, type)).fetchone()
    elif mail:
        user_dict = db.execute("""SELECT * FROM users
        WHERE mail = ?;""", (mail,)).fetchone()
    elif type:
        user_dict = db.execute("""SELECT * FROM users
        WHERE user_id = ? AND user_type = ?;""", (user_id, type)).fetchone()
    else:
        user_dict = db.execute("""SELECT * FROM users
        WHERE user_id = ?;""", (user_id,)).fetchone()
    close_db()
    return user_dict


def create_user(user_dict):
    user_obj = user(user_dict['user_id'], user_dict['password'],
                    user_dict['mail'], user_dict['user_type'])
    return user_obj


def get_variety_dict(var_id, name=None):
    db = get_db()
    if name:
        var_dict = db.execute(
            """SELECT * FROM varieties WHERE name = ?; """, (name,)).fetchone()
    else:
        var_dict = db.execute(
            """SELECT * FROM varieties WHERE var_id = ?; """, (var_id,)).fetchone()
    close_db()
    return var_dict


def create_variety(var_dict):
    variety_obj = variety_class(var_dict['var_id'], var_dict['name'], var_dict['rating'], var_dict['num_of_ratings'],
                                var_dict['description'], var_dict['sweetness'], var_dict['body'], var_dict['flavor'])
    return variety_obj


def get_regions():
    db = get_db()
    regions_sql = db.execute("""SELECT region FROM regions
    GROUP BY region;""").fetchall()
    regions = [region['region'] for region in regions_sql]
    close_db()
    return regions


def get_flavors():
    db = get_db()
    flavors_sql = db.execute("""SELECT flavor FROM flavors
    GROUP BY flavor;""").fetchall()
    flavors = [flavor['flavor'] for flavor in flavors_sql]
    close_db()
    return flavors


def get_variety_names():
    db = get_db()
    variety_names_sql = db.execute(
        """SELECT name FROM varieties ORDER BY rating;""").fetchall()
    variety_names = [variety_name['name']
                     for variety_name in variety_names_sql]
    close_db()
    return variety_names


