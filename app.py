import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.filedialog import asksaveasfilename
from tkcalendar import DateEntry
from ttkthemes import ThemedStyle
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# File to store transaction data
DATA_FILE = "transactions.csv"

# Ensure the file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Type", "Category", "Amount"])

# Helper function to read transactions
def read_transactions():    
    with open(DATA_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to add a transaction
def add_transaction(date, t_type, category, amount):
    if not date or not t_type or not category or not amount:
        messagebox.showwarning("Input Error", "All fields must be filled!")
        return
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a valid number!")
        return

    with open(DATA_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, t_type, category, amount])
    messagebox.showinfo("Success", "Transaction added successfully!")
    refresh_transactions()
    clear_fields()

# Clear input fields
def clear_fields():
    # Reset DateEntry to None (no date selected)
    entry_date.set_date(None)
    
    # Clear ComboBox and Entry fields
    combo_type.set("")  # Reset ComboBox to default (empty)
    entry_category.delete(0, tk.END)  # Clear text in the Entry widget
    entry_amount.delete(0, tk.END)  # Clear text in the Entry widget


# Refresh transaction table
def refresh_transactions(data=None):
    transactions = data if data else read_transactions()
    tree.delete(*tree.get_children())
    for transaction in transactions:
        tags = ("income",) if transaction["Type"] == "Income" else ("expense",)
        tree.insert("", "end", values=(transaction["Date"], transaction["Type"], transaction["Category"], transaction["Amount"]), tags=tags)
    tree.update_idletasks()

# Function to apply filters
def apply_filter():
    filter_window = tk.Toplevel(root)
    filter_window.title("Filter Transactions")
    filter_window.geometry("400x250")

    tk.Label(filter_window, text="Start Date:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
    start_date = DateEntry(filter_window, date_pattern="dd-mm-yyyy", font=("Arial", 12))
    start_date.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(filter_window, text="End Date:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
    end_date = DateEntry(filter_window, date_pattern="dd-mm-yyyy", font=("Arial", 12))
    end_date.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(filter_window, text="Type:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
    type_filter = ttk.Combobox(filter_window, values=["All", "Income", "Expense"], state="readonly", font=("Arial", 12))
    type_filter.grid(row=2, column=1, padx=10, pady=10)
    type_filter.set("All")

    def filter_data():
        transactions = read_transactions()
        filtered = []
        for transaction in transactions:
            if start_date.get() <= transaction["Date"] <= end_date.get():
                if type_filter.get() == "All" or transaction["Type"] == type_filter.get():
                    filtered.append(transaction)
        refresh_transactions(filtered)
        filter_window.destroy()

    tk.Button(filter_window, text="Apply", font=("Arial", 12), command=filter_data).grid(row=3, column=0, columnspan=2, pady=20)

# Function to remove filters
def remove_filter():
    refresh_transactions()

# Function to generate PDF report
def generate_pdf(transactions, file_path):
    pdf = SimpleDocTemplate(file_path, pagesize=letter)
    table_data = [["Date", "Type", "Category", "Amount"]]
    for transaction in transactions:
        table_data.append([transaction["Date"], transaction["Type"], transaction["Category"], transaction["Amount"]])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    pdf.build([table])
    messagebox.showinfo("PDF Generated", f"PDF saved to {file_path}")

# Function to generate Excel report
def generate_excel(transactions, file_path):
    df = pd.DataFrame(transactions)
    df.to_excel(file_path, index=False)
    messagebox.showinfo("Excel Generated", f"Excel saved to {file_path}")

# Function to generate report (PDF/Excel)
def generate_report():
    transactions = []
    for item in tree.get_children():
        values = tree.item(item)["values"]
        transactions.append({
            "Date": values[0],
            "Type": values[1],
            "Category": values[2],
            "Amount": values[3]
        })

    if not transactions:
        messagebox.showwarning("No Data", "No transactions to generate a report.")
        return

    # Popup window for file type selection
    def generate_selected_report():
        selected_type = file_type_var.get()
        if not selected_type:
            messagebox.showwarning("Selection Required", "Please select a file type.")
            return

        if selected_type == "PDF":
            pdf_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if pdf_file:
                generate_pdf(transactions, pdf_file)
        elif selected_type == "Excel":
            excel_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if excel_file:
                generate_excel(transactions, excel_file)

        popup.destroy()

    # Create the popup window
    popup = tk.Toplevel(root)
    popup.title("Generate Report")
    popup.geometry("300x150")

    # Dropdown variable
    file_type_var = tk.StringVar()

    # UI elements in the popup
    tk.Label(popup, text="Select report type:", font=("Helvetica", 14)).pack(pady=10)
    file_type_dropdown = ttk.Combobox(popup, textvariable=file_type_var, font=("Helvetica", 12), state="readonly",
                                      values=["PDF", "Excel"])
    file_type_dropdown.pack(pady=5)
    file_type_dropdown.set("PDF")  # Default selection

    # Generate button
    tk.Button(popup, text="Generate", command=generate_selected_report, width=10, font=("Helvetica", 12)).pack(pady=20)

    # Close button
    tk.Button(popup, text="Cancel", command=popup.destroy, width=10, font=("Helvetica", 12)).pack(pady=10)


# Visualization Function
def visualize_dashboard():
    transactions = read_transactions()

    # Parse and preprocess data
    data = pd.DataFrame(transactions)
    data["Amount"] = data["Amount"].astype(float)
    data["Date"] = pd.to_datetime(data["Date"], format="%d-%m-%Y")
    data["Month"] = data["Date"].dt.to_period("M").dt.strftime("%b %Y")

    # Function to filter transactions
    def filter_transactions(data, start_date, end_date, t_type):
        filtered_data = data.copy()
        if start_date and end_date:
            filtered_data = filtered_data[
                (filtered_data["Date"] >= pd.to_datetime(start_date, format="%d-%m-%Y")) &
                (filtered_data["Date"] <= pd.to_datetime(end_date, format="%d-%m-%Y"))
            ]
        if t_type != "All":
            filtered_data = filtered_data[filtered_data["Type"] == t_type]
        return filtered_data

    # Create Dashboard Window
    dashboard = tk.Toplevel(root)
    dashboard.title("Finance Dashboard")
    dashboard.geometry("900x700")
    dashboard.state("zoomed")
    dashboard.configure(bg="#ffffff")

    # Header Frame for Filters and Navigation
    header_frame = tk.Frame(dashboard, bg="#ffffff", pady=10)
    header_frame.pack(fill="x")

    tk.Label(header_frame, text="Start Date:", font=("Arial", 12), bg="#ffffff").pack(side="left", padx=5)
    start_date = DateEntry(header_frame, date_pattern="dd-mm-yyyy", font=("Arial", 12))
    start_date.pack(side="left", padx=5)

    tk.Label(header_frame, text="End Date:", font=("Arial", 12), bg="#ffffff").pack(side="left", padx=5)
    end_date = DateEntry(header_frame, date_pattern="dd-mm-yyyy", font=("Arial", 12))
    end_date.pack(side="left", padx=5)

    tk.Label(header_frame, text="Type:", font=("Arial", 12), bg="#ffffff").pack(side="left", padx=5)
    type_filter = ttk.Combobox(header_frame, values=["All", "Income", "Expense"], state="readonly", font=("Arial", 12))
    type_filter.set("All")
    type_filter.pack(side="left", padx=5)

    def update_charts():
        filtered_data = filter_transactions(
            data, start_date.get(), end_date.get(), type_filter.get()
        )
        if current_chart == "pie":
            update_pie_chart(filtered_data)
        elif current_chart == "bar":
            update_bar_chart(filtered_data)

    tk.Button(header_frame, text="Apply Filter", font=("Arial", 12), command=update_charts).pack(side="left", padx=5)

    # Navigation Buttons
    current_chart = "pie"

    def show_pie_chart():
        nonlocal current_chart
        current_chart = "pie"
        update_pie_chart(data)

    def show_bar_chart():
        nonlocal current_chart
        current_chart = "bar"
        update_bar_chart(data)

    tk.Button(header_frame, text="Transaction Breakdown", font=("Arial", 12), command=show_pie_chart).pack(side="left", padx=10)
    tk.Button(header_frame, text="Monthly Trends", font=("Arial", 12), command=show_bar_chart).pack(side="left", padx=10)

    # Visualization Frame
    visualization_frame = tk.Frame(dashboard, bg="#ffffff")
    visualization_frame.pack(fill="both", expand=True, pady=10, padx=10)

    # Pie Chart
    def update_pie_chart(filtered_data):
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        pie_data = filtered_data.groupby("Category")["Amount"].sum()

        if not pie_data.empty:
            ax.pie(
                pie_data.values,
                labels=pie_data.index,
                autopct="%1.1f%%",
                startangle=140,
                colors=plt.cm.Paired.colors
            )
            ax.set_title("Transaction Breakdown by Category (₹)", fontsize=14)
        else:
            ax.text(0.5, 0.5, "No Data Available", horizontalalignment='center', verticalalignment='center', fontsize=14)

        canvas = FigureCanvasTkAgg(fig, visualization_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar_frame = tk.Frame(visualization_frame)
        toolbar_frame.pack()
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.draw()

    # Bar Chart
    def update_bar_chart(filtered_data):
        for widget in visualization_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        monthly_data = filtered_data.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

        if not monthly_data.empty:
            months = monthly_data.index
            income = monthly_data.get("Income", [])
            expense = monthly_data.get("Expense", [])

            x = range(len(months))
            bar_width = 0.4
            ax.bar(x, income, width=bar_width, label="Income", color="#4caf50")
            ax.bar([p + bar_width for p in x], expense, width=bar_width, label="Expense", color="#f44336")

            ax.set_title("Monthly Income vs Expense Comparison (₹)", fontsize=14)
            ax.set_xticks([p + bar_width / 2 for p in x])
            ax.set_xticklabels(months, rotation=45, ha="right")
            ax.set_ylabel("Amount (₹)", fontsize=12)
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No Data Available", horizontalalignment='center', verticalalignment='center', fontsize=14)

        canvas = FigureCanvasTkAgg(fig, visualization_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar_frame = tk.Frame(visualization_frame)
        toolbar_frame.pack()
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas.draw()

    # Default Charts
    show_pie_chart()


# GUI Setup
root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("1000x750")
root.minsize(800, 600)
root.state("zoomed")  # Launch the application maximized
root.configure(bg="#f4f6f9")

# Apply modern theme
style = ThemedStyle(root)
style.set_theme("arc")  # Modern and clean "arc" theme
style.configure("Treeview", font=("Arial", 12), rowheight=25, background="#f9f9f9")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#d6e0e9", foreground="black")
style.configure("TButton", font=("Arial", 12), padding=10, relief="flat", background="#6c7ae0", foreground="white")
style.map("TButton", background=[("active", "#5a67d8")])
style.configure("TLabel", font=("Arial", 12))

# Adding Transactions
frame_add = tk.Frame(root, bg="#f4f6f9", pady=15)
frame_add.pack(fill="x")

tk.Label(frame_add, text="Date:", bg="#f4f6f9", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
entry_date = DateEntry(frame_add, date_pattern="dd-mm-yyyy", font=("Arial", 12))
entry_date.grid(row=0, column=1, padx=10)

tk.Label(frame_add, text="Type:", bg="#f4f6f9", font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=5)
combo_type = ttk.Combobox(frame_add, values=["Income", "Expense"], state="readonly", font=("Arial", 12))
combo_type.grid(row=0, column=3, padx=10)

tk.Label(frame_add, text="Category:", bg="#f4f6f9", font=("Arial", 12)).grid(row=0, column=4, padx=10, pady=5)
entry_category = ttk.Entry(frame_add)
entry_category.grid(row=0, column=5, padx=10)

tk.Label(frame_add, text="Amount:", bg="#f4f6f9", font=("Arial", 12)).grid(row=0, column=6, padx=10, pady=5)
entry_amount = ttk.Entry(frame_add)
entry_amount.grid(row=0, column=7, padx=10)

tk.Button(frame_add, text="Add Transaction", command=lambda: add_transaction(entry_date.get(), combo_type.get(), entry_category.get(), entry_amount.get())).grid(row=0, column=8, padx=10)

# Transaction Table
frame_table = tk.Frame(root, bg="#f4f6f9")
frame_table.pack(fill="both", expand=True, pady=20, padx=10)

columns = ("Date", "Type", "Category", "Amount")
tree = ttk.Treeview(frame_table, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=col)
tree.column("Date", width=120)
tree.column("Type", width=100)
tree.column("Category", width=150)
tree.column("Amount", width=100)
tree.tag_configure("income", background="#e1f7d5")  # Light green for income
tree.tag_configure("expense", background="#f8d7da")  # Light red for expense
tree.pack(fill="both", expand=True, side="left")

scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Buttons for actions
frame_buttons = tk.Frame(root, bg="#f4f6f9")
frame_buttons.pack(fill="x", pady=15)

tk.Button(frame_buttons, text="Filter Transactions", command=apply_filter).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Remove Filter", command=remove_filter).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Generate Report", command=generate_report).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Visualize Finance", command=visualize_dashboard).pack(side="left", padx=10)

# Initial load
refresh_transactions()

# Run application
root.mainloop()

