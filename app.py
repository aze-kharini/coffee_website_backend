from flask import Flask, render_template, session, redirect, url_for, g, request, make_response
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, CatalogForm, ForgotPasswordForm, AlterUserForm, ResetPasswordForm, DeleteForm, AddVarietyForm, AlterVarietyForm, RateVarietyForm, UsersSearchForm, ChangeProfileForm, SweetnessRecommendationForm, BodyRecommendationForm, FlavorRecommendationForm, FlavorsRecommendationForm
from functools import wraps
from mail import reset_password_mail
from actors import user, variety_class
from sql_funcs import get_flavors, get_regions, get_user_dict, get_variety_dict, get_variety_names, create_user, create_variety

"""
My website has three types of users: standard, expert and admin

1. Logged out
    - When you are not logged in you can view the main page
    - register, login
    - look at the catalog and different individual varieties
    - if you forgot your password, you can click on an option 'forgot password' on the login page, which will send you an email with a link to reset the password

2. Standard User
    - Once you log in, you are able to rate varieties (but only once per variety for 30 days)
    - Take the test which will recommend you coffee varieties and store you preferences 
    - Look at you profile, where you will have the recommended varieties displayed based on the current information of the varieties, you can change your profile as well
    - Look at the descendants and ancestors of different varieties on their variety page

3. Expert User (example account user_id: 'expert', password: 'expert')
    - If you get your user_type changed to expert by an admin, you can alter varieties
    - You are able to change the information about a variety, for example when it becomes outdated
    - You are also able to create completely new varieties in order to expand the database (there is a link at the bottom of the catalog page)

4. Admin User (admin account user_id: 'admin', password: 'Scott_labs-28')
    - When you are an admin, the credentials to log in are given to you by the website owner
    - You are now able to look up user profiles (on the main page there is a section title Users Lookup)
    - Change the contents of the users profile, for example changing their type to expert
    - You can also delete users and varieties from the database

"""

app = Flask(__name__)
# For a session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# For forms
app.config["SECRET_KEY"] = "opaweriycnweuraycsiyomfihvaewiofhvawpo"
Session(app)
# For the database
app.teardown_appcontext(close_db)


@app.before_request
def logged_in_user():
    g.user = session.get("user_id", None)
    g.type = session.get("user_type", None)

########################################################################################################################
# wrappers


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        db = get_db()
        user_type_sql = db.execute(
            """SELECT user_type FROM users WHERE user_id =?;""", (g.user,)).fetchone()
        close_db()
        user_type = user_type_sql['user_type']
        if g.type == 'standard' or g.type == 'expert' or user_type != 'admin':
            return redirect(url_for("info_site", action='admin_required'))
        return view(*args, **kwargs)
    return wrapped_view


def expert_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.type == 'standard':
            return redirect(url_for("info_site", action='expert_required'))
        return view(*args, **kwargs)
    return wrapped_view


########################################################################################################################
# Routes


@app.route("/")
def index():
    db = get_db()
    recommended_varieties_sql = db.execute(
        """SELECT * FROM varieties ORDER BY rating DESC LIMIT 6;""").fetchall()
    recommended_varieties = []
    for variety_dic in recommended_varieties_sql:
        variety_obj = create_variety(variety_dic)
        recommended_varieties.append(variety_obj)
    return render_template("index.html", recommended_varieties=recommended_varieties)

# https://www.digitalocean.com/community/tutorials/how-to-handle-errors-in-a-flask-application site helped me with the errorhandler routes

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('info_site', action='404'))


@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for('info_site', action='500'))


@app.route("/info_site/<string:action>")
def info_site(action):
    message = ""
    if action == 'logged_out':
        if session.get("user_id", None) is None:
            message = "Logged out successfully"
        else:
            message = "There was a problem during logout."
    elif action == 'mail_sent':
        message = 'E-mail was sent, check your inbox and click on the link.'
    elif action == 'expert_required':
        message = "'Expert' user required. See the main page for more information."
    elif action == 'admin_required':
        message = 'You do not have access to this website.'
    elif action == 'change_admin':
        message = 'Cannot alter an Admin user profile.'
    elif action =='voted':
        message = 'You have already rated this variety.'
    elif action == '404':
        message = 'Page not found.'
    elif action == '500':
        message = "Something went wrong."
    return render_template('info_site.html', message=message)

########################################################################################################################
# Variety related routes


@app.route("/catalog", methods=["POST", "GET"])
def catalog():
    form = CatalogForm()
    filtered_varieties = []
    found_varieties = None
    # Populating the form
    # Regions
    form.region_choices.choices = get_regions()
    # Flavors
    form.flavor_choices.choices = get_flavors()
    # Varieties to display
    db = get_db()
    varieties_sql = db.execute("""
    SELECT * FROM varieties WHERE var_id > 3;
    """).fetchall()
    for variety_dic in varieties_sql:
        variety_obj = create_variety(variety_dic)
        filtered_varieties.append(variety_obj)
    # Response
    if form.validate_on_submit() or form.region_choices.data is not None or form.flavor_choices.data is not None:
        varieties = []  # Create a list of var objects and then append them to the filtered_list if they pass all of the tests
        # Getting data from the form
        name = form.name_search.data
        rating = form.rating.data
        regions = form.region_choices.data
        flavors = form.flavor_choices.data
        if rating is None:
            rating = 0
        rating = int(rating)
        # Filling out the list
        varieties_sql = db.execute("""
        SELECT * FROM varieties
        WHERE rating >= ? AND var_id > 3 AND name LIKE '%' || ? || '%';
        """, (rating, name)).fetchall()
        for variety_dict in varieties_sql:
            variety_obj = create_variety(variety_dict)
            varieties.append(variety_obj)
        # Filtering the objects
        filtered_varieties = []
        for variety_obj in varieties:
            passed = True
            for region in regions:
                variety_regions = variety_obj.get_regions()
                if region not in variety_regions:
                    passed = False
            for flavor in flavors:
                variety_flavors = variety_obj.get_flavors()
                if flavor not in variety_flavors:
                    passed = False
            if passed:
                filtered_varieties.append(variety_obj)
        # returning the number of found varieties after the tests
        found_varieties = len(filtered_varieties)
    return render_template('catalog.html', form=form, varieties=filtered_varieties, found_varieties=found_varieties)


@app.route("/variety/<int:var_id>", methods=["POST", "GET"])
def variety(var_id):
    form = RateVarietyForm()
    variety_obj = create_variety(get_variety_dict(var_id))
    ancestors = []
    descendants = []
    voted = False
    if request.cookies.get(str(var_id)) == g.user:
        voted=True
    if g.user is not None:
        ancestors_id = variety_obj.get_ancestors_id(var_id)
        ancestors_id.remove(var_id)
        ancestors_id = sorted(ancestors_id)
        ancestors = [create_variety(get_variety_dict(ancestor_id))
                     for ancestor_id in ancestors_id]
        descendants_id = variety_obj.get_descendants_id(var_id)
        descendants_id.remove(var_id)
        descendants_id = sorted(descendants_id)
        descendants = [create_variety(get_variety_dict(
            descendant_id)) for descendant_id in descendants_id]
    response = make_response(render_template('variety.html', variety=variety_obj, form=form, ancestors=ancestors, found_ancestors=len(ancestors), descendants=descendants, found_descendants=len(descendants), voted=voted))
    if form.validate_on_submit():
        num_of_ratings = variety_obj.num_of_ratings + 1
        rating = form.rating.data
        new_rating = (variety_obj.rating*(num_of_ratings-1) +
                      rating)/(num_of_ratings)
        variety_obj.rating = round(new_rating, 2)
        variety_obj.num_of_ratings = num_of_ratings
        variety_obj.update_variety()
        voted = True
        response = make_response(render_template('variety.html', variety=variety_obj, form=form, ancestors=ancestors, found_ancestors=len(ancestors), descendants=descendants, found_descendants=len(descendants), voted=voted))
        response.set_cookie(str(var_id), g.user, max_age=30*24*60*60)
    return response

########################################################################################################################
# User Related routes

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_dict = {
            'user_id': form.user_id.data,
            'mail': form.mail.data,
            'user_type': 'standard'
        }
        # User Data Validation
        possible_clashing_user_id = get_user_dict(user_dict['user_id'])
        possible_clashing_user_mail = get_user_dict(
            None, user_dict['mail'])
        if possible_clashing_user_id is not None:
            form.user_id.errors.append("Username already taken!")
        elif possible_clashing_user_mail is not None:
            form.mail.errors.append("E-mail address already taken!")
        else:
            user_dict['password'] = generate_password_hash(
                form.password.data)
            # Adding the user to the database
            user_obj = create_user(user_dict)
            user_obj.add_user()
            return redirect(url_for("login"))
    return render_template("register_form.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        user = get_user_dict(user_id)
        # User Data Validation
        if user is None:
            form.user_id.errors.append("No such user!")
        elif not check_password_hash(user["password"], password):
            form.password.errors.append("Incorrect Password!")
        else:
            session.clear()
            user_obj = create_user(get_user_dict(user_id))
            # Updating the session
            session["user_id"] = user_id
            session["user_type"] = user_obj.type
            # Returning to the webpage we were on after log in
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login_form.html", form=form)


@login_required
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("info_site", action='logged_out'))


@app.route("/forgot_password", methods=['POST', 'GET'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        mail = form.mail.data
        user_id_check = get_user_dict(user_id)
        user_mail_check = get_user_dict(user_id, mail)
        if user_id_check is None:
            form.user_id.errors.append("No User ID found!")
        elif user_mail_check is None:
            form.mail.errors.append("No matching E-mail Address found!")
        else:
            # send an email
            reset_password_mail(mail, user_id)
            return redirect(url_for('info_site', action='mail_sent'))

    return render_template('forgot_password.html', form=form)


@app.route("/reset_password/<string:user_id>", methods=['POST', 'GET'])
def reset_password(user_id):
    # change the password by looking up the user with the email
    # set the new password
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_dict = get_user_dict(user_id)
        user_obj = create_user(user_dict)
        user_obj.password = generate_password_hash(form.password.data)
        user_obj.update_user()

        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@login_required
@app.route("/profile/<string:user_id>")
def profile(user_id):
    user_info = get_user_dict(user_id)
    user_obj = create_user(user_info)
    test_done = user_obj.test_done_check()
    recommended_varieties = None
    if test_done:
        user_obj.get_flavors()
        user_obj.get_user_preferences()
        user_preferences = user_obj.get_preferences()
        recommended_varieties = [create_variety(get_variety_dict(
            var_id)) for var_id in user_preferences.keys()]
        recommended_varieties = recommended_varieties[0:6]
    return render_template('profile.html', profile_info=user_obj, recommended_varieties=recommended_varieties)


@login_required
@app.route("/change_profile/<string:user_id>", methods=['POST', 'GET'])
def change_profile(user_id):
    form = ChangeProfileForm()
    user_obj = create_user(get_user_dict(user_id))
    if form.validate_on_submit():
        changed_user_id = form.user_id.data
        changed_mail = form.mail.data
        # User Data Validation
        if changed_user_id != user_obj.user_id:
            possible_clashing_user_id = get_user_dict(changed_user_id)
        else:
            possible_clashing_user_id = None
        if changed_mail != user_obj.mail:
            possible_clashing_user_mail = get_user_dict(None, changed_mail)
        else:
            possible_clashing_user_mail = None

        if possible_clashing_user_id is not None:
            form.user_id.errors.append("Username already taken!")
        elif possible_clashing_user_mail is not None:
            form.mail.errors.append("E-mail address already taken!")
        else:
            # Update the profile
            user_obj.mail = changed_mail
            # user_obj.user_id = changed_user_id
            user_obj.update_user(changed_user_id)
            session["user_id"] = changed_user_id
            return redirect(url_for('profile', user_id=user_obj.user_id))
    form.user_id.data = user_id
    form.mail.data = user_obj.mail
    return render_template('change_profile_form.html', user_id=user_id, form=form)


########################################################################################################################
# Admin Varieties


@expert_required
@app.route("/add_variety", methods=['GET', 'POST'])
def add_variety():
    form = AddVarietyForm()

    # Regions
    form.region_choices.choices = get_regions()
    # Flavors
    form.flavor_choices.choices = get_flavors()
    # Variety parents
    form.parent_choices.choices = get_variety_names()

    if form.validate_on_submit():
        var_dict = {
            'var_id': None,
            'name': form.name.data,
            'rating': int(form.rating.data),
            'num_of_ratings': 1,
            'description': form.description.data,
            'sweetness': float(form.sweetness.data),
            'body': float(form.body.data),
            'flavor': float(form.flavor.data)
        }
        # User Data Validation
        possible_clashing_name = get_variety_dict(
            var_dict['var_id'], var_dict['name'])
        if possible_clashing_name is not None:
            form.name.errors.append(
                "There already exists a variety with such a name.")
        else:
            # Adding it to the database
            var_obj = create_variety(var_dict)
            var_obj.regions = form.region_choices.data
            var_obj.flavors = form.flavor_choices.data
            parents_dic = form.parent_choices.data
            parents_id = []
            for parent_name in parents_dic:
                parent_dic = get_variety_dict(None, parent_name)
                parents_id.append(parent_dic['var_id'])
            var_obj.parents = parents_id
            var_obj.add_variety()
            var_obj.add_regions()
            var_obj.add_flavors()
            var_obj.add_relations()
            return redirect(url_for('variety', var_id=var_obj.var_id))
    return render_template('add_variety.html', form=form)


@admin_required
@app.route("/delete_variety/<int:var_id>", methods=['GET', 'POST'])
def delete_variety(var_id):
    form = DeleteForm()
    if form.validate_on_submit():
        confirmation = form.confirmation.data
        if confirmation == 'yes':
            variety_obj = create_variety(get_variety_dict(var_id))
            variety_obj.delete_variety()
        return redirect(url_for('catalog'))
    return render_template('delete_confirmation.html', form=form)


@expert_required
@app.route("/alter_variety/<int:var_id>", methods=['GET', 'POST'])
def alter_variety(var_id):
    # have to do some user data validation
    form = AlterVarietyForm()
    variety_obj = create_variety(get_variety_dict(var_id))
    all_regions = get_regions()
    all_flavors = get_flavors()
    var_regions = variety_obj.get_regions()
    var_flavors = variety_obj.get_flavors()
    form.delete_regions.choices = [region for region in var_regions]
    form.add_regions.choices = [
        region for region in all_regions if region not in var_regions]
    form.delete_flavors.choices = [flavor for flavor in var_flavors]
    form.add_flavors.choices = [
        flavor for flavor in all_flavors if flavor not in var_flavors]
    if form.validate_on_submit():
        # Updating the object
        changed_var_name = form.name.data
        # User data validation
        if changed_var_name != variety_obj.name:
            possible_clashing_name = get_variety_dict(
                variety_obj.var_id, variety_obj.name)
        else:
            possible_clashing_name = None
        if possible_clashing_name is not None:
            form.name.errors.append(
                "There already exists a variety with such a name.")
        else:
            variety_obj.name = form.name.data
            variety_obj.description = form.description.data
            variety_obj.sweetness = float(form.sweetness.data)
            variety_obj.body = float(form.body.data)
            variety_obj.flavor = float(form.flavor.data)
            updated_regions = []+form.add_regions.data
            for region in variety_obj.regions:
                if region not in form.delete_regions.data:
                    updated_regions.append(region)
            variety_obj.regions = updated_regions
            updated_flavors = []+form.add_flavors.data
            for flavor in variety_obj.flavors:
                if flavor not in form.delete_flavors.data:
                    updated_flavors.append(flavor)
            variety_obj.flavors = updated_flavors
            # Updating the database
            variety_obj.update_variety()
            variety_obj.update_regions()
            variety_obj.update_flavors()
            return redirect(url_for('variety', var_id=var_id))
    # Pre populating the form had to go under the response, otherwise the response would contain just the prepopulated data
    form.name.data = variety_obj.name
    form.description.data = variety_obj.description
    form.sweetness.data = float(variety_obj.sweetness)
    form.body.data = float(variety_obj.body)
    form.flavor.data = float(variety_obj.flavor)
    return render_template('alter_variety.html', form=form)


########################################################################################################################
# Admin Users
# To create an admin account, it has to be inserted into the database manually
# Expert users are created by asking an admin to award them the expert user, which they will do by looking them up and changing the user type

@admin_required
@app.route("/users_search", methods=["POST", 'GET'])
def users_search():
    form = UsersSearchForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        existing_user = get_user_dict(user_id)
        # User Data Validation
        if existing_user is None:
            form.user_id.errors.append("No such user found.")
        else:
            return redirect(url_for('profile', user_id=user_id))

    return render_template('users_search_form.html', form=form)


@admin_required
@app.route("/delete_user/<string:user_id>", methods=["POST", 'GET'])
def delete_user(user_id):
    form = DeleteForm()
    if form.validate_on_submit():
        confirmation = form.confirmation.data
        if confirmation == 'yes':
            user_obj = create_user(get_user_dict(user_id))
            user_obj.delete_user()
        return redirect(url_for('users_search'))
    return render_template('delete_confirmation.html', form=form)


@admin_required
@app.route("/alter_user/<string:user_id>", methods=["POST", 'GET'])
def alter_user(user_id):
    form = AlterUserForm()
    user_obj = create_user(get_user_dict(user_id))
    if user_obj.type == 'admin':
        return redirect(url_for('info_site', action='change_admin'))
    if form.validate_on_submit():
        # Updating the object
        changed_user_id = form.user_id.data
        changed_mail = form.mail.data
        # User Data Validation
        if changed_user_id != user_obj.user_id:
            possible_clashing_user_id = get_user_dict(changed_user_id)
        else:
            possible_clashing_user_id = None
        if changed_mail != user_obj.mail:
            possible_clashing_user_mail = get_user_dict(None, changed_mail)
        else:
            possible_clashing_user_mail = None

        if possible_clashing_user_id is not None:
            form.user_id.errors.append("Username already taken!")
        elif possible_clashing_user_mail is not None:
            form.mail.errors.append("E-mail address already taken!")
        else:
            # Updating the database
            user_obj.mail = form.mail.data
            user_obj.type = form.type.data
            user_obj.update_user(changed_user_id)
            return redirect(url_for('profile', user_id=user_obj.user_id))
    # Pre populating the form had to go under the response, otherwise the response would contain just the prepopulated data
    form.user_id.data = user_obj.user_id
    form.mail.data = user_obj.mail
    form.type.data = user_obj.type
    return render_template('alter_user.html', form=form)

########################################################################################################################
# Recommendations


@login_required
@app.route("/recommendation_form/")
def recommendation_form():
    return redirect(url_for('sweetness_rec_form'))


def calc_rec_value(answer1, answer2, answer3, answer4):
    return (int(answer1) + int(answer2) - int(answer3) - int(answer4))/4


@login_required
@app.route("/recommendation_form/sweetness", methods=['POST', 'GET'])
def sweetness_rec_form():
    form = SweetnessRecommendationForm()
    if form.validate_on_submit():
        session['sweetness'] = calc_rec_value(
            form.question_1.data, form.question_2.data, form.question_3.data, form.question_4.data)
        return redirect(url_for('body_rec_form'))
    return render_template('recommendation_form.html', part='sweetness', form=form)


@login_required
@app.route("/recommendation_form/body", methods=['POST', 'GET'])
def body_rec_form():
    form = BodyRecommendationForm()
    if form.validate_on_submit():
        session['body'] = calc_rec_value(
            form.question_1.data, form.question_2.data, form.question_3.data, form.question_4.data)
        return redirect(url_for('flavor_rec_form'))
    return render_template('recommendation_form.html', part='body', form=form)


@login_required
@app.route("/recommendation_form/flavor", methods=['POST', 'GET'])
def flavor_rec_form():
    form = FlavorRecommendationForm()
    if form.validate_on_submit():
        session['flavor'] = calc_rec_value(
            form.question_1.data, form.question_2.data, form.question_3.data, form.question_4.data)
        return redirect(url_for('flavors_rec_form'))
    return render_template('recommendation_form.html', part='flavor', form=form)


@login_required
@app.route("/recommendation_form/flavors", methods=['POST', 'GET'])
def flavors_rec_form():
    form = FlavorsRecommendationForm()
    form.flavors.choices = get_flavors()
    if form.validate_on_submit():
        session['flavors'] = form.flavors.data
        return redirect(url_for('results_rec_form'))
    return render_template('recommendation_form.html', part='flavors', form=form)


@login_required
@app.route("/recommendation_form/results")
def results_rec_form():
    user_obj = create_user(get_user_dict(g.user))
    user_obj.sweetness = session.get('sweetness', None)
    user_obj.body = session.get('body', None)
    user_obj.flavor = session.get('flavor', None)
    user_obj.flavors = session.get("flavors", None)
    # check if the user did the test before, if not, just update
    test_done = user_obj.test_done_check()
    if test_done:
        user_obj.update_user()
    else:
        user_obj.add_user_preferences()
        user_obj.add_user_flavors()
    user_preferences = user_obj.get_preferences()
    recommended_varieties = [create_variety(get_variety_dict(
        var_id)) for var_id in user_preferences.keys()]
    return render_template('recommendation_results.html', user_obj=user_obj, recommended_varieties=recommended_varieties[0:6])
