from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField, SelectField, BooleanField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, InputRequired, NumberRange, Length, Optional
from flask import current_app
import filetype

class GroupForm(FlaskForm):
    name = StringField("Group Name", validators=[DataRequired(), Length(min=1, max=120)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    max_capacity = IntegerField("Max Capacity (0 for unlimited)", default=0, validators=[NumberRange(min=0)])
    expiration_type = SelectField(
        "Link Expiration",
        choices=[
            ("never", "Never Expire"),
            ("hours", "Expire After Hours")
        ],
        validators=[DataRequired()]
    )
    expiration_hours = IntegerField("Hours Until Expiration", default=48, validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Create Group")

class InviteForm(FlaskForm):
    """Form for generating group links - no input fields needed as expiration is set at group level"""
    submit = SubmitField("Generate Link")


class IDForm(FlaskForm):
    image = FileField("Upload ")

    def __init__(self, allowed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image.validators = [
            FileRequired('File was empty!'),
            FileAllowed(allowed, "Only images are allowed!")
        ]
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    middle_name = StringField("Middle Name", validators=[Optional(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    eye_color = SelectField(
        "Eye Color",
        choices=[
            ("", "Select eye color"),
            ("brown", "Brown"),
            ("blue", "Blue"),
            ("green", "Green"),
            ("hazel", "Hazel"),
            ("gray", "Gray"),
            ("black", "Black")
        ],
        validators=[DataRequired()]
    )
    hair_color = SelectField(
        "Hair Color",
        choices=[
            ("", "Select hair color"),
            ("black", "Black"),
            ("brown", "Brown"),
            ("blonde", "Blonde"),
            ("red", "Red"),
            ("gray", "Gray"),
            ("white", "White")
        ],
        validators=[DataRequired()]
    )
    address = StringField("Address", validators=[Optional(), Length(max=200)])
    date_of_birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[DataRequired()])
    height = DecimalField("Height (in cm)", validators=[DataRequired(), NumberRange(min=0)])
    weight = DecimalField("Weight (in kg)", validators=[DataRequired(), NumberRange(min=0)])
    gender = SelectField(
        "Gender",
        choices=[("", "Select gender"), ("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[DataRequired()]
    )
    state = SelectField(
        "State",
        choices=[
            ("", "Select state"),
            ("AL", "Alabama"),
            ("AK", "Alaska"),
            ("AZ", "Arizona"),
            ("AR", "Arkansas"),
            ("CA", "California"),
            ("CO", "Colorado"),
            ("CT", "Connecticut"),
            ("DE", "Delaware"),
            ("FL", "Florida"),
            ("GA", "Georgia"),
            ("HI", "Hawaii"),
            ("ID", "Idaho"),
            ("IL", "Illinois"),
            ("IN", "Indiana"),
            ("IA", "Iowa"),
            ("KS", "Kansas"),
            ("KY", "Kentucky"),
            ("LA", "Louisiana"),
            ("ME", "Maine"),
            ("MD", "Maryland"),
            ("MA", "Massachusetts"),
            ("MI", "Michigan"),
            ("MN", "Minnesota"),
            ("MS", "Mississippi"),
            ("MO", "Missouri"),
            ("MT", "Montana"),
            ("NE", "Nebraska"),
            ("NV", "Nevada"),
            ("NH", "New Hampshire"),
            ("NJ", "New Jersey"),
            ("NM", "New Mexico"),
            ("NY", "New York"),
            ("NC", "North Carolina"),
            ("ND", "North Dakota"),
            ("OH", "Ohio"),
            ("OK", "Oklahoma"),
            ("OR", "Oregon"),
            ("PA", "Pennsylvania"),
            ("RI", "Rhode Island"),
            ("SC", "South Carolina"),
            ("SD", "South Dakota"),
            ("TN", "Tennessee"),
            ("TX", "Texas"),
            ("UT", "Utah"),
            ("VT", "Vermont"),
            ("VA", "Virginia"),
            ("WA", "Washington"),
            ("WV", "West Virginia"),
            ("WI", "Wisconsin"),
            ("WY", "Wyoming")
        ],
        validators=[DataRequired()]
    )
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    zip_code = StringField("Zip Code", validators=[DataRequired(), Length(max=10)])
    organ_donor = BooleanField("Organ Donor")
    restrictions_corrective_lenses = BooleanField("Restrictions (Corrective Lenses)")
    submit = SubmitField("Submit Application")


    def validate_image(self, image):
        data = image.data.read()
        kind = filetype.guess(data)
        image.data.seek(0)  # Reset file pointer after reading
        if kind is None or kind.extension not in current_app.config['UPLOAD_EXTENSIONS']:
            raise ValidationError("Invalid image format.")