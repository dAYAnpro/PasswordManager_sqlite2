from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox
import sqlite_database_controller as sdc
from cryptography.fernet import Fernet
from pathlib import Path
import uuid
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for both dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running as a PyInstaller bundle, use the current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ========================CONSTs============================
# Use resource_path to access your files
local_log_path = resource_path("app_data/Logs.txt")

sdc.database = str(resource_path('app_data/MainDataBase.db'))
selected_row_data = ()
# ========================GUI============================

# =======================SIGNUP===========================
def is_logged_in():
    device_id = local_log()
    user_log_state = sdc.get_table_data('Logs',
                                        condition='device_id = ?',condition_values=(device_id,))
    if user_log_state: # if saved id in local log is in database user_log_state is not empty
        return True
    else:
        return False
def is_signed_up(name:str):
    user_sign_state = sdc.get_table_data('Users',condition=f'name = {name}')
    if user_sign_state:
        return True
    else:
        return False
def check_password(name:str,password:str):
    try:
        user_data = sdc.get_table_data('Users', selections=('id', 'password'),
                                       condition=f'name = ?',condition_values=(name,),
                                       limit=1)
        if user_data[0][1]:
            if password == user_data[0][1]:  # password
                return user_data[0][0]  # id
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f'Error in checking_password: {e}')

def local_log(record:bool=False,return_user_id:bool=False,clear_log:bool=False):  # true to record false to get
    path = Path(str(local_log_path))
    path.touch(exist_ok=True)
    if clear_log: # clear device id in log
        with open(local_log_path, 'w+') as file:
            file.write('')
            file.close()
        return True
    if return_user_id:
        device_id = local_log()
        user_id = sdc.get_table_data('Logs', selections=('user_id',),
                                     condition=f'device_id = ?',condition_values=(device_id,))[0][0]
        return user_id
    else:
        if record:
            device_id = uuid.uuid4()
            device_id = str(device_id)
            with open(local_log_path, 'w+') as file:
                file.write(str(device_id))
                file.close()
            return device_id
        else:
            with open(local_log_path, 'r') as f:
                device_id = f.read()
                f.close()
                if device_id:
                    return device_id
                else :
                    return False
def global_log(clear_log:bool=False):
    if clear_log:
        device_id = local_log()
        # delete row with this device id in logs
        sdc.delete_table_row('Logs',conditions='device_id = ?',condition_values=(device_id,))
def encrypt_password(password:str):
    password_bytes = password.encode('utf-8')
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password_bytes)
    return key, encrypted_password

def decrypt_password(encrypted_password,key):
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password)
    return decrypted_password.decode('utf-8')
#=======================LOGIN===========================
def sign_up():
    # start window -----------------------------------------------------------------
    window_signup = Tk()
    window_signup.title("Sign Up")
    window_signup.geometry("1000x720")
    window_signup.config(bg="#353535")
    window_signup.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # image icon ---------------------------------------------------------------------------------
    # pass_image_icon = ImageTk.PhotoImage(Image.open("Password.png").resize(320,120))
    # pass_image_label = Label(window_signup, image=pass_image_icon)
    # pass_image_label.place(x=50, y=140)
    # welcome text ---------------------------------------------------------------------------------
    text_welcome = Label(window_signup, text="Welcome to Password Manager",bg='#353535',fg='white',font=("Arial",20))
    text_welcome.pack()
    text_welcome.place(x=160,y=20)
    text_welcome_style = ('Caveat',50,'bold')
    text_welcome.configure(font=text_welcome_style)
    # username text ---------------------------------------------------------------------------
    text_username = Label(window_signup, text="Enter Username",bg='#353535',fg='white',font=("Arial",20))
    text_username.pack()
    text_username.place(x=350,y=150)
    text_username_style = ('Comic Sans Ms',15,'bold')
    text_username.configure(font=text_username_style)
    # username input ----------------------------------------------------------------------------
    entry_username = Entry(window_signup,width=30,font=("Arial",33))
    entry_username.pack()
    entry_username.place(x=350,y=190)
    entry_username_style = ('Centaur',17,'bold')
    entry_username.configure(font=entry_username_style)
    # enter password text ---------------------------------------------------------------------------
    text_password = Label(window_signup, text="Enter Password",bg='#353535',fg='white',font=("Arial",20))
    text_password.pack()
    text_password.place(x=350,y=220)
    text_password_style = ('Comic Sans Ms',15,'bold')
    text_password.configure(font=text_password_style)
    # password input ----------------------------------------------------------------------------
    entry_password = Entry(window_signup,width=30,font=("Arial",33))
    entry_password.pack()
    entry_password.place(x=350,y=260)
    entry_password_style = ('Centaur',17,'bold')
    entry_password.configure(font=entry_password_style)
    # click button func -----------------------------------------------------------------
    def signup_input():
        user_input = entry_username.get()
        pass_input = entry_password.get()
        if user_input == '' or pass_input=='':
            messagebox.showerror("Error","Please enter your username and password")
        elif sdc.get_table_data('Users',condition='name = ?',condition_values=(user_input,)):
            messagebox.showerror("Error","Username already exists")
        else:
            sdc.add_to_table('Users',{'name':user_input,'password':pass_input})
            messagebox.showinfo('Signed Up', 'Thank You.\n Now you can log in.')
            window_signup.destroy()
            log_in()
    # sign up button ---------------------------------------------------------------------------
    button_signup = Button(window_signup,text = ' Sign Up',width=20,bg='green',fg='white',font=("Arial",20),command=signup_input)
    button_signup.pack()
    button_signup.place(x=390,y=300)
    button_signup_style = ('Centaur',17,'bold')
    button_signup.configure(font=button_signup_style)
    # main_page handle -------------------------------------------------------------------------------
    def main_page_button_command():
        window_signup.destroy()
        main_window()
    # main_page button ---------------------------------------------------------------------------
    button_main_window = Button(window_signup, text='Main', width=15, bg='green', fg='white', font=("Arial", 20),
                                command=main_page_button_command)
    button_main_window.pack()
    button_main_window.place(x=420, y=350)
    button_main_window_style = ('Centaur', 17, 'bold')
    button_main_window.configure(font=button_main_window_style)


    window_signup.mainloop()

def log_in():
    # start window -----------------------------------------------------------------
    window_login = Tk()
    window_login.title("Login In")
    window_login.geometry("1000x720")
    window_login.config(bg="#353535")
    window_login.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # login text ---------------------------------------------------------------------------------
    text_login = Label(window_login, text="Login",bg='#353535',fg='white',font=("Arial",20))
    text_login.pack()
    text_login.place(x=380,y=20)
    text_login_style = ('Caveat',50,'bold')
    text_login.configure(font=text_login_style)
    # frame ---------------------------------------------------------------------------------
    frame = Frame(window_login,bg='#555454',height=500,width=360)
    frame.pack()
    frame.place(x=260,y=120)
    # username text ---------------------------------------------------------------------------
    text_password = Label(frame, text="Enter Username", bg='#555454', fg='white', font=("Arial", 20))
    text_password.pack()
    text_password.place(x=20, y=20)
    text_password_style = ('Comic Sans Ms', 15, 'bold')
    text_password.configure(font=text_password_style)
    # username input ----------------------------------------------------------------------------
    entry_username = Entry(frame, width=20, font=("Arial", 33))
    entry_username.pack()
    entry_username.place(x=20, y=60)
    entry_username_style = ('Centaur', 17, 'bold')
    entry_username.configure(font=entry_username_style)
    # enter password text ---------------------------------------------------------------------------
    text_password = Label(frame, text="Enter Password",bg='#555454',fg='white',font=("Arial",20))
    text_password.pack()
    text_password.place(x=20,y=100)
    text_password_style = ('Comic Sans Ms',15,'bold')
    text_password.configure(font=text_password_style)
    # password input ----------------------------------------------------------------------------
    entry_password = Entry(frame,width=20,font=("Arial",33))
    entry_password.pack()
    entry_password.place(x=20,y=140)
    entry_password_style = ('Centaur',17,'bold')
    entry_password.configure(font=entry_password_style)
    # login handle -------------------------------------------------------------------------------
    def login_input():
        user_input = entry_username.get()
        pass_input = entry_password.get()
        if user_input == '' or pass_input=='':
            messagebox.showerror("Error","Please enter your username and password")
        elif check_password(user_input,pass_input):
            id = check_password(user_input,pass_input)
            device_id = local_log(record=True)
            sdc.add_to_table('Logs', {'user_id': id,'device_id':device_id})
            messagebox.showinfo("Logged in","Username and password is CORRECT.")
            window_login.destroy()
            passwords()
        else:
            messagebox.showerror("Error", "Username or password wrong.")
    # login button ---------------------------------------------------------------------------
    button_login = Button(frame,text = 'Login',width=15,bg='green',fg='white',font=("Arial",20),command=login_input)
    button_login.pack()
    button_login.place(x=20,y=180)
    button_login_style = ('Centaur',17,'bold')
    button_login.configure(font=button_login_style)
    # main_page handle -------------------------------------------------------------------------------
    def main_page_button_command():
        window_login.destroy()
        main_window()
    # main_page button ---------------------------------------------------------------------------
    button_main_window = Button(frame,text = 'main',width=15,bg='green',fg='white',font=("Arial",20),command=main_page_button_command)
    button_main_window.pack()
    button_main_window.place(x=20,y=230)
    button_main_window_style = ('Centaur',17,'bold')
    button_main_window.configure(font=button_main_window_style)

    window_login.mainloop()

def main_window():
    # start window -----------------------------------------------------------------
    window_main = Tk()
    window_main.title("Password Manager")
    window_main.geometry("1000x720")
    window_main.config(bg="#353535")
    window_main.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # login text ---------------------------------------------------------------------------------
    text_welcome = Label(window_main, text="Welcome to Password Manager", bg='#353535', fg='white', font=("Arial", 20))
    text_welcome.pack()
    text_welcome.place(x=100, y=20)
    text_welcome_style = ('Caveat', 50, 'bold')
    text_welcome.configure(font=text_welcome_style)
    # frame ---------------------------------------------------------------------------------
    frame = Frame(window_main, bg='#555454', height=300, width=360)
    frame.pack()
    frame.place(x=250, y=120)
    # login button command----------------------------------------------------------------------------------
    def login_button_command():
        window_main.destroy()
        log_in()
    # login button ---------------------------------------------------------------------------
    button_login = Button(frame, text='LOGIN', width=15, bg='green', fg='white', font=("Arial", 20),command=login_button_command)
    button_login.pack()
    button_login.place(x=80, y=100)
    button_login_style = ('Centaur', 17, 'bold')
    button_login.configure(font=button_login_style)
    # signup button command -------------------------------------------------------------------
    def signup_button_command():
        window_main.destroy()
        sign_up()
    # signup button ---------------------------------------------------------------------------
    button_signup = Button(frame, text='SIGNUP', width=15, bg='green', fg='white', font=("Arial", 20),command=signup_button_command)
    button_signup.pack()
    button_signup.place(x=80, y=150)
    button_signup_style = ('Centaur', 17, 'bold')
    button_signup.configure(font=button_signup_style)

    window_main.mainloop()

def passwords():
    # Window ------------------------------------------------------------------------------
    window_passwords = Tk()
    window_passwords.title("Password Manager")
    window_passwords.geometry("1000x700")
    window_passwords.config(bg="#353535")
    window_passwords.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # add password button command ---------------------------------------------------------------------
    def add_password_command():
        add_password(refresh_command)
    # add passwords button ----------------------------------------------------------------------
    button_add_password = Button(window_passwords,text = 'Add Password',width=12,bg='green',fg='white',font=("Arial",20),command=add_password_command)
    button_add_password.pack()
    button_add_password.place(x=10,y=15)
    button_add_password_style = ('Centaur',14,'bold')
    button_add_password.configure(font=button_add_password_style)
    # edit password button command ---------------------------------------------------------------------
    def edit_password_command():
        if selected_row_data:
            edit_password(refresh_command,selected_row_data[0],selected_row_data[1],selected_row_data[2],selected_row_data[3],selected_row_data[4])
        else:
            messagebox.showerror("Error","Please select a row.")
    # edit passwords button ----------------------------------------------------------------------
    button_edit_password = Button(window_passwords,text = 'Edit Password',width=12,bg='green',fg='white',font=("Arial",20),command=edit_password_command)
    button_edit_password.pack()
    button_edit_password.place(x=160,y=15)
    button_edit_password_style = ('Centaur',14,'bold')
    button_edit_password.configure(font=button_edit_password_style)
    # delete password button command ---------------------------------------------------------------------
    def delete_password_command():
        if selected_row_data:
            pass_id,app_name,app_username,app_password,app_description = selected_row_data
            user_id = local_log(return_user_id=True)
            if user_id:
                sdc.delete_table_row('Passwords',
                                 conditions='id =? and user_id = ? and app_name = ? and app_username = ? and app_description = ?',
                                 condition_values=(pass_id,user_id,app_name,app_username,app_description))
                refresh_command()
            else:
                print('user id not found')
        else:
            messagebox.showerror("Error","Please select a row.")
    # delete passwords button ----------------------------------------------------------------------
    button_delete_password = Button(window_passwords,text = 'delete Password',width=12,bg='green',fg='white',font=("Arial",20),command=delete_password_command)
    button_delete_password.pack()
    button_delete_password.place(x=310,y=15)
    button_delete_password_style = ('Centaur',14,'bold')
    button_delete_password.configure(font=button_delete_password_style)
    # log out button command ---------------------------------------------------------------------
    def log_out_command():
        global_log(clear_log=True)
        window_passwords.destroy()
        main_window()
    # log out button ----------------------------------------------------------------------
    button_logout = Button(window_passwords, text='Log Out', width=12, bg='green', fg='white',
                                 font=("Arial", 20), command=log_out_command)
    button_logout.pack()
    button_logout.place(x=850, y=15)
    button_logout_style = ('Centaur', 14, 'bold')
    button_logout.configure(font=button_logout_style)
    # refresh button command ---------------------------------------------------------------------
    def refresh_command():
        update_tree()
    # refresh button ----------------------------------------------------------------------
    button_refresh = Button(window_passwords, text='Refresh', width=12, bg='green', fg='white',
                           font=("Arial", 20), command=refresh_command)
    button_refresh.pack()
    button_refresh.place(x=700, y=15)
    button_refresh_style = ('Centaur', 14, 'bold')
    button_refresh.configure(font=button_refresh_style)
    # passwords frame --------------------------------------------------------------------------
    frame_password = Frame(window_passwords,bg='#555454',height=630,width=980)
    frame_password.pack()
    frame_password.place(x=10, y=60)
    # tree(df) passwords -----------------------------------------------------------------------
    def update_tree():
        # password table item selected ------------------------------------------------------------
        def on_row_select(event):
            """Function to handle row selection in Treeview."""
            global selected_row_data
            # Get selected row from Treeview
            selected_item = tree_passwords.selection()
            if selected_item:
                # Get values from the selected item
                selected_row_data = tree_passwords.item(selected_item)["values"]
                # tree_passwords.delete(selected_item)

        # password table item clicked -------------------------------------------------------------
        def on_item_click(event):
            # Get the clicked item and its column
            region = tree_passwords.identify_region(event.x, event.y)  # Identify the region clicked
            if region == 'cell':
                item = tree_passwords.identify_row(event.y)  # Get the row of the clicked cell
                column = tree_passwords.identify_column(event.x)  # Get the column of the clicked cell

                if item and column:  # Ensure item and column are valid
                    cell_value = tree_passwords.item(item, 'values')[int(column[1:]) - 1]  # Get the cell value
                    # Copy to clipboard
                    frame_password.clipboard_clear()  # Clear the clipboard
                    frame_password.clipboard_append(cell_value)  # Append the cell value to clipboard
                    temp_window = Toplevel(frame_password)
                    temp_window.title("Copped")
                    # Add a label with the message
                    label = Label(temp_window, text=f"Copied: {cell_value}", padx=20, pady=20)
                    label.pack()
                    # Close the temporary window after the specified duration
                    temp_window.after(1000, temp_window.destroy)
        # passwords data polling -------------------------------------------------------------------
        user_id = local_log(return_user_id=True)
        # all the passwords
        passwords_data = sdc.get_table_data('Passwords',
                                            selections=('id','app_name', 'app_username', 'app_password', 'password_key','app_description'),
                                            condition='user_id = ?', condition_values=(user_id,), as_dataframe=True)
        if not passwords_data.empty:
            passwords_data['app_password'] = passwords_data.apply(
            lambda row: decrypt_password(row.app_password, row.password_key), axis=1)
            passwords_data = passwords_data.drop(columns=['password_key'])
            # passwords tree --------------------------------------------------------------------------
            tree_passwords = Treeview(frame_password)
            tree_passwords['columns'] = list(passwords_data.columns)
            tree_passwords['show'] = 'headings'
            # headers
            for col in passwords_data.columns:
                tree_passwords.heading(col, text=col)
                tree_passwords.column(col, anchor='center', width=192)
            # rows
            for index, row in passwords_data.iterrows():
                tree_passwords.insert("", "end", values=list(row))
            # for copy
            tree_passwords.bind('<Double-1>', on_item_click)
            # Bind single left-click to row selection
            tree_passwords.bind("<ButtonRelease-1>", on_row_select)
            tree_passwords.pack()
            tree_passwords.place(x=10, y=5)
        else:
            for widget in frame_password.winfo_children():
                widget.destroy()
    update_tree()
    # run -------------------------------------------------------------------------------------
    window_passwords.mainloop()
def add_password(refresh_command):
    window_add_password = Toplevel()
    window_add_password.title("ADD Password")
    window_add_password.geometry("400x400")
    window_add_password.config(bg="#353535")
    window_add_password.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # add password text ---------------------------------------------------------------------------------
    text_add_password = Label(window_add_password, text="Add Password", bg='#353535', fg='white',font=("Arial", 10))
    text_add_password.pack()
    text_add_password.place(x=120, y=5)
    text_add_password_style = ('Caveat', 20, 'bold')
    text_add_password.configure(font=text_add_password_style)
    # frame ---------------------------------------------------------------------------------
    frame = Frame(window_add_password,bg='#555454',height=325,width=300)
    frame.pack()
    frame.place(x=50,y=50)
    # app_name text ---------------------------------------------------------------------------
    text_app_name = Label(frame, text="App Name", bg='#555454', fg='white', font=("Arial", 20))
    text_app_name.pack()
    text_app_name.place(x=20, y=5)
    text_app_name_style = ('Comic Sans Ms', 12, 'bold')
    text_app_name.configure(font=text_app_name_style)
    # app_name input ----------------------------------------------------------------------------
    entry_app_name = Entry(frame, width=20, font=("Arial", 33))
    entry_app_name.pack()
    entry_app_name.place(x=20, y=35)
    entry_app_name_style = ('Centaur', 17, 'bold')
    entry_app_name.configure(font=entry_app_name_style)
    # app_username text ---------------------------------------------------------------------------
    text_app_username = Label(frame, text="User Name", bg='#555454', fg='white', font=("Arial", 20))
    text_app_username.pack()
    text_app_username.place(x=20, y=65)
    text_app_username_style = ('Comic Sans Ms', 12, 'bold')
    text_app_username.configure(font=text_app_username_style)
    # app_username input ----------------------------------------------------------------------------
    entry_app_username = Entry(frame, width=20, font=("Arial", 33))
    entry_app_username.pack()
    entry_app_username.place(x=20, y=95)
    entry_app_username_style = ('Centaur', 17, 'bold')
    entry_app_username.configure(font=entry_app_username_style)
    # app_password text ---------------------------------------------------------------------------
    text_app_password = Label(frame, text="Password", bg='#555454', fg='white', font=("Arial", 20))
    text_app_password.pack()
    text_app_password.place(x=20, y=125)
    text_app_password_style = ('Comic Sans Ms', 12, 'bold')
    text_app_password.configure(font=text_app_password_style)
    # app_password input ----------------------------------------------------------------------------
    entry_app_password = Entry(frame, width=20, font=("Arial", 33))
    entry_app_password.pack()
    entry_app_password.place(x=20, y=155)
    entry_app_password_style = ('Centaur', 17, 'bold')
    entry_app_password.configure(font=entry_app_password_style)
    # app_description text ---------------------------------------------------------------------------
    text_app_description = Label(frame, text="Description", bg='#555454', fg='white', font=("Arial", 20))
    text_app_description.pack()
    text_app_description.place(x=20, y=185)
    text_app_description_style = ('Comic Sans Ms', 12, 'bold')
    text_app_description.configure(font=text_app_description_style)
    # app_description input ----------------------------------------------------------------------------
    entry_app_description = Entry(frame, width=20, font=("Arial", 33))
    entry_app_description.pack()
    entry_app_description.place(x=20, y=215)
    entry_app_description_style = ('Centaur', 17, 'bold')
    entry_app_description.configure(font=entry_app_description_style)
    # click button func -----------------------------------------------------------------
    def add_input():
        appname_input = entry_app_name.get()
        app_username_input = entry_app_username.get()
        app_password_input = entry_app_password.get()
        app_description_input = entry_app_description.get()
        key,encrypted_pass = encrypt_password(app_password_input)
        user_id = local_log(return_user_id=True)
        if user_id:
            sdc.add_to_table('Passwords',values={'user_id':user_id,
                                                 'app_name':appname_input,
                                                 'app_username':app_username_input,
                                                 'app_password':encrypted_pass,
                                                 'password_key':key,
                                                 'app_description':app_description_input})
        else:
            print('user id not found')

        on_closing()

    # add password button ---------------------------------------------------------------------------
    button_add_password = Button(frame, text=' ADD', width=15, bg='green', fg='white', font=("Arial", 20),command=add_input)
    button_add_password.pack()
    button_add_password.place(x=20, y=265)
    button_add_password_style = ('Centaur', 17, 'bold')
    button_add_password.configure(font=button_add_password_style)
    # on closing -------------------------------------------------------------------------------------
    def on_closing():
        refresh_command()
        window_add_password.destroy()
    # main -----------------------------------------------------------------------------------------
    # Bind the window close event to `on_closing` function
    window_add_password.protocol("WM_DELETE_WINDOW", on_closing)
    window_add_password.mainloop()
def edit_password(refresh_command,password_id,app_name,app_username,app_password,app_description):
    window_edit_password = Toplevel()
    window_edit_password.title("Edit Password")
    window_edit_password.geometry("400x400")
    window_edit_password.config(bg="#353535")
    window_edit_password.resizable(False, False)
    # window_signup.iconbitmap("icon.ico")
    # add password text ---------------------------------------------------------------------------------
    text_edit_password = Label(window_edit_password, text="Add Password", bg='#353535', fg='white',font=("Arial", 10))
    text_edit_password.pack()
    text_edit_password.place(x=120, y=5)
    text_edit_password_style = ('Caveat', 20, 'bold')
    text_edit_password.configure(font=text_edit_password_style)
    # frame ---------------------------------------------------------------------------------
    frame = Frame(window_edit_password,bg='#555454',height=325,width=300)
    frame.pack()
    frame.place(x=50,y=50)
    # app_name text ---------------------------------------------------------------------------
    text_app_name = Label(frame, text="App Name", bg='#555454', fg='white', font=("Arial", 20))
    text_app_name.pack()
    text_app_name.place(x=20, y=5)
    text_app_name_style = ('Comic Sans Ms', 12, 'bold')
    text_app_name.configure(font=text_app_name_style)
    # app_name input ----------------------------------------------------------------------------
    entry_app_name = Entry(frame, width=20, font=("Arial", 33))
    entry_app_name.insert(0, app_name)  # Insert the placeholder text initially
    entry_app_name.pack()
    entry_app_name.place(x=20, y=35)
    entry_app_name_style = ('Centaur', 17, 'bold')
    entry_app_name.configure(font=entry_app_name_style)
    # app_username text ---------------------------------------------------------------------------
    text_app_username = Label(frame, text="User Name", bg='#555454', fg='white', font=("Arial", 20))
    text_app_username.pack()
    text_app_username.place(x=20, y=65)
    text_app_username_style = ('Comic Sans Ms', 12, 'bold')
    text_app_username.configure(font=text_app_username_style)
    # app_username input ----------------------------------------------------------------------------
    entry_app_username = Entry(frame, width=20, font=("Arial", 33))
    entry_app_username.insert(0,app_username)
    entry_app_username.pack()
    entry_app_username.place(x=20, y=95)
    entry_app_username_style = ('Centaur', 17, 'bold')
    entry_app_username.configure(font=entry_app_username_style)
    # app_password text ---------------------------------------------------------------------------
    text_app_password = Label(frame, text="Password", bg='#555454', fg='white', font=("Arial", 20))
    text_app_password.pack()
    text_app_password.place(x=20, y=125)
    text_app_password_style = ('Comic Sans Ms', 12, 'bold')
    text_app_password.configure(font=text_app_password_style)
    # app_password input ----------------------------------------------------------------------------
    entry_app_password = Entry(frame, width=20, font=("Arial", 33))
    entry_app_password.insert(0, app_password)
    entry_app_password.pack()
    entry_app_password.place(x=20, y=155)
    entry_app_password_style = ('Centaur', 17, 'bold')
    entry_app_password.configure(font=entry_app_password_style)
    # app_description text ---------------------------------------------------------------------------
    text_app_description = Label(frame, text="Description", bg='#555454', fg='white', font=("Arial", 20))
    text_app_description.pack()
    text_app_description.place(x=20, y=185)
    text_app_description_style = ('Comic Sans Ms', 12, 'bold')
    text_app_description.configure(font=text_app_description_style)
    # app_description input ----------------------------------------------------------------------------
    entry_app_description = Entry(frame, width=20, font=("Arial", 33))
    entry_app_description.insert(0, app_description)
    entry_app_description.pack()
    entry_app_description.place(x=20, y=215)
    entry_app_description_style = ('Centaur', 17, 'bold')
    entry_app_description.configure(font=entry_app_description_style)
    # click button func -----------------------------------------------------------------
    def save_input():
        appname_input = entry_app_name.get()
        app_username_input = entry_app_username.get()
        app_password_input = entry_app_password.get()
        app_description_input = entry_app_description.get()
        key,encrypted_pass = encrypt_password(app_password_input)

        user_id = local_log(return_user_id=True)
        if user_id:
            sdc.update_table('Passwords',set={'app_name':appname_input,'app_username':app_username_input,
                                        'app_password':encrypted_pass,'password_key':key,
                                        'app_description':app_description_input},
                             conditions='id =? and user_id = ? and app_name = ? and app_username = ? and app_description = ?'
                             ,condition_values=(password_id,user_id,app_name,app_username,app_description))
        else:
            print('user id not found')

        on_closing()

    # add password button ---------------------------------------------------------------------------
    button_edit_password = Button(frame, text='Save', width=15, bg='green', fg='white', font=("Arial", 20),command=save_input)
    button_edit_password.pack()
    button_edit_password.place(x=20, y=265)
    button_edit_password_style = ('Centaur', 17, 'bold')
    button_edit_password.configure(font=button_edit_password_style)

    # on closing ---------------------------------------------------------------------------------
    def on_closing():
        refresh_command()
        window_edit_password.destroy()

    # Bind the window close event to `on_closing` function
    window_edit_password.protocol("WM_DELETE_WINDOW", on_closing)
    window_edit_password.mainloop()

#=======================MAIN===========================


if is_logged_in():
    passwords()
else:
    main_window()
