#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import mimetypes
from smtplib import SMTP
import datetime
import os


class Email:
    """
    Performs email-related activities
    """
    def __init__(self, un, pw, log):
        """Connect to account"""
        self.un = un
        self.pw = pw
        self.log = log
        self.smtpserver = SMTP('smtp.gmail.com', 587)
        self.imapserver = imaplib.IMAP4_SSL('imap.gmail.com', imaplib.IMAP4_SSL_PORT)

    def connect_for_sending(self):
        """Connect to the SMTP server for sending emails"""
        self.smtpserver.ehlo()
        self.smtpserver.starttls()
        self.smtpserver.login(self.un, self.pw)
        self.log.debug('Connected with email server.')

    def connect_for_reading(self):
        """Connect to the IMAP server to read emails"""
        self.imapserver.login(self.un, self.pw)

    def search(self, label='inbox', mail_filter='ALL'):
        """Get email objects based on a filter"""
        self.connect_for_reading()
        self.imapserver.select(label)
        mail_status, mail_data = self.imapserver.uid('search', None, mail_filter)
        # Convert list of ids from bytes to string, then split
        mail_ids = mail_data[0].decode('utf8').split(' ')
        # Get most recent message and check the date
        mail_id = mail_ids[-1]
        email_status, email_data = self.imapserver.uid('fetch', mail_id, "(RFC822)")
        raw_email = email_data[0][1]
        # Parse email from bytes into EmailMessage object for easy data extraction
        emailobj = email.message_from_bytes(raw_email)
        # Check if data of email object was today
        emaildate = datetime.datetime.strptime(emailobj['Date'][:-6], '%a, %d %b %Y %H:%M:%S')
        today = datetime.datetime.now()
        if emaildate.timestamp() > today.timestamp():
            # Email is current. Return elements
            return emailobj

    def forward(self, email_to, email_object):
        """Command to forward an email"""
        email_object.replace_header('From', self.un)
        email_object.replace_header('To', email_to)
        self.log.debug('Communicating with server.')
        try:
            self.connect_for_sending()
            self.smtpserver.sendmail(self.un, email_to, email_object.as_string())
            self.log.debug('Message sent.')
            self.smtpserver.quit()
        except TimeoutError:
            self.log.exception('Connection with server timed out.')
        except:
            self.log.exception('Could not connect with email server.')

    def send(self, email_to, subject, body, attachment_paths=[]):
        """Command to package and send email"""
        self.log.debug('Beginning email process.')
        msg = MIMEMultipart()
        msg["From"] = self.un
        msg["To"] = ', '.join([email_to])
        msg["Subject"] = subject
        msg.preamble = body
        if len(attachment_paths) > 0:
            self.log.debug('Encoding any attachments')
            for attachment_path in attachment_paths:
                ctype, encoding = mimetypes.guess_type(attachment_path)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                if maintype == 'text':
                    with open(attachment_path) as f:
                        attachment = MIMEText(f.read(), _subtype=subtype)
                else:
                    with open(attachment_path) as f:
                        attachment = MIMEBase(maintype, subtype)
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        self.log.debug('Communicating with server.')
        try:
            self.connect_for_sending()
            self.smtpserver.sendmail(self.un, email_to, msg.as_string())
            self.log.debug('Message sent.')
            self.smtpserver.quit()
        except TimeoutError:
            self.log.exception('Connection with server timed out.')
        except:
            self.log.exception('Could not connect with email server.')


class PBullet:
    """
    Connects to Pushbullet API
    Args for __init__:
        api: str, Pushbullet API key
    """
    def __init__(self, api):
        self.pushbullet = __import__('pushbullet')

        self.api = api
        self.pb = self.pushbullet.PushBullet(self.api)

    def send_message(self, title, message):
        """Sends a message"""
        self.pb.push_note(title, message)

    def send_address(self, title, address):
        """Sends an address"""
        self.pb.push_address(title, address)

    def send_link(self, text, link):
        """Sends a link"""
        self.pb.push_link(text, link)

    def send_img(self, filepath, title, filetype='image/png'):
        """Sends an image"""
        with open(filepath, 'rb') as thing:
            file_data = self.pb.upload_file(thing, title, file_type=filetype)
        push = self.pb.push_file(**file_data)


class TWAPI:
    def __init__(self):
        self.API = __import__('tweepy').API


class Twitter(TWAPI):
    def __init__(self, key_dict):
        self.twp = __import__('tweepy')
        # Import keys
        self.CONSUMER_KEY = key_dict['consumer_key']
        self.CONSUMER_SECRET = key_dict['consumer_secret']
        self.ACCESS_KEY = key_dict['access_key']
        self.ACCESS_SECRET = key_dict['access_secret']
        auth = self.twp.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        auth.set_access_token(self.ACCESS_KEY, self.ACCESS_SECRET)
        super(Twitter, self).__init__(auth)

    def get_messages(self):
        msgs = self.direct_messages()
        return msgs

    def get_followers(self):
        followers = self.followers()
        return followers

    def post(self, text, log=None, char_limit=140):
        if text != "":
            if len(text) > char_limit:
                text = text[:char_limit]
            try:
                self.update_status(status=text)
            except:
                if log is not None:
                    log.exception('Failed to post tweet.')
                else:
                    raise ValueError('Tweet failed to post!')
                    pass

    def send_message(self, user_id, text):
        if text != "":
            self.send_direct_message(user_id=user_id, text=text)

    def delete_tweet(self, datetime_lim, containing=""):
        timeline = self.twp.Cursor(self.user_timeline).items()
        for tweet in timeline:
            if tweet.created_at < datetime_lim:
                if containing != "":
                    if containing in tweet.text:
                        print("Destroying {}\n{}".format(tweet.id, tweet.text))
                        self.destroy_status(tweet.id)
                else:
                    print("Destroying {}\n{}".format(tweet.id, tweet.text))
                    self.destroy_status(tweet.id)

