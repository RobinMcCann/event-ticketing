from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, Email, EqualTo, NumberRange, Regexp

from app import bcrypt
from app.utils.models import AppUser
from app.utils.utils import get_concerts, format_concert_option

import os

MAX_TICKETS_PER_ORDER = os.getenv('MAX_TICKETS_PER_ORDER')

class RegisterForm(FlaskForm):
    
    first_name = StringField(validators=[InputRequired("Ange ditt förnamn.")],
                             render_kw={'placeholder' : 'Förnamn'})
    
    last_name = StringField(validators=[InputRequired("Ange ditt efternamn.")],
                            render_kw={'placeholder' : 'Efternamn'})

    email = EmailField(validators=[InputRequired("Ange din epost-address."), Email("Epost-addressen är inte giltig.")],
                       render_kw={'placeholder' : 'Epost-address'})
    
    username = StringField(validators=[InputRequired("Välj ett användarnamn."), 
                                       Length(min=4, max=20)],
                           render_kw={'placeholder' : 'Användarnamn'})

    password = PasswordField(validators=[InputRequired("Välj ett lösenord."), 
                                         Length(min=4, max=20)],
                             render_kw={'placeholder' : 'Lösenord'})

    password2 = PasswordField(validators=[InputRequired("Ange lösenordet igen."), 
                                          EqualTo('password', message="Lösenorden överensstämmer inte!"), 
                                          Length(min=4, max=20)],
                              render_kw={'placeholder' : 'Lösenord igen'})

    submit = SubmitField('Skapa användare')

    def validate_username(self, username):
        username_exists = AppUser.query.filter_by(username=username.data).first()

        if username_exists or username.data == "admin":
            raise ValidationError("Användarnamnet är taget redan. Välj ett annat.")


class LoginForm(FlaskForm):
        
    username = StringField(validators=[InputRequired("Ange ditt användarnamn."), 
                                       Length(min=4, max=20)],
                           render_kw={'placeholder' : 'Användarnamn'})

    password = PasswordField(validators=[InputRequired("Ange ditt lösenord."), 
                                         Length(min=4, max=20)],
                             render_kw={'placeholder' : 'Lösenord'})

    submit = SubmitField('Logga in')

class TicketForm(FlaskForm):

    buyername = StringField(validators=[InputRequired("Ange beställarens namn."),
                                        Length(min=4, max=80)],
                            render_kw={'placeholder' : 'Beställarens namn'})

    concerts = get_concerts()
    concert_names = [("", "Välj konsert")] + [(concert['Namn'], format_concert_option(concert)) for concert in concerts]

    concert = SelectField(choices = concert_names,
                          default = "Välj konsert",
                          validators=[InputRequired("Välj en konsert")])

    number_of_tickets = StringField(validators=[InputRequired(f"Ange hur många biljetter beställaren vill ha (max {MAX_TICKETS_PER_ORDER})."),
                                                Regexp(r'^\d+$', message="Fyll i en giltig siffra.")],
                                    render_kw={'placeholder' : f'Välj antal biljetter (1-{MAX_TICKETS_PER_ORDER})'})

    def validate_number_of_tickets(self, n):
        try:
            n = int(n.data)
            if not (1 <= n <= 8):
                raise ValidationError(f"Du kan beställa 1-{MAX_TICKETS_PER_ORDER} biljetter åt gången.")
        except (ValueError, TypeError):
            raise ValidationError("Fyll i en giltig siffra.")

    submit = SubmitField("Skapa biljettlänk")


class ClaimTicketForm(FlaskForm):

    claim = SubmitField("Använd biljett.")

class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(validators=[InputRequired("Ange ditt nuvarande lösenord."), 
                                                 Length(min=4, max=20)],
                                     render_kw={'placeholder' : 'Ditt nuvarande lösenord'})

    new_password = PasswordField(validators=[InputRequired("Ange ett nytt lösenord."), 
                                             Length(min=4, max=20)],
                                 render_kw={'placeholder' : 'Ange ett nytt lösenord'})

    new_password2 = PasswordField(validators=[InputRequired("Ange ett nytt lösenord."), 
                                              EqualTo('new_password', message="Lösenorden överensstämmer inte!"),
                                              Length(min=4, max=20)],
                                  render_kw={'placeholder' : 'Ange ditt nya lösenord igen'})

    def validate_current_password(self, pw):
        if not bcrypt.check_password_hash(current_user.password_hash, pw.data):
            raise ValidationError("Fel lösenord.")

    submit = SubmitField("Byt lösenord")                              