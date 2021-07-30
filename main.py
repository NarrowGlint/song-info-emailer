import imaplib
import email
from email.header import decode_header

import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import smtplib
from email.message import EmailMessage
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def program():
    obj = imaplib.IMAP4_SSL('imap.gmail.com', '993')  # Connect to an IMAP4 sever over SSL, port 993
    obj.login('EMAIL HERE','PASSWORD HERE')  # Identify the client user and password
    obj.select()  # Select a the 'INBOX' mailbox (default parameter)
    # Search mailbox no (None) charset, criterion:"UnSeen". Will return a tuple, grab the second part,
    # split each string into a list, and return the length of that list:
    number_of_emails = (len(obj.search(None,'UnSeen')[1][0].split()))
    print(number_of_emails)

    obj.close()
    obj.logout()

    if number_of_emails >= 1:
        print('New Emails!')
        #Account Information

        username = "songreplier@gmail.com"
        password = "ireplytosongs"

        def clean(text):
            #clean textd for creating a folder
            return "".join(c if c.isalnum() else "_" for c in text)

        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login(username, password)

        status, messages = imap.select("INBOX")
        # number of top emails to fetch
        N = 1
        # total number of emails
        messages = int(messages[0])

        for i in range(messages, messages-N, -1):
            # fetch the email message by ID
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)
                    print("Subject:", subject)
                    print("From:", From)
                    # if the email message is multipart
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                print(body)
                            else:
                                pass
        # close the connection and logout
        imap.close()
        imap.logout()


        start = '<div dir="ltr">'
        end = '<br></div>'

        #tempName = body.replace('Sent from my iPhone', '')
        songName = re.sub('<[^<]+?>', '', body)#tempName#[body.find(start)+len(start):body.rfind(end)]
        print(songName)


        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome("./chromedriver")
            driver.get('https://genius.com/')
            time.sleep(5)
            search_bar = driver.find_element_by_name("q")
            search_bar.clear()
            search_bar.send_keys(songName)
            search_bar.send_keys(Keys.RETURN)
        except:
            pass
        time.sleep(5)
        try:
            firstTrack = driver.find_element_by_xpath('/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[2]/search-result-section/div/div[2]/search-result-items/div[1]/search-result-item/div/mini-song-card/a/div[2]/div[1]/div[1]')
            firstTrack.click()
        except NoSuchElementException:
            pass
        time.sleep(5)
        email_address = 'songreplier@gmail.com'  # os.environ.get('EMAIL_USER')
        email_password = 'ireplytosongs'  # os.environ.get('EMAIL_PASS')
        try:
            driver.find_element_by_xpath('//*[@id="application"]/main/div[1]/div[3]/a/span').click()  #FIND FIRST SONG
            email_address = 'EMAIL HERE'   #os.environ.get('EMAIL_USER')
            email_password = 'PASSWORD HERE' #os.environ.get('EMAIL_PASS')
        except NoSuchElementException:
            print('HAHA U GOT A NoSuchElementException')

        try:
            time.sleep(5)
            about_text = driver.find_element_by_xpath('//*[@id="application"]/main/div[3]/div[3]/div[1]/div[2]/div[1]/div').text
            print(about_text)

            thing = re.search('<(.*)>', From)
            originalEmail = thing.group(1)
            print(originalEmail)

            msg = EmailMessage()
            msg['Subject'] = ''
            msg['From'] = email_address
            msg['To'] = originalEmail
            msg.set_content(about_text)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_address, email_password)
                smtp.send_message(msg)
        except NoSuchElementException:
            lyrics = driver.find_element_by_xpath('//*[@id="annotation-portal-target"]/div/div[1]').text
            print(lyrics)
            thing = re.search('<(.*)>', From)
            originalEmail = thing.group(1)
            print(originalEmail)

            final_lyrics = 'Since there was no info about your song on Genius, hear are the lyrics: \n' + lyrics
            msg = EmailMessage()
            msg['Subject'] = ''
            msg['From'] = email_address
            msg['To'] = originalEmail
            msg.set_content(final_lyrics)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_address, email_password)
                smtp.send_message(msg)
        else:
            pass

        time.sleep(10)
        driver.quit()
        program()
    else:
        print('No New Emails')
        time.sleep(10)
        program()

program()
