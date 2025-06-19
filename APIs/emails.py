from djoser import email

#Customize djoser's emails
class CustomPasswordResetEmail(email.PasswordResetEmail):
    template_name = "emails/password_reset_token_email.html"

class CustomPasswordChangedConfirmationEmail(email.PasswordChangedConfirmationEmail):
    template_name = "emails/reset_successful_email.html"
