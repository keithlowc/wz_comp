from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string


class EmailNotificationSystem:
    def __init__(self):
        self.from_email = 'noreply@duelout.com'

    def send_competition_email(self, check_in_url, subject, competition_name, email_list):
        '''
        This function sends an email notification
        to the current email list and should
        re route the user to the checkin page 
        confirmation on duelout.com
        
        '''
        from_email = 'noreply@duelout.com'

        email_sent = False

        try:
            print('--------> SENDING EMAIL!')
            html_content = render_to_string('email/check_in_email.html', {
                                                'competition_name': competition_name,
                                                'competition_check_in_url': check_in_url,
                                            })

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        from_email,
                        email_list)

            email.attach_alternative(html_content, 'text/html')
            email.send()

            email_sent = True
        except Exception as e:
            print('--------> NOT SENDING! EMAIL')

        return email_sent


    def send_mail_text(self, subject, body, recipient):
        '''
        Send mail with only text
        '''

        try:
            send_mail(subject, body, self.from_email, recipient)
        except Exception as e:
            print('--------> There was an error - Unable to send email')
    

    def send_mass_email_to_teams(self, data_tuple):
        '''
        Send mass email. Each recipient
        gets one email and it seems to be
        more efficient than send_mail
        '''

        try:
            send_mass_mail(data_tuple)
        except Exception as e:
            print('--------> There was an error - Unable to send mass email {}'.format(e))
