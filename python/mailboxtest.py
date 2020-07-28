# Try and Tell with the Docs
# https://docs.python.org/3/library/mailbox.html

#%%
mbox_location = 'Junk Email.mbox/mbox'
#%%
'''
an mbox is a an iterable dictionary of messages
all messages are loaded into memory
processing of larger mboxes will take longer to process
** creates new mbox if one does not exist
'''
#%%
import mailbox
mbox = mailbox.mbox(mbox_location)
#%%
'''
Need to use ByteParser factory for some of the methods in the documentation to work.
https://stackoverflow.com/a/52484584
'''
#%%
# from email import policy
# from email.parser import BytesParser

# mbox = mailbox.mbox(mbox_location, factory=BytesParser(policy=policy.default).parse)
#%%
'''
get number of messages in the mailbox
'''
#%%
print(mbox.__len__())
#%%
'''
messages have a string representation
which dumps all metadata, headers and body
'''
#%%
print(mbox[0])
#%%
print(mbox[0].__str__())
#%%
'''
messages have keys to represent the metadata of the message
'''
#%%
print(mbox[1].keys())
#%%
'''metadata has a string representation or use the get() method'''
#%%
print('From: ', mbox[0].get('From'))
print('From: ', mbox[0]['From'])
print('To: ', mbox[0]['To'])
print('Subject: ', mbox[0]['Subject'])
print('Date: ', mbox[0]['Date'])
print('Message-ID: ', mbox[0]['Message-ID'])
print('Content-Type: ', mbox[0]['Content-Type'])
#%%
'''
you can loop through all messages
'''
#%%
for msg in mbox:
    print(msg['from'])
    break
#%%
'''
or loop with iterkeys
'''
#%%
for key in mbox.iterkeys():
    print(key, mbox[key]['from'])
    break
#%%
'''
you can delete a message
'''
#%%
mbox.discard(0)
#%%
'''
use with flush() to write changes back to disk
but CAUTION that you can't undo this
'''
#%%
mbox.flush()
#%%
'''
A Counter object can help with searching
Chris Riederer has an idea for some interesting things
http://www.relevantmisc.com/scraping/2020/01/29/processing-mbox/
'''
#%%
from collections import Counter
c = Counter(m["from"] for m in mbox)
# print(c.most_common(10))
for email_from, count in c.most_common(10):
    print(email_from, ': ', count)
#%%
'''
# use walk() to iterate over the parts (content) of a message
# loop over all messages with walk() or just iterate message.get_payload(),
'''
#%%
for message in mbox:
    for part in message.walk():
        print(part.get_content_type())
#%%
'''
or get one message
if the content is multipart the payload will be a list of
[<email.message.Message object at 0x105aab0a0>, <email.message.Message object at 0x105aab2e0>]
and you can use get_content_type() again to get a specific rendering
or concatenate them together as in this example
if the content is not multipart it is expected to be a string.
https://stackoverflow.com/a/26567942
'''
#%%
message = mbox[6]
if message.is_multipart():
    # only get the plaintext content
    for part in message.get_payload():
        if part.get_content_type() == 'text/plain':
            content = part.get_payload()
        else:
            pass
        # print(part.get_payload(decode=True).decode())
    # something is off with the documentation about the decode parameter
    # without decode() returns bytestring
    # content = ''.join(part.get_payload(decode=True).decode() for part in message.get_payload())
else:
    # if this causes error too, add decode()
    content = message.get_payload(decode=True)

# print(content)

# could do something like this while looping all words in search list
if 'table' in content:
    print('table')

# print(content.split())
from collections import Counter
c = Counter(content.split())
# print(c.most_common(10))
print(c)
# for email_from, count in c.most_common(10):
#     print(email_from, ': ', count)
#%%
'''
Scan all messages
'''
#%%
content = ''
key = -1
for message in mbox:
    key += 1
    if message.is_multipart():
        # only get the plaintext content
        for part in message.get_payload():
            if part.get_content_type() == 'text/plain':
                content += part.get_payload()
            else:
                # multipart/mixed
                print(key, 'multi:', message.get_content_type())
                pass
            # print(part.get_payload(decode=True).decode())
        # something is off with the documentation about the decode parameter
        # without decode() returns bytestring
        # content = ''.join(part.get_payload(decode=True).decode() for part in message.get_payload())
    else:
        # text/plain
        print(key, message.get_content_type())
        # if this causes error too, add decode()
        content += message.get_payload(decode=True).decode()

    # could do something like this while looping all words in search list
    if 'table' in content:
        print(key, 'table')
        

# print(content.split())
from collections import Counter
c = Counter(content.split())
print(c.most_common(10))
# print(c)
# for email_from, count in c.most_common(10):
#     print(email_from, ': ', count)
#%%
'''
Get a string with both plaintext and html parts
This is the example from https://stackoverflow.com/a/26567942
But the decode parameter doesn't work so add decode()
'''
#%%
message = mbox[0]
if message.is_multipart():
    content = ''.join(part.get_payload(decode=True).decode() for part in message.get_payload())
else:
    content = message.get_payload(decode=True)

# print(content)
#%%
'''
html will be multipart/alternative
and have two parts, text/plain and text/html

what about attachments?
here's an example, https://www.thepythoncode.com/article/reading-emails-in-python
'''
#%%
message = mbox[0]
parts = message.get_payload()
print(parts[0].get_content_type())
#%%
'''
Loop through all messages looking for a specific word in the subject
https://docs.python.org/3.7/library/mailbox.html#examples
'''
#%%
for message in mailbox.mbox('~/mbox'):
    subject = message['subject']       # Could possibly be None.
    if subject and 'python' in subject.lower():
        print(subject)
#%%
'''
Another example from the docs showing moving messages to different boxes
based on a list name.
https://docs.python.org/3.7/library/mailbox.html#examples
You could also use this approach to move suspected spam messages 
to a different mailbox
'''
#%%
list_names = ('python-list', 'python-dev', 'python-bugs')

boxes = {name: mailbox.mbox('~/email/%s' % name) for name in list_names}
inbox = mailbox.Maildir('~/Maildir', factory=None)

for key in inbox.iterkeys():
    try:
        message = inbox[key]
    except email.errors.MessageParseError:
        continue                # The message is malformed. Just leave it.

    for name in list_names:
        list_id = message['list-id']
        if list_id and name in list_id:
            # Get mailbox to use
            box = boxes[name]

            # Write copy to disk before removing original.
            # If there's a crash, you might duplicate a message, but
            # that's better than losing a message completely.
            box.lock()
            box.add(message)
            box.flush()
            box.unlock()

            # Remove original message
            inbox.lock()
            inbox.discard(key)
            inbox.flush()
            inbox.unlock()
            break               # Found destination, so stop looking.

for box in boxes.itervalues():
    box.close()

# %%
