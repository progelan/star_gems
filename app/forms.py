from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, FloatField,\
    FieldList, FormField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Optional, Length, Regexp
from app.models import User, Preference, TypeGem, Requirement
from app.routes import current_user
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from markupsafe import Markup


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])# встроенный валидатор
    character = SelectField('Character', choices=[('elf', 'Elf'), ('gnome', 'Gnome'), ('master', 'Master Gnome')])# (db, view)
    confirmpass = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, original_username, original_email):
        super(EditProfileForm, self).__init__()
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username already in use')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Email already registered')


class EditPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpass = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Save')


class ActionById(FlaskForm):
    value = HiddenField()


class RemoveProfileForm(FlaskForm):
    submit_remove = SubmitField('Delete profile')


class RestoreProfileForm(FlaskForm):
    submit_restore = SubmitField('Restore profile')


class AddGemsForm(FlaskForm):
    type_gem = QuerySelectField(label='Type gem',
                                query_factory=lambda: TypeGem.query,
                                get_label=lambda gem: gem.type,
                                allow_blank=True,
                                validators=[DataRequired()])
    amount_gem = IntegerField('Amount', validators=[NumberRange(min=1, max=10)])
    submit = SubmitField('Add gems')


class EditPrefForm(FlaskForm):
    pref = QuerySelectField(query_factory=lambda: Preference.query.filter_by(elf_id=current_user.id),
                            get_label='gem_type',
                            allow_blank=True,
                            blank_text='Select preference',
                            validators=[DataRequired()])
    gem_rate = FloatField('Rate', validators=[DataRequired(), NumberRange(min=0, max=1)])
    submit_edit = SubmitField('Save')


class AddPrefForm(FlaskForm):
    gem_type = SelectField(choices=[])
    gem_rate = FloatField(validators=[DataRequired(), NumberRange(min=0, max=1)])
    submit_value = Markup('<span class="fas fa-plus" title="Add preference"></span>')
    submit_add = SubmitField(submit_value)


class ViewQueryForm(FlaskForm):
    submit_value = Markup('<span class="fa fa-eye" title="View"></span>')
    submit = SubmitField(submit_value)
    input_field = TextField()


class DistributionForm(FlaskForm):
    elf = QuerySelectField(query_factory=lambda: User.query.filter(User.character == 'elf'),
                            get_label='name',
                            allow_blank=True,
                            validators=[DataRequired()],
                            blank_text=('Select elf'))
    value = HiddenField()
    submit_distrib = SubmitField('Distribution')
    submit_confirm = SubmitField('Confirm Distribution')


class RequirementsForm(FlaskForm):
    req_type = QuerySelectField(label='Type requirement',
                            query_factory=lambda: Requirement.query,
                            get_label='req_type',
                            allow_blank=True,
                            blank_text=('Select requirement'),
                            validators=[DataRequired()])
    req_rate = FloatField(label='Rate', validators=[DataRequired(), NumberRange(min=0, max=1)])
    submit_edit = SubmitField('Save')


class AddTypeForm(FlaskForm):
    gem_type = TextField(validators=[DataRequired(), Length(min=3, max=18), Regexp('^[a-zA-Z]+$', message='enter only latin letter')])
    submit_value = Markup('<span class="fas fa-plus" title="Add type"></span>')
    submit_add = SubmitField(submit_value)

    def validate_gem_type(self, gem_type):
        new_type = TypeGem.query.filter_by(type=gem_type.data).first()
        if new_type is not None:
            raise ValidationError('Gem type already in use')


class GemTypesForm(FlaskForm):
    gem_type = QuerySelectField(label='Gem type',
                                query_factory=lambda: TypeGem.query,
                                get_label= 'type',
                                allow_blank=True,
                                blank_text=('Select type gem'),
                                validators=[DataRequired()])
    edit_type = TextField(label='Rename',
                         validators=[DataRequired(),
                                    Length(min=3, max=18),
                                    Regexp('^[a-zA-Z]+$',
                                    message='enter only latin letter')])
    submit_type = SubmitField('Save')

    def validate_edit_type(self, edit_type):
        new_type = TypeGem.query.filter_by(type=edit_type.data).first()
        if new_type is not None:
            raise ValidationError('Gem type already in use')
