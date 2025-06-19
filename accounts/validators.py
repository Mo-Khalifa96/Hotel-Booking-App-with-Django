import re
from datetime import date
from django.utils.translation import gettext_lazy
from django.core.exceptions import ValidationError

#Custom method to validate age 
def validate_age(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 18:
        raise ValidationError("User must be at least 18 years old to register.")


#Custom method to validate image size 
def validate_image_size(value): 
    filesize = value.size
    limit_mb = 5  # Maximum file size (5MB)
    if filesize > limit_mb * 1024 * 1024:
        raise ValidationError(f"Photo size should not exceed {limit_mb} MB.")


#Custom method to validate phone numbers 
def validate_phone_number(value):
    '''
    Custom validator for phone numbers.\n
    <br>
    Regex explanation: \n
    ^                 - Start of the string \n
    \\+?              - Optional leading plus sign (for international codes) \n 
    [\\d\\s\\-\\(\\)]+ - One or more digits, spaces, hyphens, or parentheses \n 
    \\$                - End of the string \n 
    <br>
    This regex allows for formats like: \n
    +123 456 7890 \n
    (123) 456-7890 \n
    123-456-7890 \n
    1234567890 \n
    +44 20 7946 0958 \n
    '''
    
    phone_regex = r"^\+?[\d\s\-\(\)]+$"

    if not re.fullmatch(phone_regex, value):
        raise ValidationError(
            gettext_lazy("Enter a valid phone number. Only digits, spaces, hyphens, parentheses, and an optional leading '+' are allowed."),
            code='invalid_phone_number')

    #check the total digits count (should be more than 7 digits)
    digits_only = re.sub(r'\D', '', value)
    if len(digits_only) < 7: 
        raise ValidationError(
            gettext_lazy("Phone number must contain at least 7 digits."),
            code='phone_number_too_short')
    