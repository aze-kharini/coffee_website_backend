from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, DecimalField, widgets, BooleanField, IntegerField, EmailField, TextAreaField
# Since I had to install additional packages, I do not think that email validator will work on the server
from wtforms.validators import InputRequired, EqualTo, NumberRange, Email


# I have taken the code for creating a new field from this website: https://gist.github.com/ectrimble20/468156763a1389a913089782ab0f272e 
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

########################################################################################################################
# Variety related forms


class CatalogForm(FlaskForm):
    name_search = StringField("Name")
    rating = DecimalField("Rating", validators=[NumberRange(0, 5), InputRequired()], default=0)
    region_choices = MultiCheckboxField("Region", coerce=str)
    flavor_choices = MultiCheckboxField("Flavor", coerce=str)
    submit = SubmitField("Search")


class AddVarietyForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    rating = DecimalField("Rating", validators=[NumberRange(0, 5), InputRequired()])
    sweetness = DecimalField("Sweetness", validators=[
                             InputRequired(), NumberRange(-10, 10)])
    body = DecimalField("Body", validators=[
                        InputRequired(), NumberRange(-10, 10)])
    flavor = DecimalField("Flavor", validators=[
                          InputRequired(), NumberRange(-10, 10)])
    region_choices = MultiCheckboxField("Region", coerce=str)
    flavor_choices = MultiCheckboxField("Flavor", coerce=str)
    parent_choices = MultiCheckboxField("Genetic Parents", coerce=str)
    submit = SubmitField("Add")


class AlterVarietyForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    sweetness = DecimalField("Sweetness", validators=[
                             InputRequired(), NumberRange(-10, 10)])
    body = DecimalField("Body", validators=[
                        InputRequired(), NumberRange(-10, 10)])
    flavor = DecimalField("Flavor", validators=[
                          InputRequired(), NumberRange(-10, 10)])
    delete_regions = MultiCheckboxField("Delete Regions", coerce=str)
    add_regions = MultiCheckboxField("Add Regions", coerce=str)
    delete_flavors = MultiCheckboxField("Delete Flavors", coerce=str)
    add_flavors = MultiCheckboxField("Add Flavors", coerce=str)
    submit = SubmitField("Alter")


class RateVarietyForm(FlaskForm):
    rating = IntegerField("How would you rate this variety?",
                          validators=[NumberRange(1, 5)])
    submit = SubmitField("Rate variety!")


########################################################################################################################
# User Related Forms

class RegistrationForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    mail = StringField("E-mail Address", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    password2 = PasswordField("Repeat Password", validators=[
                              InputRequired(), EqualTo('password')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    mail = EmailField("E-mail Address", validators=[InputRequired(), Email()])
    submit = SubmitField("Send Email")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[InputRequired()])
    password2 = PasswordField("Repeat new password", validators=[
                              InputRequired(), EqualTo('password')])
    submit = SubmitField("Reset password")


class ChangeProfileForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    mail = EmailField("E-mail Address", validators=[InputRequired(), Email()])
    submit = SubmitField("Change")

########################################################################################################################
# Admin Related forms


class UsersSearchForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    submit = SubmitField("Search")


class AlterUserForm(FlaskForm):
    user_id = StringField("Username", validators=[InputRequired()])
    mail = EmailField("E-mail Address", validators=[InputRequired(), Email()])
    type = SelectField("Type of a user", choices=[
                       'standard', 'expert'], validators=[InputRequired()])
    submit = SubmitField("Alter")


class DeleteForm(FlaskForm):
    confirmation = SelectField('Do you really want to continue?', validators=[
                               InputRequired()], choices=['no', 'yes'], default='no')
    submit = SubmitField("Confirm")

########################################################################################################################
# Recommendation related forms

# I will make the variable names the same for the first three forms, because then I an use the same Jinja format for all of them


class SweetnessRecommendationForm(FlaskForm):
    question_1 = IntegerField("Is milk chocolate more enjoyable for you, then dark chocolate?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_2 = IntegerField("How much do you prefer sweetness over bitterness in you cup?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_3 = IntegerField("Are dark roasts something you enjoy?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_4 = IntegerField("Do you prefer coffee blends (arabica mixed with robusta) over pure arabica?", validators=[
                              InputRequired(), NumberRange(-10, 10)])

    submit = SubmitField("Next Page")


class BodyRecommendationForm(FlaskForm):
    question_1 = IntegerField("Do you like full bodied coffee?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_2 = IntegerField("Do you have a preference for metal filters over paper filters.", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_3 = IntegerField("Would you rather have your tea without milk?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_4 = IntegerField("Does filtered coffee taste better for you than espresso?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    submit = SubmitField("Next Page")


class FlavorRecommendationForm(FlaskForm):
    question_1 = IntegerField("Do you like chocolate?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_2 = IntegerField("Would you rather put nutella on your toast then marmalade?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_3 = IntegerField("Would you prefer a fruity cake over a chocolate cake?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    question_4 = IntegerField("Are sour candies better then caramel?", validators=[
                              InputRequired(), NumberRange(-10, 10)])
    submit = SubmitField("Next Page")


class FlavorsRecommendationForm(FlaskForm):
    flavors = MultiCheckboxField("Which flavors do you enjoy?", coerce=str)
    submit = SubmitField("Send")
