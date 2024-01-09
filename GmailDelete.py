import time
import base64
import tkinter as tk;
from Google import create_service

CLIENT_FILE = 'client-secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

Key_Words_Delet = ["unsubscribe", "college", "alerts", "university"];
Key_Words_Keep = ["champlain", "drexel", "pitt", "rochester"];

gmail_service = create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)
def CreateWindow():
  window = tk.Tk()
  return window;

def CreateButton(window):
  button = tk.Button(window)
  button.pack()
  return window
window = CreateWindow();
window=CreateButton(window)
window.mainloop()
# step 1. Serach emails
def search_emails(query, labels=None):
  # email_messages = []
  next_page_token = None

  message_response = gmail_service.users().messages().list(
      userId='me',
      labelIds=labels,
      includeSpamTrash=False,
      q=query,
      maxResults=500).execute()
  email_messages = message_response.get('messages')
  next_page_token = message_response.get('nextPageToken')

  while next_page_token:
    message_response = gmail_service.users().messages().list(
        userId='me',
        labelIds=labels,
        q=query,
        maxResults=500,
        includeSpamTrash=False,
        pageToken=next_page_token).execute()
    email_messages.extend(message_response['messages'])
    next_page_token = message_response.get('nextPageToken')
    #print('Page Token: {0}'.format(next_page_token))
    time.sleep(0.5)
    
  return email_messages

def DeleteOld():
  query = "before:2022/10/20"
  email_result= search_emails(query);
  for email_result in email_results:
    gmail_service.users().messages().trash(userId='me',
                                          id=email_result['id']).execute()
def CheckPart(part, email_result):
  value=0;
  if "body" in part:
   if "data" in part["body"]:
    value += CheckData(part['body']["data"], email_result)
   elif "parts" in part:
      for item in part["parts"]:
       value += CheckPart(item, email_result)
  elif "data" in part["payload"]["body"]:
    value += CheckData(part["payload"]["body"]["data"], email_result);
  elif "parts" in part["payload"]:
    
    for item in part["payload"]["parts"]:
      value += CheckPart(item, email_result)
      if value>=1:
        break;
  return value;
  

    
def CheckData(data, email_result):
    byte_code = base64.urlsafe_b64decode(data)

    deleted_count=0;
    text = byte_code.decode("utf-8")
    text = str(text)
    text= text.lower()
    for WordSearch in Key_Words_Delet:
      deleted=False;
      found_key=True;
      try:
        if text.find(WordSearch):
         
          for WordSearchGood in Key_Words_Keep:
            if not text.find(WordSearchGood)==-1:
              found_key=False;
              break;
        if found_key==True and deleted==False:
          
          deleted_count=1
          gmail_service.users().messages().trash(userId='me',
                                                id=email_result['id']).execute()
          break;
      except Exception as error:
        print(f'An error occurred: {error}')
       
    return deleted_count;


email_results = search_emails("")#nothing specific in query

deleted_count=0;
total_count =len(email_results);
current_count=0;
# Step 2. delete emails

for email_result in email_results:
  current_count+=1;
  print(f"{100*(current_count/total_count)}%...");
  
  try:
    msg= gmail_service.users().messages().get(userId='me', id=email_result['id']).execute()
          
    deleted_count+=CheckPart(msg, email_result);
       
        
  except Exception as error:
        print(f'An error occurred: {error}')
  


print(f'There were a total of {total_count} messages and {deleted_count} message deleted')
