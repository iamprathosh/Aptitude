from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, RadioField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ImageUploadForm(FlaskForm):
    question_image = FileField('Question Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    options_image = FileField('Options Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    is_diagram = BooleanField('This is a diagrammatic question (show image if OCR fails)')
    answer_type = SelectField('Answer Type', choices=[
        ('option', 'Multiple Choice'), 
        ('text', 'Text Input')
    ], default='option')
    submit = SubmitField('Process Images')

class ManualQuestionForm(FlaskForm):
    question_text = TextAreaField('Question Text', validators=[Optional()])
    question_image = FileField('Question Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    is_diagram = BooleanField('This is a diagrammatic question (show image)')
    answer_type = SelectField('Answer Type', choices=[
        ('option', 'Multiple Choice'), 
        ('text', 'Text Input')
    ], default='option')
    submit = SubmitField('Create Question')

class VoteForm(FlaskForm):
    option = RadioField('Select an option', validators=[Optional()], coerce=int)
    text_answer = TextAreaField('Your Answer', validators=[Optional()])
    submit = SubmitField('Submit Vote')
