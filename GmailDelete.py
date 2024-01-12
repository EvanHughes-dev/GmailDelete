import time
import base64
from tkinter import *
import GoogleConnect as GoogleAccess
import list_search as get_key_words


CLIENT_FILE = 'client-secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

Key_Words_Delet = ["unsubscribe", "college", "alerts", "university"]
Key_Words_Keep = ["champlain", "drexel", "pitt", "rochester"]
is_logged_in: bool = False

get_key_words.check_folder() # check if the directory exists
get_key_words.check_files() # check if the files exists

def create_empty_window():
    CreatedWindowObject = Tk()
    return CreatedWindowObject


# <editor-fold desc="Login">
def create_login(main_window):
    GoogleAccess.create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)
    main_window.destroy()


def create_button(main_window):
    button = Button(main_window, text="Click to Login", command=lambda : create_login(main_window), activebackground="#ff8aba")
    button.pack()
    return main_window


def login():
    window = create_empty_window();
    window = create_button(window)
    window.mainloop()


def log_out(window):
    GoogleAccess.remove_login(API_NAME, API_VERSION)
    window.destroy()
    login()

# </editor-fold>>


# <editor-fold desc="Display Options>
def create_logout(main_window):
    button = Button(main_window, text="Click to Logout", command=lambda: log_out(main_window), activebackground="#ff8aba")

    return main_window


def save_new_black_name(nameOBJ):
    textValue = nameOBJ.get()
    get_key_words.add_data_black(textValue)
    nameOBJ.delete(0, END)


def save_new_white_name(nameOBJ):
    textValue = nameOBJ.get()
    get_key_words.add_data_white(textValue)
    nameOBJ.delete(0, END)


def create_inputs(main_window):

    right_frame = Frame(main_window, width=650, height=400, bg='grey')
    right_frame.grid(row=0, column=0, padx=10, pady=5)

    bigger_add_word_frame = Frame(main_window, width=150, height=100, bg='#3f929e')
    bigger_add_word_frame.grid(row=0, column=2, padx=10, pady=5)
    add_word_frame = Frame(bigger_add_word_frame, width=100, height=100, bg='#65979e')
    add_word_frame.grid(row=0, column=2, padx=10, pady=5)

    # create an input field for black phrases
    Label(add_word_frame, text="Create Black Word").grid(row=3, column=0, padx=10, pady=5)
    black_entry = Entry(add_word_frame, bd=5)
    black_entry.grid(row=3, column=1, padx=10, pady=5)
    Button(add_word_frame, text="Press to add", command=lambda: save_new_black_name(black_entry), bd=5).grid(row=3, column=2, padx=10, pady=5)

    # do same for white
    Label(add_word_frame, text="Create white Word").grid(row=4, column=0, padx=10, pady=5)
    white_entry = Entry(add_word_frame, bd=5)
    white_entry.grid(row=4, column=1, padx=10, pady=5)
    Button(add_word_frame, text="Press to add", command=lambda: save_new_white_name(white_entry), bd=5).grid(row=4, column=2, padx=10, pady=5)
    return main_window


def display_options():
    window = create_empty_window()
    window = create_logout(window)
    window = create_inputs(window)
    window.state('zoomed')
    window.title("Gmail Spam Deleter")
    window.mainloop()


# </editor-fold>


# <editor-fold desc="search email">

def search_emails(gmail_service, query, labels=None):
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
        # print('Page Token: {0}'.format(next_page_token))
        time.sleep(0.5)

    return email_messages


# </editor-fold>

# <editor-fold desc="Specific Search">

def delete_by_year(email_results, gmail_service):
    query = "before:2022/10/20"
    email_result = search_emails(query)
    for email_result in email_results:
        gmail_service.users().messages().trash(userId='me',
                                               id=email_result['id']).execute()


def check_all_data(part, email_result):
    value = 0;
    if "body" in part:
        if "data" in part["body"]:
            value += check_for_text(part['body']["data"], email_result)
        elif "parts" in part:
            for item in part["parts"]:
                value += check_all_data(item, email_result)
    elif "data" in part["payload"]["body"]:
        value += check_for_text(part["payload"]["body"]["data"], email_result);
    elif "parts" in part["payload"]:

        for item in part["payload"]["parts"]:
            value += check_all_data(item, email_result)
            if value >= 1:
                break;
    return value;


def check_for_text(gmail_service, data, email_result):
    byte_code = base64.urlsafe_b64decode(data)

    deleted_count = 0
    text = byte_code.decode("utf-8")
    text = str(text)
    text = text.lower()
    for WordSearch in Key_Words_Delet:
        deleted = False;
        found_key = True;
        try:
            if text.find(WordSearch):

                for WordSearchGood in Key_Words_Keep:
                    if not text.find(WordSearchGood) == -1:
                        found_key = False;
                        break;
            if found_key == True and deleted == False:
                deleted_count = 1
                gmail_service.users().messages().trash(userId='me',
                                                       id=email_result['id']).execute()
                break;
        except Exception as error:
            print(f'An error occurred: {error}')

    return deleted_count;
# </editor-fold>


if not GoogleAccess.check_connection(API_NAME, API_VERSION):
    login()
else:
    display_options()
# email_results = search_emails("")  # nothing specific in query


# Step 2. delete emails
def check_delete(email_results, gmail_service):
    total_count = len(email_results)
    current_count = 0
    deleted_count = 0
    for email_result in email_results:
        current_count += 1;
        print(f"{100 * (current_count / total_count)}%...");

        try:
            msg = gmail_service.users().messages().get(userId='me', id=email_result['id']).execute()

            deleted_count += check_all_data(msg, email_result);


        except Exception as error:
            print(f'An error occurred: {error}')

    print(f'There were a total of {total_count} messages and {deleted_count} message deleted')
