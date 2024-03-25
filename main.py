import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkcalendar import Calendar
import sqlite3

# ======================================================================================================================
# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('pharmacy_inventory.db')
cursor = conn.cursor()


# Function to create the table if it doesn't exist
def create_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dosage TEXT,
        form TEXT,
        manufacturer TEXT,
        stock INTEGER,
        expiry_date TEXT,
        reorder_point INTEGER,
        price REAL
    )""")
    conn.commit()
create_table()  # Call the function to create the table

# create patients table
def create_patients_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        phone_number TEXT,
        allergies TEXT
    )""")
    conn.commit()
create_patients_table()  # Call the function to create the table


# create prescriptions table
def create_prescriptions_table():
    cursor.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        medicine_id INTEGER,
        dosage TEXT,
        frequency TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id),
        FOREIGN KEY (medicine_id) REFERENCES medicines(id)
    )""")
    conn.commit()
create_prescriptions_table()  # Call the function to create the table

#======================================================================================================================

# Function to add a new medicine to the database
def add_medicine_window(medicine_treeview):
    medicine_window = tk.Toplevel(window)  # Create a new top-level window
    medicine_window.title("Add Medicine")  # Set the window title

    # Create labels and entry fields for medicine details
    tk.Label(medicine_window, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    name_entry = tk.Entry(medicine_window)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Dosage:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    dosage_entry = tk.Entry(medicine_window)
    dosage_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Form:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    form_entry = tk.Entry(medicine_window)
    form_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Manufacturer:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    manufacturer_entry = tk.Entry(medicine_window)
    manufacturer_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Stock:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    stock_entry = tk.Entry(medicine_window)
    stock_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Expiry Date (YYYY-MM-DD):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    expiry_date_entry = tk.Entry(medicine_window)
    expiry_date_entry.grid(row=5, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Reorder Point:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    reorder_point_entry = tk.Entry(medicine_window)
    reorder_point_entry.grid(row=6, column=1, padx=5, pady=5)

    tk.Label(medicine_window, text="Price:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    price_entry = tk.Entry(medicine_window)
    price_entry.grid(row=7, column=1, padx=5, pady=5)

    # Button to save the new medicine
    save_button = tk.Button(medicine_window, text="Save Medicine", command=lambda: add_medicine(
        name_entry.get(), dosage_entry.get(), form_entry.get(), manufacturer_entry.get(),
        int(stock_entry.get()), expiry_date_entry.get(), int(reorder_point_entry.get()), float(price_entry.get())
    ))
    save_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    # call the function to Update the display frame after adding the medicine
    update_medicine_display(medicine_treeview)

    # Focus on the first entry field
    name_entry.focus_set()

    # Run the main loop for the new window
    medicine_window.mainloop()


def add_medicine(name, dosage, form, manufacturer, stock, expiry_date, reorder_point, price):
    try:
        # Insert new medicine data into the database
        cursor.execute("""INSERT INTO medicines (name, dosage, form, manufacturer, stock, expiry_date, reorder_point, 
            price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                       (name, dosage, form, manufacturer, stock, expiry_date, reorder_point, price))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while saving the medicine to the database.")


# function to Update the display frame after adding the medicine
def update_medicine_display(medicine_treeview):
    # Clear existing rows in the Treeview
    # Fetch updated list of medicines from the database
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()

    # Insert each medicine into the Treeview
    for medicine in medicines:
        medicine_treeview.insert('', 'end', values=medicine)


# Function to delete a selected medicine
def delete_selected_medicine(medicine_treeview):
    try:
        # Get the selected medicine ID
        selected_item = medicine_treeview.selection()[0]  # Get selected item
        selected_medicine_id = medicine_treeview.item(selected_item, 'values')[0]  # Get the ID from the item's values

        if selected_medicine_id is not None:  # Check if a medicine is selected
            # Confirmation prompt before deletion
            confirmation = tk.messagebox.askquestion("Confirm Delete", "Are you sure you want to delete this medicine?")

            if confirmation == 'yes':
                try:
                    # Delete medicine data from the database based on ID
                    cursor.execute("""DELETE FROM medicines WHERE id = ?""", (selected_medicine_id,))
                    conn.commit()

                    # Update the display frame after deleting the medicine
                    update_medicine_display(medicine_treeview)
                except sqlite3.Error as err:
                    tk.messagebox.showerror("Error", f"Error deleting medicine: {err}")
        else:
            tk.messagebox.showinfo("Error", "Please select a medicine to delete.")
    except IndexError:
        tk.messagebox.showinfo("Error", "Please select a medicine to delete.")


def edit_selected_medicine(medicine_treeview):
    # function to edit selected medicine
    # Get the selected medicine ID
    try:
        selected_item = medicine_treeview.selection()[0]  # Get selected item
        selected_medicine_id = medicine_treeview.item(selected_item, 'values')[0]  # Get the ID from the item's values

        if selected_medicine_id:  # Check if a medicine is selected
            # Fetch current details of the medicine from the database
            cursor.execute("SELECT * FROM medicines WHERE id = ?", (selected_medicine_id,))
            medicine = cursor.fetchone()

            # Open a new window with entry fields pre-filled with the current details of the medicine
            edit_medicine_window = tk.Toplevel(window)  # Create a new top-level window
            edit_medicine_window.title("Edit Medicine")  # Set the window title

            # Create labels and entry fields for medicine details, pre-filled with current details
            tk.Label(edit_medicine_window, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            name_entry = tk.Entry(edit_medicine_window)
            name_entry.insert(0, medicine[1])  # Fill the entry field with the current name
            name_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Dosage:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            dosage_entry = tk.Entry(edit_medicine_window)
            dosage_entry.insert(0, medicine[2])  # Fill the entry field with the current dosage
            dosage_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Form:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            form_entry = tk.Entry(edit_medicine_window)
            form_entry.insert(0, medicine[3])  # Fill the entry field with the current form
            form_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Manufacturer:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            manufacturer_entry = tk.Entry(edit_medicine_window)
            manufacturer_entry.insert(0, medicine[4])  # Fill the entry field with the current manufacturer
            manufacturer_entry.grid(row=3, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Stock:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
            stock_entry = tk.Entry(edit_medicine_window)
            stock_entry.insert(0, medicine[5])  # Fill the entry field with the current stock
            stock_entry.grid(row=4, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Expiry Date (YYYY-MM-DD):").grid(row=5, column=0, sticky="w", padx=5,
                                                                                  pady=5)
            expiry_date_entry = tk.Entry(edit_medicine_window)
            expiry_date_entry.insert(0, medicine[6])  # Fill the entry field with the current expiry date
            expiry_date_entry.grid(row=5, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Reorder Point:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
            reorder_point_entry = tk.Entry(edit_medicine_window)
            reorder_point_entry.insert(0, medicine[7])  # Fill the entry field with the current reorder point
            reorder_point_entry.grid(row=6, column=1, padx=5, pady=5)

            tk.Label(edit_medicine_window, text="Price:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
            price_entry = tk.Entry(edit_medicine_window)
            price_entry.insert(0, medicine[8])  # Fill the entry field with the current price
            price_entry.grid(row=7, column=1, padx=5, pady=5)

            # Button to save the changes
            save_button = tk.Button(edit_medicine_window, text="Save Changes", command=lambda: update_medicine(
                selected_medicine_id,
                name_entry.get(), dosage_entry.get(), form_entry.get(), manufacturer_entry.get(),
                int(stock_entry.get()), expiry_date_entry.get(), int(reorder_point_entry.get()),
                float(price_entry.get()),
                medicine_treeview))
            save_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

            # Run the main loop for the new window
            edit_medicine_window.mainloop()
        else:
            tk.messagebox.showinfo("Error", "Please select a medicine to edit.")
    except IndexError:
        tk.messagebox.showinfo("Error", "Please select a medicine to edit.")


def update_medicine(id, name, dosage, form, manufacturer, stock, expiry_date, reorder_point, price,
                    medicine_treeview):
    try:
        # Update medicine data in the database
        cursor.execute(
            """UPDATE medicines SET name = ?, dosage = ?, form = ?, manufacturer = ?, stock = ?, expiry_date = ?, 
            reorder_point = ?, price = ? WHERE id = ?""",
            (name, dosage, form, manufacturer, stock, expiry_date, reorder_point, price, id))
        conn.commit()

        # Update the display frame after editing the medicine
        update_medicine_display(medicine_treeview)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while updating the medicine in the database.")


def populate_treeview(medicine_treeview):
    # Clear existing rows in the Treeview

    # Fetch all medicines from the database
    cursor.execute("SELECT * FROM medicines")
    medicines = cursor.fetchall()

    # Insert each medicine into the Treeview
    for medicine in medicines:
        medicine_treeview.insert('', 'end', values=medicine)


def inventory_window():
    # Create left frame for medication details
    left_frame = tk.LabelFrame(window, text="Medicine Details", bd=5, width=200, height=150)
    left_frame.pack(side="top", fill="both", expand=False)

    left_frame0 = tk.LabelFrame(left_frame, text="", bd=2, width=200, height=150)
    left_frame0.grid(row=0, column=0, padx=15, pady=15)

    # Create a frame for the control buttons inside the left frame
    control_frame = tk.Frame(left_frame0)
    control_frame.pack(side="bottom")

    # Create the control buttons
    add_button = tk.Button(control_frame, text="Add Medicine", command=lambda: add_medicine_window(medicine_treeview))
    add_button.pack(side="left", padx=5, pady=5)

    edit_button = tk.Button(control_frame, text="Edit", command=lambda: edit_selected_medicine(medicine_treeview))
    edit_button.pack(side="left", padx=5, pady=5)

    delete_button = tk.Button(control_frame, text="Delete", command=lambda: delete_selected_medicine(medicine_treeview))
    delete_button.pack(side="left", padx=5, pady=5)

    save_button = tk.Button(control_frame, text="Save")
    save_button.pack(side="left", padx=5, pady=5)

    exit_button = tk.Button(control_frame, text="Exit")
    exit_button.pack(side="left", padx=5, pady=5)

    # Create a frame for the fields
    fields_frame = tk.Frame(left_frame0)
    fields_frame.pack(pady=10)

    # Create aframe to display added medicines
    display_frame = tk.LabelFrame(window, text="Display medicine", bd=5, width=600, height=450, relief=tk.RIDGE)
    display_frame.pack(side="top", fill="both", expand=True)

    # Create the medicine list treeview
    medicine_columns = ["ID", "Name", "Dosage", "Form", "Manufacturer", "Stock", "Expiry Date", "Reorder Point",
                        "Price"]
    medicine_treeview = ttk.Treeview(display_frame, columns=medicine_columns, show="headings", style="mystyle.Treeview")
    for col in medicine_columns:
        medicine_treeview.heading(col, text=col)
        medicine_treeview.column(col, width=100, anchor="center")
    medicine_treeview.pack(side="left", fill="both", expand=True)

    # Configure style to add lines between columns
    style = ttk.Style()
    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Helvetica', 10), rowheight=25)
    style.configure("mystyle.Treeview.Heading", font=('Helvetica', 10, 'bold'))
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

    # Create the scrollbar for the treeview
    scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=medicine_treeview.yview)
    scrollbar.pack(side="right", fill="y")
    medicine_treeview.configure(yscrollcommand=scrollbar.set)


def exit_window():
    # Close the database connection and destroy the window
    conn.close()
    window.destroy()


# ======================================================================================================================


def update_patients_display(patients_treeview):
    try:
        # Clear existing rows in the Treeview
        for row in patients_treeview.get_children():
            patients_treeview.delete(row)
        # Fetch all patients from the database
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        # Insert each patient into the Treeview
        for patient in patients:
            patients_treeview.insert('', 'end', values=patient)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while fetching patients from the database.")

def add_patient_from_input(patients_name_entry, patients_address_entry, patients_phone_number_entry, patients_allergies_entry, patients_treeview):
    # Get the information from the entry fields
    name = patients_name_entry.get()
    address = patients_address_entry.get()
    phone_number = patients_phone_number_entry.get()
    allergies = patients_allergies_entry.get()

    try:
        # Insert new patient data into the database
        cursor.execute("""INSERT INTO patients (name, address, phone_number, allergies)
                        VALUES (?, ?, ?, ?)""", (name, address, phone_number, allergies))
        conn.commit()
        # Update the display frame after adding the patient
        update_patients_display(patients_treeview)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while adding the patient to the database.")


def update_patient(selected_patient_id, param, param1, param2, param3, patients_treeview):
    # Update patient data in the database
    try:
        cursor.execute("""UPDATE patients SET name = ?, address = ?, phone_number = ?, allergies = ? WHERE id = ?""",
                       (param, param1, param2, param3, selected_patient_id))
        conn.commit()
        # Update the display frame after editing the patient
        update_patients_display(patients_treeview)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while updating the patient in the database.")


def edit_patient(patients_treeview):
    try:
        # Get the selected patient ID
        selected_item = patients_treeview.selection()[0]  # Get selected item
        selected_patient_id = patients_treeview.item(selected_item, 'values')[0]  # Get the ID from the item's values

        if selected_patient_id:  # Check if a patient is selected
            # Fetch current details of the patient from the database
            cursor.execute("SELECT * FROM patients WHERE id = ?", (selected_patient_id,))
            patient = cursor.fetchone()

            # Open a new window with entry fields pre-filled with the current details of the patient
            edit_patient_window = tk.Toplevel(window)  # Create a new top-level window
            edit_patient_window.title("Edit Patient")  # Set the window title

            # Create labels and entry fields for patient details, pre-filled with current details
            tk.Label(edit_patient_window, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            name_entry = tk.Entry(edit_patient_window)
            name_entry.insert(0, patient[1])  # Fill the entry field with the current name
            name_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(edit_patient_window, text="Address:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            address_entry = tk.Entry(edit_patient_window)
            address_entry.insert(0, patient[2])  # Fill the entry field with the current address
            address_entry.grid(row=1, column=1, padx=5, pady=5)

            tk.Label(edit_patient_window, text="Phone Number:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            phone_number_entry = tk.Entry(edit_patient_window)
            phone_number_entry.insert(0, patient[3])  # Fill the entry field with the current phone number
            phone_number_entry.grid(row=2, column=1, padx=5, pady=5)

            tk.Label(edit_patient_window, text="Allergies:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
            allergies_entry = tk.Entry(edit_patient_window)
            allergies_entry.insert(0, patient[4])  # Fill the entry field with the current allergies
            allergies_entry.grid(row=3, column=1, padx=5, pady=5)

            # Button to save the changes
            save_button = tk.Button(edit_patient_window, text="Save Changes", command=lambda: update_patient(
                selected_patient_id,
                name_entry.get(), address_entry.get(), phone_number_entry.get(), allergies_entry.get(),
                patients_treeview))
            save_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

            # Run the main loop for the new window
            edit_patient_window.mainloop()
        else:
            tk.messagebox.showinfo("Error", "Please select a patient to edit.")
    except IndexError:
        tk.messagebox.showinfo("Error", "Please select a patient to edit.")

def delete_patient(patients_treeview):
    try:
        # Get the selected patient ID
        selected_item = patients_treeview.selection()[0]  # Get selected item
        selected_patient_id = patients_treeview.item(selected_item, 'values')[0]  # Get the ID from the item's values

        if selected_patient_id:  # Check if a patient is selected
            # Confirmation prompt before deletion
            confirmation = tk.messagebox.askquestion("Confirm Delete", "Are you sure you want to delete this patient?")

            if confirmation == 'yes':
                try:
                    # Delete patient data from the database based on ID
                    cursor.execute("""DELETE FROM patients WHERE id = ?""", (selected_patient_id,))
                    conn.commit()

                    # Update the display frame after deleting the patient
                    update_patients_display(patients_treeview)
                except sqlite3.Error as err:
                    tk.messagebox.showerror("Error", f"Error deleting patient: {err}")
        else:
            tk.messagebox.showinfo("Error", "Please select a patient to delete.")
    except IndexError:
        tk.messagebox.showinfo("Error", "Please select a patient to delete.")
def search_patient(search_term, patients_treeview):
    # Perform search logic and update the treeview with the search results
    # This function should fetch the matching patients from the database and update the treeview
    pass


def clear_input_fields(patients_name_entry, patients_address_entry, patients_phone_number_entry, patients_allergies_entry):
    # Logic to clear the patient details fields
    patients_name_entry.delete(0, tk.END)
    patients_address_entry.delete(0, tk.END)
    patients_phone_number_entry.delete(0, tk.END)
    patients_allergies_entry.delete(0, tk.END)

def patients_window():
    patients_window1 = tk.Toplevel(window)
    patients_window1.title("Patients")
    patients_window1.geometry("800x600")

    # Create the top frame for the search bar and buttons
    top_frame1 = tk.LabelFrame(patients_window1, bd=5)
    top_frame1.pack(side="top", fill="x")

    # Create the search bar
    search_label = tk.Label(top_frame1, text="Search:")
    search_label.grid(row=0, column=0, padx=5, pady=5)
    search_entry = tk.Entry(top_frame1)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    # Create the search button
    search_button = tk.Button(top_frame1,
                              text="Search", command=lambda: search_patient(search_entry.get(), patient_treeview))
    search_button.grid(row=0, column=2, padx=5, pady=5)

    # create frame to add patients details
    frame1 = tk.LabelFrame(patients_window1, text="Patients Details", bd=5)
    frame1.pack(side="top", fill="both", expand=False)

    patientsframe = tk.Frame(frame1)
    patientsframe.pack(side="left")

    # Create labels and entry fields for each field
    patients_name = tk.Label(patientsframe, text="Name:")
    patients_name.grid(row=0, column=0, padx=5, pady=5)
    patients_name_entry = tk.Entry(patientsframe)
    patients_name_entry.grid(row=0, column=1, padx=5, pady=5)

    patients_address = tk.Label(patientsframe, text="Address:")
    patients_address.grid(row=1, column=0, padx=5, pady=5)
    patients_address_entry = tk.Entry(patientsframe)
    patients_address_entry.grid(row=1, column=1, padx=5, pady=5)

    patients_phone_number = tk.Label(patientsframe, text="Phone Number:")
    patients_phone_number.grid(row=2, column=0, padx=5, pady=5)
    patients_phone_number_entry = tk.Entry(patientsframe)
    patients_phone_number_entry.grid(row=2, column=1, padx=5, pady=5)

    # Create labels and entry fields for patients allergies
    patients_allergies = tk.Label(patientsframe, text="Allergies:")
    patients_allergies.grid(row=3, column=0, padx=5, pady=5)
    patients_allergies_entry = tk.Entry(patientsframe)
    patients_allergies_entry.grid(row=3, column=1, padx=5, pady=5)

    # create a control frame for the buttons
    control_frame1 = tk.Frame(frame1)
    control_frame1.pack(side="bottom")

    # Create the add patient button
    add_patient_button = tk.Button(control_frame1, text="Add Patient", command=lambda: add_patient_from_input(
                                                patients_name_entry, patients_address_entry, patients_phone_number_entry,
                                                patients_allergies_entry, patient_treeview))
    add_patient_button.grid(row=0, column=3, padx=5, pady=5)

    # Create the edit patient button
    edit_patient_button = tk.Button(control_frame1, text="Edit Patient", command=lambda: edit_patient(patient_treeview))
    edit_patient_button.grid(row=0, column=4, padx=5, pady=5)

    # Create the delete patient button
    delete_patient_button = tk.Button(control_frame1, text="Delete Patient", command=lambda: delete_patient(patient_treeview))
    delete_patient_button.grid(row=0, column=5, padx=5, pady=5)

    # Create the save patient button
    save_patient_button = tk.Button(control_frame1, text="clear", command=lambda: clear_input_fields(patients_name_entry,
                                patients_address_entry, patients_phone_number_entry, patients_allergies_entry))
    save_patient_button.grid(row=0, column=6, padx=5, pady=5)

    # Create the exit patient button
    exit_patient_button = tk.Button(control_frame1, text="Exit")
    exit_patient_button.grid(row=0, column=7, padx=5, pady=5, sticky="s")

    # Create the patient list frame
    patient_list_frame = tk.LabelFrame(patients_window1, text="Patients List", bd=5)
    patient_list_frame.pack(side="top", fill="both", expand=True)

    # Create the patient list treeview
    patients_columns = ["ID", "Name", "Address", "Phone Number", "Allergies"]
    patient_treeview = ttk.Treeview(patient_list_frame, columns=patients_columns,
                                    show="headings", style="mystyle.Treeview")
    for col in patients_columns:
        patient_treeview.heading(col, text=col)
        patient_treeview.column(col, width=100, anchor="center")
    patient_treeview.pack(side="left", fill="both", expand=True)

    # Configure style to add lines between columns
    style = ttk.Style()
    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Helvetica', 10), rowheight=25)
    style.configure("mystyle.Treeview.Heading", font=('Helvetica', 10, 'bold'))
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

    # Create the scrollbar for the treeview
    scrollbar = ttk.Scrollbar(patient_list_frame, orient="vertical", command=patient_treeview.yview)
    scrollbar.pack(side="right", fill="y")
    patient_treeview.configure(yscrollcommand=scrollbar.set)

    # populate the treeview with patients
    update_patients_display(patient_treeview)


# ======================================================================================================================
def add_prescription(patient_id, medicine_id, dosage, frequency, start_date, end_date, prescription_treeview):
    try:
        # Insert new prescription data into the database
        cursor.execute("""INSERT INTO prescriptions (patient_id, medicine_id, dosage, frequency, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?)""", (patient_id, medicine_id, dosage, frequency, start_date, end_date))
        conn.commit()
        # Update the display frame after adding the prescription
        update_prescription_display(prescription_treeview)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while saving the prescription to the database.")

def update_prescription_display(prescription_treeview):
    try:
        # Clear existing rows in the Treeview
        for row in prescription_treeview.get_children():
            prescription_treeview.delete(row)
        # Fetch all prescriptions from the database
        cursor.execute("SELECT * FROM prescriptions")
        prescriptions = cursor.fetchall()
        # Insert each prescription into the Treeview
        for prescription in prescriptions:
            prescription_treeview.insert('', 'end', values=prescription)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        tk.messagebox.showerror("Error", "An error occurred while fetching prescriptions from the database.")

def delete_selected_prescription(prescription_treeview):
    try:
        # Get the selected prescription ID
        selected_item = prescription_treeview.selection()[0]  # Get selected item
        selected_prescription_id = prescription_treeview.item(selected_item, 'values')[0]  # Get the ID from the item's values

        if selected_prescription_id:  # Check if a prescription is selected
            # Confirmation prompt before deletion
            confirmation = tk.messagebox.askquestion("Confirm Delete", "Are you sure you want to delete this prescription?")

            if confirmation == 'yes':
                try:
                    # Delete the prescription from the database
                    cursor.execute("DELETE FROM prescriptions WHERE id = ?", (selected_prescription_id,))
                    conn.commit()
                    # Update the display frame after deleting the prescription
                    update_prescription_display(prescription_treeview)
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                    tk.messagebox.showerror("Error", "An error occurred while deleting the prescription from the database.")
        else:
            tk.messagebox.showinfo("Error", "Please select a prescription to delete.")
    except IndexError:
        tk.messagebox.showinfo("Error", "Please select a prescription to delete.")

def clear_prescription_input_fields(patient_id_entry, medicine_id_entry, dosage_entry,
                                    frequency_entry, start_date_entry, end_date_entry):
    # function clears the input fields
    patient_id_entry.delete(0, tk.END)
    medicine_id_entry.delete(0, tk.END)
    dosage_entry.delete(0, tk.END)
    frequency_entry.delete(0, tk.END)
    start_date_entry.delete(0, tk.END)
    end_date_entry.delete(0, tk.END)
def prescription_window():
    prescription_window1 = tk.Toplevel(window)
    prescription_window1.title("Prescriptions")
    prescription_window1.geometry("800x600")

    # Create the top frame for the search bar and buttons
    ptop_frame = tk.LabelFrame(prescription_window1, text="Search", bd=5)
    ptop_frame.pack(side="top", fill="x")

    # Create the search bar
    search_label = tk.Label(ptop_frame, text="Search:")
    search_label.grid(row=0, column=0, padx=5, pady=5)
    search_entry = tk.Entry(ptop_frame)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    # Create the search button
    search_button = tk.Button(ptop_frame, text="Search")
    search_button.grid(row=0, column=2, padx=5, pady=5)

    # Create the middle frame for prescription details
    middle_frame = tk.LabelFrame(prescription_window1, text="Prescription Details", bd=5)
    middle_frame.pack(side="top", fill="x")

    # Create labels and entry fields for each field
    patient_id_label = tk.Label(middle_frame, text="Patient ID:")
    patient_id_label.grid(row=0, column=0, padx=5, pady=5)
    patient_id_entry = tk.Entry(middle_frame)
    patient_id_entry.grid(row=0, column=1, padx=5, pady=5)

    medicine_id_label = tk.Label(middle_frame, text="Medicine ID:")
    medicine_id_label.grid(row=1, column=0, padx=5, pady=5)
    medicine_id_entry = tk.Entry(middle_frame)
    medicine_id_entry.grid(row=1, column=1, padx=5, pady=5)

    dosage_lbl = tk.Label(middle_frame, text="Dosage:")
    dosage_lbl.grid(row=2, column=0, padx=5, pady=5)
    ddosage_entry = tk.Entry(middle_frame)
    ddosage_entry.grid(row=2, column=1, padx=5, pady=5)

    frequency_label = tk.Label(middle_frame, text="Frequency:")
    frequency_label.grid(row=3, column=0, padx=5, pady=5)
    frequency_entry = tk.Entry(middle_frame)
    frequency_entry.grid(row=3, column=1, padx=5, pady=5)

    start_date_label = tk.Label(middle_frame, text="Start Date:")
    start_date_label.grid(row=4, column=0, padx=5, pady=5)
    start_date_entry = tk.Entry(middle_frame)
    start_date_entry.grid(row=4, column=1, padx=5, pady=5)

    end_date_label = tk.Label(middle_frame, text="End Date:")
    end_date_label.grid(row=5, column=0, padx=5, pady=5)
    end_date_entry = tk.Entry(middle_frame)
    end_date_entry.grid(row=5, column=1, padx=5, pady=5)

    # Create the add prescription button
    add_prescription_button = tk.Button(middle_frame, text="Add Prescription", command=lambda: add_prescription(
        patient_id_entry.get(), medicine_id_entry.get(), ddosage_entry.get(), frequency_entry.get(),
        start_date_entry.get(), end_date_entry.get(), prescription_treeview))
    add_prescription_button.grid(row=6, column=0, padx=5, pady=5)

    # Create the delete prescription button
    delete_prescription_button = tk.Button(middle_frame, text="Delete Prescription", command=lambda: delete_selected_prescription(prescription_treeview))
    delete_prescription_button.grid(row=6, column=1, padx=5, pady=5)

    # Create the edit prescription button
    edit_prescription_button = tk.Button(middle_frame, text="Edit Prescription")
    edit_prescription_button.grid(row=6, column=2, padx=5, pady=5)

    # Create the save prescription button
    clear_prescription_input_button = tk.Button(middle_frame, text="clear",
                                                command=lambda: clear_prescription_input_fields(
                                                patient_id_entry, medicine_id_entry, ddosage_entry,
                                                frequency_entry, start_date_entry, end_date_entry))
    clear_prescription_input_button.grid(row=6, column=3, padx=5, pady=5)

    # Create the prescription list frame
    prescription_list_frame = tk.LabelFrame(prescription_window1, text="Prescription List", bd=5)
    prescription_list_frame.pack(side="top", fill="both", expand=True)

    # Create the prescription list treeview
    columns = ["ID", "Patient ID", "Medicine_id", "Dosage", "Frequency", "start date", "End date"]
    prescription_treeview = ttk.Treeview(prescription_list_frame, columns=columns,
                                         show="headings", style="mystyle.Treeview")
    for col in columns:
        prescription_treeview.heading(col, text=col)
        prescription_treeview.column(col, width=100, anchor="center")
    prescription_treeview.pack(side="left", fill="both", expand=True)

    # Configure style to add lines between columns
    style = ttk.Style()
    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Helvetica', 10), rowheight=25)
    style.configure("mystyle.Treeview.Heading", font=('Helvetica', 10, 'bold'))
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

    # Create the scrollbar for the treeview
    scrollbar = ttk.Scrollbar(prescription_list_frame, orient="vertical", command=prescription_treeview.yview)
    scrollbar.pack(side="right", fill="y")
    prescription_treeview.configure(yscrollcommand=scrollbar.set)


# ======================================================================================================================
def calculate_bill(prescription_id):
    try:
        # Fetch the prescription details from the database
        cursor.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
        prescription = cursor.fetchone()

        if prescription is not None:
            # Fetch the medicine details from the database
            cursor.execute("SELECT * FROM medicines WHERE id = ?", (prescription[2],))
            medicine = cursor.fetchone()

            if medicine is not None:
                # Calculate the total cost
                total_cost = medicine[8] * int(prescription[3])
                return total_cost
            else:
                print("Medicine not found.")
                return None
        else:
            print("Prescription not found.")
            return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
def billing_window():
    billing_window1 = tk.Toplevel(window)
    billing_window1.title("Billing")
    billing_window1.geometry("800x600")

    # Create the top frame for the search bar and buttons
    btop_frame = tk.LabelFrame(billing_window1, text="Search", bd=5)
    btop_frame.pack(side="top", fill="x")

    # Create the search bar
    search_label = tk.Label(btop_frame, text="Search:")
    search_label.grid(row=0, column=0, padx=5, pady=5)
    search_entry = tk.Entry(btop_frame)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    # Create the search button
    search_button = tk.Button(btop_frame, text="Search")
    search_button.grid(row=0, column=2, padx=5, pady=5)

    # Create the middle frame for billing details
    bmiddle_frame = tk.LabelFrame(billing_window1, text="Billing Details", bd=5)
    bmiddle_frame.pack(side="top", fill="x")

    # Create labels and entry fields for each field
    patient_id_label = tk.Label(bmiddle_frame, text="Patient ID:")
    patient_id_label.grid(row=0, column=0, padx=5, pady=5)
    patient_id_entry = tk.Entry(bmiddle_frame)
    patient_id_entry.grid(row=0, column=1, padx=5, pady=5)

    prescription_id_label = tk.Label(bmiddle_frame, text="Prescription Info:")
    prescription_id_label.grid(row=1, column=0, padx=5, pady=5)
    prescription_id_entry = tk.Entry(bmiddle_frame)
    prescription_id_entry.grid(row=1, column=1, padx=5, pady=5)

    total_cost_label = tk.Label(bmiddle_frame, text="Total Cost:")
    total_cost_label.grid(row=2, column=0, padx=5, pady=5)
    total_cost_entry = tk.Entry(bmiddle_frame)
    total_cost_entry.grid(row=2, column=1, padx=5, pady=5)

    # Create the calculate bill button
    calculate_bill_button = tk.Button(bmiddle_frame, text="Calculate Bill", command=lambda: calculate_bill(
        prescription_id_entry.get()))
    calculate_bill_button.grid(row=3, column=0, padx=5, pady=5)

    # Create the save bill button
    save_bill_button = tk.Button(bmiddle_frame, text="Save Bill")
    save_bill_button.grid(row=3, column=1, padx=5, pady=5)

    # Create the exit bill button
    exit_bill_button = tk.Button(bmiddle_frame, text="Exit")
    exit_bill_button.grid(row=3, column=2, padx=5, pady=5)

    # Create the billing list frame
    billing_list_frame = tk.LabelFrame(billing_window1, text="Billing List", bd=5)
    billing_list_frame.pack(side="right", fill="both", expand=True)



# ======================================================================================================================
# function for reports window
def reports_window():
    reportss_window = tk.Toplevel(window)
    reportss_window.title("Reports")
    reportss_window.geometry("800x600")

    # Create the top frame for report type selection and filtering options
    reports_top_frame = tk.LabelFrame(reportss_window, text="Select Report Type and Filter")
    reports_top_frame.pack(side="top", fill="x")

    # Report type selection
    ttk.Label(reports_top_frame, text="Select Report Type:").grid(row=0, column=0, padx=5, pady=5)
    report_type_combobox = ttk.Combobox(reports_top_frame, values=["patients Report", "Medicine Report", "Sales Report",
                                                                   "Inventory Report"], state="readonly")
    report_type_combobox.grid(row=0, column=1, padx=5, pady=5)

    # Filtering options
    ttk.Label(reports_top_frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5)
    start_date_entry = ttk.Entry(reports_top_frame)
    start_date_entry.grid(row=1, column=1, padx=5, pady=5)
    start_date_cal_button = ttk.Button(reports_top_frame, text="date?", command=lambda: select_date(start_date_entry))
    start_date_cal_button.grid(row=1, column=2, padx=5, pady=5)

    ttk.Label(reports_top_frame, text="End Date:").grid(row=1, column=3, padx=5, pady=5)
    end_date_entry = ttk.Entry(reports_top_frame)
    end_date_entry.grid(row=1, column=4, padx=5, pady=5)
    end_date_cal_button = ttk.Button(reports_top_frame, text="date?", command=lambda: select_date(end_date_entry))
    end_date_cal_button.grid(row=1, column=5, padx=5, pady=5)

    # Create the generate report button
    generate_report_button = ttk.Button(reports_top_frame, text="Generate Report",
                                        command=lambda: generate_report(report_type_combobox.get(),
                                                                        start_date_entry.get(), end_date_entry.get()))
    generate_report_button.grid(row=0, column=3, padx=5, pady=5, rowspan=2)

    # Function to open calendar
    def select_date(entry_widget):
        def set_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date)
            cal.destroy()

        cal = Calendar(reportss_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack()
        cal.place(relx=0.1, rely=0.3)
        cal.bind("<Button-1>", lambda event: set_date())

    # Placeholder function for generating report
    def generate_report(report_type, start_date, end_date):
        if report_type == "":
            messagebox.showerror("Error", "Please select a report type")
            return

        # Display a message with the selected report type and filtering options
        message = f"Generating {report_type} report"
        if start_date:
            message += f" from {start_date}"
        if end_date:
            message += f" to {end_date}"
        messagebox.showinfo("Generating Report", message)

    # Create the report display frame
    display_frame = tk.LabelFrame(reportss_window, text="Report Display", bd=5)
    display_frame.pack(side="top", fill="both", expand=True)

    # Create the report display table depending on selected report type


# ======================================================================================================================

# Create the main window
window = tk.Tk()
window.title("Pharmacy Inventory Manager")
window.geometry("800x600")

# Create top frame for buttons
top_frame = tk.LabelFrame(window, bd=3)
top_frame.pack(side="top", fill="x")

# Create the buttons in the top frame
inventory_button = tk.Button(top_frame, text="Inventory", command=inventory_window)
inventory_button.grid(row=0, column=0, padx=5, pady=5)

patients_button = tk.Button(top_frame, text="Patients", command=patients_window)
patients_button.grid(row=0, column=1, padx=5, pady=5)

prescriptions_button = tk.Button(top_frame, text="Prescriptions", command=prescription_window)
prescriptions_button.grid(row=0, column=2, padx=5, pady=5)

billing_button = tk.Button(top_frame, text="Billing", command=billing_window)
billing_button.grid(row=0, column=3, padx=5, pady=5)

reports_button = tk.Button(top_frame, text="Reports", command=reports_window)
reports_button.grid(row=0, column=4, padx=5, pady=5)
# ======================================================================================================================


if __name__ == "__main__":
    # Run the application
    window.mainloop()

