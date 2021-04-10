import imaplib
import quopri
from email.parser import Parser
from settings import *
import email
import base64
import os
import re
# def download_mail_attachment(msg):
#     if msg==None:
#         return None
#     for part in msg.walk():
#         if part.get_content_disposition()=='attachment':
#             filename=part.get_filename()
#             l=filename.split('\r\n')
#             encodingList=[]
#             nameList=[]
#             quote_printable=[]
#             for i in range(len(l)):
#                 if '?B?' in l[i]:
#                     print(l[i].split('?B?'))
#                     tmp1,tmp2=l[i].split('?B?')
#                     qp=False
#                 elif '?Q?' in l[i]:
#                     print(l[i].split('?Q?'))
#                     tmp1,tmp2=l[i].split('?Q?')
#                     qp=True
#                 else:
#                     print('error!')
#                     sys.exit()
#                 tmp1=tmp1.split('?')[1]
#                 encodingList.append(tmp1)
#                 nameList.append(tmp2)
#                 quote_printable.append(qp)
#             name=''
#             print(encodingList,nameList)
#             for i in range(len(encodingList)):
#                 encoding=encodingList[i]
#                 name_b64=nameList[i]
#                 if not quote_printable[i]:
#                     string=base64.decodebytes(name_b64.encode()).decode(encoding)
#                 else:
#                     string=quopri.decodestring(name_b64.encode()).decode(encoding)
#                 name=name + string
#             if name[-1]=='?':
#                 name=name[:-1]
#             print(name)
#             with open('./saves/'+name,'ab') as f:
#                 f.write(base64.decodebytes(part.get_payload().encode()))
def decode(string):
    if '?B?' in string:
        tmp1,tmp2=string.split('?B?')
        qp=False
    elif '?b?' in string:
        tmp1,tmp2=string.split('?b?')
        qp=False
    elif '?Q?' in string:
        tmp1,tmp2=string.split('?Q?')
        qp=True
    else:
        print('no need of decoding:',string)
        return string
    encoding=tmp1.split('?')[1]
    info=tmp2
    if not qp:
        s=base64.decodebytes(info.encode()).decode(encoding)
    else:
        s=quopri.decodestring(info.encode()).decode(encoding)
    if s[-1]=='?':
        s=s[:-1]
    return s
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type','').lower()
        pos = content_type.find('charset=')
        if pos>=0:
            charset=content_type[pos+8:].strip()[1:-1]
    return charset
def get_content(msg):
    content=''
    for part in msg.walk():
        content_type = part.get_content_type()
        charset = guess_charset(part)
        if content_type=='text/plain':
            content=part.get_payload(decode=True).decode(charset).strip()
            break
        elif content_type=='text/html':
            content=part.get_payload(decode=True).decode(charset)
            res = re.search('<p>(.*?)</p>',content)
            if not res:
                print('error while parsing html.')
                content=''
            content=res.group(1)
            break
    return content

def login():
    conn = imaplib.IMAP4_SSL("imaphz.qiye.163.com", 993)
    conn.login(email,password)
    INBOX = conn.select("INBOX")
    type, data = conn.search(None, 'ALL')
    msgList = data[0].split()
    for i in msgList[::-1]:
        type, datas = conn.fetch(i,'(RFC822)')
        try:
            contents=datas[0][1].decode('utf-8')
        except UnicodeDecodeError as e:
            print('An exception raised during Unicode decoding:',e)
            continue
        res=contents.find('Subject: ')
        if not res>=0:
            print('No title was found in the mail.')
            continue
        res=contents[res+9:].split('\r\n')[0].strip()
        subject=decode(res)
        if subject!='运动会报名':
            print('mail title:',subject,'do not match.')
            continue
        print('matched.')
        msg = Parser().parsestr(contents)
        result = get_content(msg)
        if not result:
            print('result is null.')
            continue
        with open(filename,'a',encoding='utf-8') as f:
            f.write(','.join(re.split('[,+]',result))+'\n')
            print(result,'is added to',filename,'.')
if __name__=='__main__':
    login()