import sqlite3
import string
import random
import qrcode
from urllib.request import urlopen
from tkinter import *
import tkinter.messagebox
from tktimepicker import AnalogPicker, AnalogThemes, constants
from PIL import Image, ImageTk

def generate_pnr():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def generate_qrcode(text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("boarding_pass_qr.png")




def display_qrcode():

    qr_window = Toplevel(root)
    qr_window.iconphoto(False, PhotoImage(file='icon.png'))
    qr_window.title("QR Code")
    image_path = "boarding_pass_qr.png"
    image = image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    image_label = Label(root, image=photo)
    image_label.grid(row=0, column=0)



def connect_db():
    conn = sqlite3.connect('boarding_passes.db')
    return conn, conn.cursor()

def updateTime(time):
    time_lbl.configure(text="{}{}".format(*time)) # remove 3rd flower bracket in case of 24 hrs time
    
def get_time():

    top = Toplevel(root)
    top.iconphoto(False, PhotoImage(file='clock_icon.png'))
    top.title("Time Picker")

    time_picker = AnalogPicker(top, type=constants.HOURS24)
    time_picker.pack(expand=True, fill="both")

    theme = AnalogThemes(time_picker)
    ok_btn = Button(top, text="Okay", command=lambda: updateTime(time_picker.time()))
    ok_btn.pack()

def check_in(conn, c, entries):
    name, phone_number, airline, flight_number, departure_airport, arrival_airport, departure_time = (e.get() for e in entries)

    pnr = generate_pnr()
    try:
        c.execute('''INSERT INTO boarding_passes (name, phone_number, airline, flight_number, departure_airport, arrival_airport, departure_time, pnr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, phone_number, airline, flight_number, departure_airport, arrival_airport, departure_time, pnr))
        conn.commit()

        message = f"\nCheck-in successful! Your PNR is: {pnr}"
        tkinter.messagebox.showinfo("PNR generated successfuly", message)


    except sqlite3.IntegrityError:
        message = f"\nCheck-in failed! Phone number {phone_number} is already checked in."
        tkinter.messagebox.showerror("Check-in failed", message)
    

def print_boarding_pass(conn, c, pnr_entry):
    pnr = pnr_entry.get()

    c.execute('''SELECT * FROM boarding_passes WHERE pnr = ?''', (pnr,))
    data = c.fetchone()

    if not data:
        print("Invalid PNR. Please try again.")
        return

    openNewWindow(data)


def openNewWindow(data: tuple):

    # Toplevel object which will 
    # be treated as a new window
    newWindow = Toplevel(root)
   
    newWindow.iconphoto(False, PhotoImage(file='icon.png'))
    # sets the title of the
    # Toplevel widget
    newWindow.title("Pass")
 
    # sets the geometry of toplevel
    newWindow.geometry("220x240")
    
    # A Label widget to show in toplevel
    Label(newWindow, text="Name: ").grid(row=0, column=0)
    Label(newWindow, text="PNR: ").grid(row=1, column=0)
    Label(newWindow, text="Airline: ").grid(row=2, column=0)
    Label(newWindow, text="Flight number: ").grid(row=3, column=0)
    Label(newWindow, text="").grid(row=4, column=0)
    Label(newWindow, text="Boarding Time: ").grid(row=5, column=0)
    Label(newWindow, text="Departure Airport: ").grid(row=6, column=0)
    Label(newWindow, text="Arrival Airport: ").grid(row=7, column=0)
    Label(newWindow, text="").grid(row=8, column=0)


    text=f'''Passenger Mr./Ms. {data[0]} with PNR number {data[7]} travelling via {data[2]} flight number {data[3]} departing from {data[4]} airport to {data[5]} airport at {data[6]} hrs.
    \nPlease note that boarding begins at {data[6]-100} hrs and closes 20 minutes before departure.\nHave a safe journey!'''

    Button(newWindow, text="  Generate QR  ", command=lambda: generate_qrcode(text)).grid(row=9, column=0)
    Button(newWindow, text="     Show QR     ", command=lambda: Image.open('boarding_pass_qr.png').show()).grid(row=9, column=1)
 



    '''
    #Creating gap
    Label(newWindow, text="\t").grid(row=0, column=1)
    Label(newWindow, text="\t").grid(row=1, column=1)
    Label(newWindow, text="\t").grid(row=2, column=1)
    Label(newWindow, text="\t").grid(row=3, column=1)
    Label(newWindow, text="\t").grid(row=4, column=1)
    Label(newWindow, text="\t").grid(row=5, column=1)
    Label(newWindow, text="\t").grid(row=6, column=1)
    Label(newWindow, text="\t").grid(row=7, column=1)
    '''
     # A Label widget to show in toplevel
    Label(newWindow, text=f"{data[0]}").grid(row=0, column=1)
    Label(newWindow, text=f"{data[7]}").grid(row=1, column=1)
    Label(newWindow, text=f"{data[2]}").grid(row=2, column=1)
    Label(newWindow, text=f"{data[3]}").grid(row=3, column=1)
    Label(newWindow, text="").grid(row=4, column=1)
    Label(newWindow, text=f"{data[6]-100} hrs").grid(row=5, column=1)
    Label(newWindow, text=f"{data[4]}").grid(row=6, column=1)
    Label(newWindow, text=f"{data[5]}").grid(row=7, column=1)



def create_table(conn, c):
    # Define table schema with data types
    c.execute('''CREATE TABLE IF NOT EXISTS boarding_passes (
              name TEXT,
              phone_number TEXT PRIMARY KEY,
              airline TEXT,
              flight_number TEXT,
              departure_airport TEXT,
              arrival_airport TEXT,
              departure_time NUMBER,
              pnr TEXT
)''')

    conn.commit()

if __name__ == "__main__":
    conn, c = connect_db()
    create_table(conn, c)  # Create table if it doesn't exist

    root = Tk()
    root.title("Boarding Pass Generator")
    root.iconphoto(False, PhotoImage(file='icon.png'))

    Label(root, text="Enter your name: ").grid(row=0)
    Label(root, text="Enter phone number: ").grid(row=1)
    Label(root, text="Enter airline: ").grid(row=2)
    Label(root, text="Enter flight number: ").grid(row=3)
    Label(root, text=" Enter departure airport (e.g., Bangalore (BLR)): ").grid(row=4)
    Label(root, text=" Enter arrival airport (e.g., Delhi (DEL)): ").grid(row=5)
    Label(root, text="Choose flight departure time: ").grid(row=6)
   

    entries = [Entry(root) for _ in range(7)]
    for i, entry in enumerate(entries):
        entry.grid(row=i, column=1)
    
    
    time = ()
    time_lbl = Label(root)
    time_btn = Button(root, text="Get Time", command=get_time)
    time_lbl.grid(row=7, column=1)
    time_btn.grid(row=7, column=0)
    

    Button(root, text='  Click to Check In  ', command=lambda: check_in(conn, c, entries)).grid(row=8, column=1, sticky=W, pady=4)

    Label(root, text="Enter your PNR: ").grid(row=9)
    pnr_entry = Entry(root)
    pnr_entry.grid(row=9, column=1)
    Button(root, text='Print Boarding Pass', command=lambda: print_boarding_pass(conn, c, pnr_entry)).grid(row=10, column=1, sticky=W, pady=4)


    mainloop()
