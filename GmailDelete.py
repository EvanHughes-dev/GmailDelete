import time
import base64
from tkinter import *

import GoogleConnect as GoogleAccess
import list_search as get_key_words
from tkcalendar import DateEntry

CLIENT_FILE = 'client-secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']


is_logged_in: bool = False

get_key_words.check_folder()  # check if the directory exists
get_key_words.check_files()  # check if the files exists


def create_gmail_services():
    return GoogleAccess.create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)


def create_empty_window():
    created_window_object = Tk()
    return created_window_object


# <editor-fold desc="Login">
def create_login(main_window):
    GoogleAccess.create_service(CLIENT_FILE, API_NAME, API_VERSION, SCOPES)
    main_window.destroy()
    display_options()


def create_button(main_window):
    button = Button(main_window, text="Click to Login", command=lambda: create_login(main_window),
                    activebackground="#ff8aba")
    button.pack()
    return main_window


def login():
    window = create_empty_window()
    window = create_button(window)
    window.mainloop()


def log_out(window):
    GoogleAccess.remove_login(API_NAME, API_VERSION)
    window.destroy()
    login()

# </editor-fold>>

# <editor-fold desc="Display Options">


def create_logout(main_window):
    Button(main_window, text="Click to Logout", command=lambda: log_out(main_window),
           activebackground="#ff8aba").grid(row=1, column=1)


def save_new_word(name_object, main_window, color):
    text_value = name_object.get()
    get_key_words.add_word_new(text_value, color)
    name_object.delete(0, END)
    change_words(main_window)


def create_frames(main_window):
    main_body_color = 'red'

    main_body = Frame(main_window, width=main_window.winfo_screenwidth()/4,
                      height=main_window.winfo_screenheight()/3, bg=main_body_color)
    main_body.grid(row=0, column=1, padx=10, pady=5)
    main_body.grid_propagate(0)

    create_header(main_body, main_body_color)
    create_body_options(main_body)

    bigger_add_word_frame = Frame(main_window, width=150, height=100, bg='#3f929e')
    bigger_add_word_frame.grid(row=0, column=2, padx=10, pady=5)

    add_word_frame = Frame(bigger_add_word_frame, width=100, height=100, bg='#65979e')
    add_word_frame.grid(row=0, column=2, padx=10, pady=5)

    create_buttons(add_word_frame, main_window)

    return main_window


def create_word_display_frame(main_window):
    left_frame = Frame(main_window, width=650, height=400, bg='grey')
    left_frame.grid(row=0, column=0, padx=10, pady=5)

    left_frame.grid_propagate(0)
    display_words(left_frame, main_window)


def create_header(main_body, main_body_color):

    header_width_sides = main_body.winfo_screenwidth()/16
    header_width_center = main_body.winfo_screenwidth()/8

    header_height = main_body.winfo_screenheight()/21

    main_body_header_color = "green"

    status_frame = Frame(main_body, width=main_body.winfo_screenwidth()/4, height=header_height, bg=main_body_color)
    status_frame.grid(row=0, column=0, columnspan=5)
    current_status = Label(status_frame, text="No Current Operations", bg=main_body_color)
    current_status.place(relx=0.5, rely=0.5, anchor=CENTER)

    Frame(main_body, width=header_width_sides, height=header_height, bg=main_body_color).grid(row=1, column=0)

    main_body_header = Frame(main_body, width=header_width_center, height=header_height, bg=main_body_header_color)
    main_body_header.grid(row=1, column=1, columnspan=3)
    main_body_header.grid_propagate(0)
    Label(main_body_header, text="Test", bg=main_body_header_color).place(relx=0.5, rely=0.5, anchor=CENTER)

    Frame(main_body, width=header_width_sides, height=header_height, bg=main_body_color).grid(row=1, column=4)


def create_buttons(add_word_frame, main_window):
    # create an input field for black phrases
    Label(add_word_frame, text="Create Black Word").grid(row=3, column=0, padx=10, pady=5)

    black_entry = Entry(add_word_frame, bd=5)
    black_entry.grid(row=3, column=1, padx=10, pady=5)
    black_button = Button(add_word_frame, text="Press to add", command=lambda: save_new_word(
        black_entry, main_window, color="black"), bd=5)
    black_button.grid(row=3, column=2, padx=10, pady=5)

    # do same for white
    Label(add_word_frame, text="Create white Word").grid(row=4, column=0, padx=10, pady=5)

    white_entry = Entry(add_word_frame, bd=5)
    white_entry.grid(row=4, column=1, padx=10, pady=5)
    white_button = Button(add_word_frame, text="Press to add", command=lambda: save_new_word(
        white_entry, main_window, color="white"), bd=5)
    white_button.grid(row=4, column=2, padx=10, pady=5)


def create_body_options(main_body):

    Button(main_body, text="Delete By Content", command=lambda: delete_by_content()).grid(row=2, column=0, pady=5)
    Button(main_body, text="Clear Words").grid(row=2, column=1)
    date = DateEntry(main_body, background="magenta3", foreground="white", bd=2)
    date.grid(row=2, column=2, columnspan=2)

    Button(main_body, text="Delete By Date", command=lambda: delete_by_year(date.get_date().strftime("%m/%d/%Y"))).grid(
        row=2, column=4)


def display_options():
    window = create_empty_window()
    create_logout(window)
    create_frames(window)
    create_word_display_frame(window)
    window.state('zoomed')
    window.title("Gmail Spam Deleter")
    window.mainloop()


def display_words(frame, window):
    word_date = get_key_words.read_files()

    white_word_data = word_date["white"]
    black_word_data = word_date["black"]

    return_frames_for_list(frame, white_word_data, "white", window)
    return_frames_for_list(frame, black_word_data, "black", window)


def return_frames_for_list(frame, list_values, white_black, window):

    current_row = 1
    current_column = 0

    header_font_size = 30
    body_font_size = 20

    padding_y_header = 3
    padding_x_header = 5

    padding_y_body = 2
    padding_x_body = 1

    if white_black == "white":
        Label(frame, text="White List", font=header_font_size).grid(
            row=0, column=current_column, pady=padding_y_header, padx=padding_x_header, columnspan=2)
    else:
        current_column = 2
        Label(frame, text="Black List", font=header_font_size).grid(
            row=0, column=current_column, pady=padding_y_header, padx=padding_x_header, columnspan=2)

    for item in list_values:

        temp_word_frame = Frame(frame)
        temp_word_frame.grid(row=current_row, column=current_column, columnspan=2, pady=padding_y_body, padx=padding_x_body)

        Label(temp_word_frame, text=item, font=body_font_size).grid(row=0, column=0)

        Button(temp_word_frame, text="X", bg="red", command=lambda: delete_word(
            item, white_black, window)).grid(
            row=0, column=1)

        current_row += 1


def delete_word(item, white_black, window):
    get_key_words.delete_word(item, white_black)
    change_words(window)


def change_words(window):
    create_word_display_frame(window)

# </editor-fold>

# <editor-fold desc="search email">


def search_emails(gmail_service, query, labels=None):
    # email_messages = []

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
def check_delete(email_results, gmail_service):
    total_count = len(email_results)
    current_count = 0
    deleted_count = 0
    for email_result in email_results:
        current_count += 1
        print(f"{100 * (current_count / total_count)}%...")

        try:
            msg = gmail_service.users().messages().get(userId='me', id=email_result['id']).execute()

            deleted_count += check_all_data(gmail_service, msg, email_result)

        except Exception as error:
            print(f'An error occurred: {error}')

    print(f'There were a total of {total_count} messages and {deleted_count} message deleted')


def delete_by_year(time_value):
    gmail_service = create_gmail_services()
    query = "before:" + time_value
    email_results = search_emails(gmail_service, query)

    for email_result in email_results:

        gmail_service.users().messages().trash(userId='me',
                                               id=email_result['id']).execute()
        time.sleep(0.5)


def delete_by_content():
    gmail_service = create_gmail_services()
    query = ""

    email_results = search_emails(gmail_service, query)
    check_delete(email_results, gmail_service)

    
def check_all_data(gmail_service, part, email_result):
    value = 0
    if "body" in part:
        if "data" in part["body"]:
            value += check_for_text(gmail_service, part['body']["data"], email_result)
        elif "parts" in part:
            for item in part["parts"]:
                value += check_all_data(gmail_service, item, email_result)
    elif "data" in part["payload"]["body"]:
        value += check_for_text(gmail_service, part["payload"]["body"]["data"], email_result)
    elif "parts" in part["payload"]:

        for item in part["payload"]["parts"]:
            value += check_all_data(gmail_service, item, email_result)
            if value >= 1:
                break
    return value


def check_for_text(gmail_service, data, email_result):
    byte_code = base64.urlsafe_b64decode(data)

    deleted_count = 0
    text = byte_code.decode("utf-8")
    text = str(text)
    text = text.lower()
    key_words_delete = get_key_words.read_files()['black']
    key_words_keep = get_key_words.read_files()['white']

    for word_search in key_words_delete:

        found_key = False
        word_search = word_search.lower()

        try:

            if not text.find(word_search) == -1:
                found_key = True

                for word_search_good in key_words_keep:
                    word_search_good = word_search_good.lower()
                    if not text.find(word_search_good) == -1:
                        found_key = False
                        break
            if found_key:
                deleted_count = 1

                gmail_service.users().messages().trash(userId='me',
                                                       id=email_result['id']).execute()
                break
        except Exception as error:
            print(f'An error occurred: {error}')

    return deleted_count
# </editor-fold>


if not GoogleAccess.check_connection(API_NAME, API_VERSION):
    login()
else:
    display_options()
