from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

Base = declarative_base()

# create a database engine
engine = create_engine('sqlite:///pharmacy.db', echo=True)
Base.metadata.create_all(engine)


class Medication(Base):
    __tablename__ = 'medications'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    strength = Column(String)
    stock_level = Column(Integer)
    expiry_date = Column(Date)
    reorder_point = Column(Integer)

class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True)
    medication_id = Column(Integer)
    patient_id = Column(Integer)
    quantity = Column(Integer)
    date_prescribed = Column(Date)

class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_of_birth = Column(Date)
    allergies = Column(String)

class Bill(Base):
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer)
    total_cost = Column(Float)
    date = Column(Date)

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer)
    amount = Column(Float)
    date = Column(Date)

class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)
    phone = Column(String)
    email = Column(String)

class Nurse(Base):
    __tablename__ = 'nurses'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)

# functions to interact with the database
from sqlalchemy.orm import Session

def add_medication(session: Session, name: str, strength: str, stock_level: int, expiry_date: Date, reorder_point: int):
    medication = Medication(name=name, strength=strength, stock_level=stock_level, expiry_date=expiry_date, reorder_point=reorder_point)
    session.add(medication)
    session.commit()

def edit_medication(session: Session, medication_id: int, name: str, strength: str, stock_level: int, expiry_date: Date, reorder_point: int):
    medication = session.query(Medication).filter(Medication.id == medication_id).first()
    if medication:
        medication.name = name
        medication.strength = strength
        medication.stock_level = stock_level
        medication.expiry_date = expiry_date
        medication.reorder_point = reorder_point
        session.commit()

def search_medication(session: Session, name: str):
    return session.query(Medication).filter(Medication.name.contains(name)).all()

def delete_medication(session: Session, medication_id: int):
    medication = session.query(Medication).filter(Medication.id == medication_id).first()
    if medication:
        session.delete(medication)
        session.commit()

def track_stock_levels(session: Session):
    return session.query(Medication.name, Medication.stock_level).all()

def track_expiry_dates(session: Session):
    return session.query(Medication.name, Medication.expiry_date).all()

def track_reorder_points(session: Session):
    return session.query(Medication.name, Medication.reorder_point).all()

def generate_inventory_report(session: Session):
    medications = session.query(Medication).all()
    report = []
    for medication in medications:
        report.append({
            'name': medication.name,
            'strength': medication.strength,
            'stock_level': medication.stock_level,
            'expiry_date': medication.expiry_date,
            'reorder_point': medication.reorder_point
        })
    return report

def generate_alerts(session: Session):
    alerts = []
    medications = session.query(Medication).all()
    for medication in medications:
        if medication.stock_level <= medication.reorder_point:
            alerts.append(f"Low stock alert for {medication.name}")
        if medication.expiry_date <= Date.today():
            alerts.append(f"Expired medication alert for {medication.name}")
    return alerts

# functions to manage prescriptions
def add_prescription(session: Session, medication_id: int, patient_id: int, quantity: int, date_prescribed: Date):
    prescription = Prescription(medication_id=medication_id, patient_id=patient_id, quantity=quantity, date_prescribed=date_prescribed)
    session.add(prescription)
    session.commit()

def verify_prescription(session: Session, prescription_id: int):
    prescription = session.query(Prescription).filter(Prescription.id == prescription_id).first()
    if prescription:
        medication = session.query(Medication).filter(Medication.id == prescription.medication_id).first()
        if medication and medication.stock_level >= prescription.quantity:
            return True
    return False

def get_patient_history(session: Session, patient_id: int):
    prescriptions = session.query(Prescription).filter(Prescription.patient_id == patient_id).all()
    history = []
    for prescription in prescriptions:
        medication = session.query(Medication).filter(Medication.id == prescription.medication_id).first()
        if medication:
            history.append({
                'medication_name': medication.name,
                'quantity': prescription.quantity,
                'date_prescribed': prescription.date_prescribed
            })
    return history

def get_patient_allergies(session: Session, patient_id: int):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        return patient.allergies

def generate_label(session: Session, prescription_id: int):
    prescription = session.query(Prescription).filter(Prescription.id == prescription_id).first()
    if prescription:
        medication = session.query(Medication).filter(Medication.id == prescription.medication_id).first()
        patient = session.query(Patient).filter(Patient.id == prescription.patient_id).first()
        if medication and patient:
            label = f"Patient: {patient.name}\nMedication: {medication.name}\nQuantity: {prescription.quantity}\nDate Prescribed: {prescription.date_prescribed}"
            return label

# function to manage patient profiles
def add_patient(session: Session, name: str, date_of_birth: Date, allergies: str):
    patient = Patient(name=name, date_of_birth=date_of_birth, allergies=allergies)
    session.add(patient)
    session.commit()

def edit_patient(session: Session, patient_id: int, name: str, date_of_birth: Date, allergies: str):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        patient.name = name
        patient.date_of_birth = date_of_birth
        patient.allergies = allergies
        session.commit()

def delete_patient(session: Session, patient_id: int):
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        session.delete(patient)
        session.commit()

def search_patient(session: Session, name: str):
    return session.query(Patient).filter(Patient.name.contains(name)).all()

# function to add bills and payments
def add_bill(session: Session, patient_id: int, total_cost: float, date: Date):
    bill = Bill(patient_id=patient_id, total_cost=total_cost, date=date)
    session.add(bill)
    session.commit()

def get_sales_report(session: Session):
    bills = session.query(Bill).all()
    sales_report = []
    for bill in bills:
        sales_report.append({
            'bill_id': bill.id,
            'patient_id': bill.patient_id,
            'total_cost': bill.total_cost,
            'date': bill.date
        })
    return sales_report

def get_costs_report(session: Session):
    medications = session.query(Medication).all()
    costs_report = []
    for medication in medications:
        costs_report.append({
            'medication_id': medication.id,
            'name': medication.name,
            'cost': medication.cost,  # Assuming cost attribute exists in Medication model
            'stock_level': medication.stock_level
        })
    return costs_report

def get_profit_report(session: Session):
    sales_report = get_sales_report(session)
    costs_report = get_costs_report(session)
    profit_report = []

    for sale in sales_report:
        for cost in costs_report:
            if sale['medication_id'] == cost['medication_id']:
                profit_report.append({
                    'medication_id': sale['medication_id'],
                    'profit': sale['total_cost'] - cost['cost']
                })
    return profit_report

# functions to manage bills and payments:
def edit_bill(session: Session, bill_id: int, patient_id: int, total_cost: float, date: Date):
    bill = session.query(Bill).filter(Bill.id == bill_id).first()
    if bill:
        bill.patient_id = patient_id
        bill.total_cost = total_cost
        bill.date = date
        session.commit()

def delete_bill(session: Session, bill_id: int):
    bill = session.query(Bill).filter(Bill.id == bill_id).first()
    if bill:
        session.delete(bill)
        session.commit()

def search_bill(session: Session, bill_id: int):
    return session.query(Bill).filter(Bill.id == bill_id).first()

def add_payment(session: Session, bill_id: int, amount: float, date: Date):
    payment = Payment(bill_id=bill_id, amount=amount, date=date)
    session.add(payment)
    session.commit()

def edit_payment(session: Session, payment_id: int, bill_id: int, amount: float, date: Date):
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        payment.bill_id = bill_id
        payment.amount = amount
        payment.date = date
        session.commit()

def delete_payment(session: Session, payment_id: int):
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        session.delete(payment)
        session.commit()

def search_payment(session: Session, payment_id: int):
    return session.query(Payment).filter(Payment.id == payment_id).first()

# def get_doctor(session: Session, doctor_id: int):

# def get_nurse(session: Session, nurse_id: int):

# graphical user exeprience (GUI)
def main_menu():
    window = tk.Tk()
    window.title("Pharmacy Management System")

    add_medication_button = tk.Button(window, text="Add Medication", command=add_medication_window)
    add_medication_button.pack()

    edit_medication_button = tk.Button(window, text="Edit Medication", command=edit_medication_window)
    edit_medication_button.pack()

    delete_medication_button = tk.Button(window, text="Delete Medication", command=delete_medication_window)
    delete_medication_button.pack()

    search_medication_button = tk.Button(window, text="Search Medication", command=search_medication_window)
    search_medication_button.pack()

    generate_report_button = tk.Button(window, text="Generate Report", command=generate_report_window)
    generate_report_button.pack()

    generate_alerts_button = tk.Button(window, text="Generate Alerts", command=generate_alerts_window)
    generate_alerts_button.pack()

    add_bill_button = tk.Button(window, text="Add Bill", command=add_bill_window)
    add_bill_button.pack()

    edit_bill_button = tk.Button(window, text="Edit Bill", command=edit_bill_window)
    edit_bill_button.pack()

    delete_bill_button = tk.Button(window, text="Delete Bill", command=delete_bill_window)
    delete_bill_button.pack()

    search_bill_button = tk.Button(window, text="Search Bill", command=search_bill_window)
    search_bill_button.pack()

    add_payment_button = tk.Button(window, text="Add Payment", command=add_payment_window)
    add_payment_button.pack()


# Similar buttons for payments

    window.mainloop()

def add_medication_window():
    window = tk.Toplevel()
    window.title("Add Medication")

    # Create labels and entries for the fields using the grid layout
    name_label = tk.Label(window, text="Name")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=0, column=1)


    strength_label = tk.Label(window, text="Strength")
    strength_label.grid(row=1, column=0)
    strength_entry = tk.Entry(window)
    strength_entry.grid(row=1, column=1)


    stock_level_label = tk.Label(window, text="Stock Level")
    stock_level_label.grid(row=2, column=0)
    stock_level_entry = tk.Entry(window)
    stock_level_entry.grid(row=2, column=1)


    expiry_date_label = tk.Label(window, text="Expiry Date")
    expiry_date_label.grid(row=3, column=0)
    expiry_date_entry = tk.Entry(window)
    expiry_date_entry.grid(row=3, column=1)


    reorder_point_label = tk.Label(window, text="Reorder Point")
    reorder_point_label.grid(row=4, column=0)
    reorder_point_entry = tk.Entry(window)
    reorder_point_entry.grid(row=4, column=1)

    # Add similar labels and entries for the other fields

    # add a submit button to add the medication to the database
    submit_button = tk.Button(window, text="Submit",
                              command=lambda: add_medication(name_entry.get(), strength_entry.get(),
                                                             int(stock_level_entry.get()),
                                                             datetime.strptime(expiry_date_entry.get(),
                                                                               '%Y-%m-%d').date(),
                                                             int(reorder_point_entry.get())))
    submit_button.grid(row=5, column=0, columnspan=2)
# GUI for editing a medication
def edit_medication_window(name_entry, strength_entry, stock_level_entry, expiry_date_entry, reorder_point_entry):
    window = tk.Toplevel()
    window.title("Edit Medication")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="Medication ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    # Rest of the fields are similar to add_medication_window

    # Submit button to edit the medication in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: edit_medication(int(id_entry.get()), name_entry.get(), strength_entry.get(), int(stock_level_entry.get()), datetime.strptime(expiry_date_entry.get(), '%Y-%m-%d').date(), int(reorder_point_entry.get())))
    submit_button.grid(row=6, column=0, columnspan=2)

# GUI for deleting a medication
def delete_medication_window():
    window = tk.Toplevel()
    window.title("Delete Medication")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="Medication ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    # Submit button to delete the medication from the database
    submit_button = tk.Button(window, text="Submit", command=lambda: delete_medication(int(id_entry.get())))
    submit_button.grid(row=1, column=0, columnspan=2)

# gui for searching for a medication
def search_medication_window():
    window = tk.Toplevel()
    window.title("Search Medication")

    # Create labels and entries for the fields
    name_label = tk.Label(window, text="Name")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=0, column=1)

    # Submit button to search for the medication in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: search_medication(name_entry.get()))
    submit_button.grid(row=1, column=0, columnspan=2)
# GUI for generating a report
def generate_report_window():
    window = tk.Toplevel()
    window.title("Generate Report")

    report = generate_inventory_report()

    text = tk.Text(window)
    text.insert(tk.END, report)
    text.pack()

# GUI for generating alerts
def generate_alerts_window():
    window = tk.Toplevel()
    window.title("Generate Alerts")

    alerts = generate_alerts()

    text = tk.Text(window)
    text.insert(tk.END, alerts)
    text.pack()


# GUI for adding patients and managing patient profiles
    window = tk.Toplevel()
    window.title("Add Patient")

    # Create labels and entries for the fields
    name_label = tk.Label(window, text="Name")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=0, column=1)

    dob_label = tk.Label(window, text="Date of Birth")
    dob_label.grid(row=2, column=0)
    # create a date picker widget using the tkcalendar library
    dob_entry = tk.Entry(window)
    dob_entry.grid(row=2, column=1)

    # create allergy labe and a a box for the allergies
    allergies_label = tk.Label(window, text="Allergies")
    allergies_label.grid(row=3, column=0)
    allergies_entry = tk.Entry(window)
    allergies_entry.grid(row=3, column=1)

    # Submit button to add the patient to the database
    submit_button = tk.Button(window, text="Submit", command=lambda: add_patient(name_entry.get(), datetime.strptime(dob_entry.get(), '%Y-%m-%d').date(), allergies_entry.get()))
    submit_button.grid(row=4, column=0, columnspan=2)

def edit_patient_window():
    window = tk.Toplevel()
    window.title("Edit Patient")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="patient ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    name_label = tk.Label(window, text="Name")
    name_label.grid(row=1, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=1, column=1)

    dob_label = tk.Label(window, text="Date of Birth")
    dob_label.grid(row=2, column=0)
    # create a date picker widget using the tkcalendar library
    dob_entry = tk.Entry(window)
    dob_entry.grid(row=2, column=1)

    # create allergy labe and a a box for the allergies
    allergies_label = tk.Label(window, text="Allergies")
    allergies_label.grid(row=3, column=0)
    allergies_entry = tk.Entry(window)
    allergies_entry.grid(row=3, column=1)


    # ...

    # Submit button to edit the patient in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: edit_patient(int(id_entry.get()), name_entry.get(), datetime.strptime(dob_entry.get(), '%Y-%m-%d').date(), allergies_entry.get()))
    submit_button.grid(row=5, column=0, columnspan=2)

def delete_patient_window():
    window = tk.Toplevel()
    window.title("Delete Patient")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="patient ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    # Submit button to delete the patient from the database
    submit_button = tk.Button(window, text="Submit", command=lambda: delete_patient(int(id_entry.get())))
    submit_button.grid(row=2, column=0, columnspan=2)

def search_patient_window():
    window = tk.Toplevel()
    window.title("Search Patient")

    # Create labels and entries for the fields
    name_label = tk.Label(window, text="Name")
    name_label.grid(row=0, column=0)
    name_entry = tk.Entry(window)
    name_entry.grid(row=0, column=1)

    # Submit button to search for the patient in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: search_patient(name_entry.get()))
    submit_button.grid(row=2, column=0, columnspan=2)

# GUI for bills and payments
def add_bill_window():
    window = tk.Toplevel()
    window.title("Add Bill")

    # Create labels and entries for the fields
    patient_id_label = tk.Label(window, text="Patient ID")
    patient_id_label.grid(row=0, column=0)
    patient_id_entry = tk.Entry(window)
    patient_id_entry.grid(row=0, column=1)

    total_cost_label = tk.Label(window, text="Total Cost")
    total_cost_label.grid(row=1, column=0)
    total_cost_entry = tk.Entry(window)
    total_cost_entry.grid(row=1, column=1)

    date_label = tk.Label(window, text="Date")
    date_label.grid(row=2, column=0)
    date_entry = tk.Entry(window)
    date_entry.grid(row=2, column=1)


    # ...

    # Submit button to add the bill to the database
    submit_button = tk.Button(window, text="Submit", command=lambda: add_bill(int(patient_id_entry.get()), float(total_cost_entry.get()), datetime.strptime(date_entry.get(), '%Y-%m-%d').date()))
    submit_button.grid(row=4, column=0, columnspan=2)

def edit_bill_window():
    window = tk.Toplevel()
    window.title("Edit Bill")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="Bill ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    patient_id_label = tk.Label(window, text="Patient ID")
    patient_id_label.grid(row=1, column=0)
    patient_id_entry = tk.Entry(window)
    patient_id_entry.grid(row=1, column=1)

    total_cost_label = tk.Label(window, text="Total Cost")
    total_cost_label.grid(row=2, column=0)
    total_cost_entry = tk.Entry(window)
    total_cost_entry.grid(row=2, column=1)

    date_label = tk.Label(window, text="Date")
    date_label.grid(row=3, column=0)
    date_entry = tk.Entry(window)
    date_entry.grid(row=3, column=1)


    # Submit button to edit the bill in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: edit_bill(int(id_entry.get()), int(patient_id_entry.get()), float(total_cost_entry.get()), datetime.strptime(date_entry.get(), '%Y-%m-%d').date()))
    submit_button.grid(row=5, column=0, columnspan=2)

def delete_bill_window():
    window = tk.Toplevel()
    window.title("Delete Bill")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="Bill ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    # ...

    # Submit button to delete the bill from the database
    submit_button = tk.Button(window, text="Submit", command=lambda: delete_bill(int(id_entry.get())))
    submit_button.grid(row=2, column=0, columnspan=2)

def search_bill_window():
    window = tk.Toplevel()
    window.title("Search Bill")

    # Create labels and entries for the fields
    id_label = tk.Label(window, text="Bill ID")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(window)
    id_entry.grid(row=0, column=1)

    # ...

    # Submit button to search for the bill in the database
    submit_button = tk.Button(window, text="Submit", command=lambda: search_bill(int(id_entry.get())))
    submit_button.grid(row=2, column=0, columnspan=2)

# Similar windows for payments
def add_payment_window():
    window = tk.Toplevel()
    window.title("Add Payment")

    # Create labels and entries for the fields
    bill_id_label = tk.Label(window, text="Bill ID")
    bill_id_label.grid(row=0, column=0)
    bill_id_entry = tk.Entry(window)
    bill_id_entry.grid(row=0, column=1)

    amount_label = tk.Label(window, text="Amount")
    amount_label.grid(row=1, column=0)
    amount_entry = tk.Entry(window)
    amount_entry.grid(row=1, column=1)

    date_label = tk.Label(window, text="Date")
    date_label.grid(row=2, column=0)
    date_entry = tk.Entry(window)
    date_entry.grid(row=2, column=1)

    # Submit button to add the payment to the database
    submit_button = tk.Button(window, text="Submit", command=lambda: add_payment(int(bill_id_entry.get()), float(amount_entry.get()), datetime.strptime(date_entry.get(), '%Y-%m-%d').date()))
    submit_button.grid(row=4, column=0, columnspan=2)

def generate_report_window():
    window = tk.Toplevel()
    window.title("Generate Report")

    session = Session()
    report = generate_inventory_report(session)

    text = tk.Text(window)
    text.insert(tk.END, report)
    text.pack()

# Add buttons for these functions to the main menu
main_menu()