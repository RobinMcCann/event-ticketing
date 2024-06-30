from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email, EqualTo

from app.utils.models import AppUser


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

    password2 = PasswordField(validators=[InputRequired("Ange lösenordet igen."), EqualTo('password', message="Lösenorden överensstämmer inte!"), 
                                         Length(min=4, max=20)],
                             render_kw={'placeholder' : 'Lösenord igen'})

    submit = SubmitField('Skapa användare')

    def validate_username(self, username):
        username_exists = AppUser.query.filter_by(username=username.data).first()

        if username_exists:
            raise ValidationError("Användarnamnet är taget redan. Välj ett annat.")


class LoginForm(FlaskForm):
        
    username = StringField(validators=[InputRequired("Ange ditt användarnamn."), 
                                       Length(min=4, max=20)],
                           render_kw={'placeholder' : 'Användarnamn'})

    password = PasswordField(validators=[InputRequired("Ange ditt lösenord."), 
                                         Length(min=4, max=20)],
                             render_kw={'placeholder' : 'Lösenord'})

    submit = SubmitField('Logga in')