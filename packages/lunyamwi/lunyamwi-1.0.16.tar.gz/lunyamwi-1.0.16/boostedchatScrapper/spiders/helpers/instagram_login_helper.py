import email
import imaplib
import logging
import os
import random
import re
import time
from pathlib import Path

from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice
from django_tenants.utils import schema_context
from api.scout.models import Scout,Device

logger = logging.getLogger()

def change_password_handler(username):
    # Simple way to generate a random string
    chars = list("abcdefghijklmnopqrstuvwxyz1234567890!&£@#")
    password = "".join(random.sample(chars, 8))
    return password


def get_code_from_email(username):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("CHALLENGE_EMAIL"), os.getenv("CHALLENGE_PASSWORD"))
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = payload.get_payload(decode=True).decode()
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
    return False


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False


@schema_context(os.getenv("SCHEMA_NAME"))
def login_user(scout: Scout):

    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    
    cl = Client()
    
    device = Device.objects.filter(scout=scout).latest('created_at')
    scout = Scout.objects.get(id=device.scout_id)
    if device.status==0 or device.status == 1: 
        cl.set_device(device={
                "app_version": device.app_version,
                "android_version": device.android_version,
                "android_release": device.android_release,
                "dpi": device.dpi,
                "resolution": device.resolution,
                "manufacturer": device.manufacturer,
                "device": device.device,
                "model": device.model,
                "cpu": device.cpu,
                "version_code": device.version_code,
            },reset=True)
        cl.set_user_agent(f"Instagram {device.app_version} Android ({device.android_version}/{device.android_release}; {device.dpi}; {device.resolution}; {device.manufacturer}; {device.device}; {device.model}; {device.cpu}; en_US; {device.version_code})",reset=True)
        cl.set_country(scout.country)
        cl.set_country_code(scout.code)

        
    # cl.login_by_sessionid()
    # index = 1
    # before_ip = cl._send_public_request("https://api.ipify.org/")
    
    username = f"user-{os.getenv('PROXY_USERNAME').strip()}-country-{str.lower(scout.country)}-city-{str.lower(scout.city)}"
    password = os.getenv('PROXY_PASSWORD').strip()
    proxy = None
    
    proxy = f"http://{username}:{password}@gate.smartproxy.com:10001"

    
    cl.set_proxy(
        proxy
    )
    # after_ip = cl._send_public_request("https://api.ipify.org/")
    # print(f"Before: {before_ip}")
    # print(f"After: {after_ip}")
    # cl.challenge_code_handler = challenge_code_handler(scout.username, 1)
    cl.delay_range = [5, 8]
    max_attempts = 2
    session_file_path = Path(f"{scout.username}.json")
    if os.path.exists(session_file_path):
        for attempt in range(1, max_attempts + 1):
            session = cl.load_settings(session_file_path)
            if session:
                cl.set_settings(session)
                try:
                    cl.get_timeline_feed()  # Check if the session is valid
                    print("Session is valid, login with session")

                    break
                except Exception as e:
                    old_session = cl.get_settings()
                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])
                    print(f"Session is invalid (attempt {attempt}): {e}")
                    if attempt < max_attempts:
                        print(f"Waiting 1 minute before trying again (attempt {attempt})")
                        time.sleep(60)  # Wait for 1 minute
                    else:
                        print("All attempts failed, removing session file and logging in with username and password")
                        os.remove(session_file_path)
                        cl.login(username=scout.username,password=scout.password)
                        cl.dump_settings(session_file_path)
                        device.status = 1
                        device.save()
                        print("Session saved to file")
    else:
        cl.login(username=scout.username,password=scout.password)
        print("Login with username and password")
        cl.dump_settings(session_file_path)
        device.status = 1
        device.save()
        print("Session saved to file")
    return cl
