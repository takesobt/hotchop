# gui/app.py
import os, logging, pdb
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox  
from hotchop.extractor import HOTchopper
from hotchop.utils import criteria_error_check

def main():
    root = tk.Tk()
    root.title("HOT Chopper")
    #root.geometry("800x600")

    def on_submit():
        # Input HOT File path
        input_path = input_path_entry.get()
        if not os.path.exists(input_path):
            logging.error(f"Input HOT File path: {input_path} could not be found.")
            messagebox.showerror(
                "Error", f"Input HOT File path: {input_path} could not be found."
            )
            return
        # criteria type
        if rb1.get() == 1:
            criteria_type = "TDNR"
        else:
            criteria_type = "TRNN"
        # chop_criteria
        chop_criteria = criteria_error_check(
            criteria_type,
            text_area.get("1.0", tk.END).strip().split("\n")
        )
        if "ERR" in chop_criteria:
            logging.error(f"Error: There are some errors in chop criteria: {chop_criteria['ERR']}")
            messagebox.showerror("Error", chop_criteria['ERR'])
            return
        # Chopped HOT File path
        output_path = output_path_entry.get()
        if os.path.exists(output_path):
            if not messagebox.askyesno(
                "Confirmation", f"Output File : {output_path} is already exist.\nDo you want to overwrite it?"
                ):
                return
        # Call main program
        logging.info("👉 HOT chopper starts!") 
        logging.info(f"Input: {input_path}")
        logging.info(f"Output: {output_path}")            
        HOTchopper_ins = HOTchopper(
            input_path, output_path, criteria_type, chop_criteria
        )
        HOTchopper_ins.HOT_chop()

        # Result get by dictionary
        chop_criteria = HOTchopper_ins.getresult_criteria()
        wk_msg = ""
        for c1, c2 in chop_criteria.items():
            wk_msg += c1 + " " + c2 + "\n"
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, wk_msg)
        # msgbox
        logging.info("✅ The HOT file was chopped successfully.") 
        messagebox.showinfo("Success", HOTchopper_ins.getresult_number())

    def select_input_file():
        input_file = filedialog.askopenfilename(title="Select Input File")
        if input_file:
            input_path_entry.delete(0, tk.END)
            input_path_entry.insert(0, input_file)

    def select_output_file():
        output_file = filedialog.asksaveasfilename(title="Select Output File")
        if output_file:
            output_path_entry.delete(0, tk.END)
            output_path_entry.insert(0, output_file)

    def update_ScrolledText(*args, **kwargs ):
        text_area.delete("1.0", tk.END)
        if rb1.get() == 1:
            default_text = (
                "xxxyyyyyyyyyy"
                + "\n"
                + "xxxyyyyyyyyyy"
                + "\n"
                + "."
                + "\n"
                + "."
                + "\n"
                + "xxxyyyyyyyyyy"
            )
        else:
            default_text = (
                "nnnnnn" + "\n" + "nnnnnn" + "\n" + "." + "\n" + "." + "\n" + "nnnnnn"
            )
        text_area.insert(tk.END, default_text)

    # Create the main UI window
    # row 0
    tk.Label(root, text="HOT Chop", font=("time", 20)).grid(
        row=0, column=0, padx=10, pady=5, columnspan=3
    )
    # row 1
    tk.Label(root, text="Input HOT File:").grid(
        row=1, column=0, padx=10, pady=5
    )
    input_path_entry = tk.Entry(root, width=50)
    input_path_entry.grid(row=1, column=1, padx=10, pady=5)
    input_path_button = tk.Button(
        root, text="Browse", command=select_input_file
    )
    input_path_button.grid(row=1, column=2, padx=10, pady=5)
    # row 2
    tk.Label(root, text="Chopped HOT File:").grid(
        row=2, column=0, padx=10, pady=5
    )
    output_path_entry = tk.Entry(root, width=50)
    output_path_entry.grid(row=2, column=1, padx=10, pady=5)
    output_path_button = tk.Button(
        root, text="Browse", command=select_output_file
    )
    output_path_button.grid(row=2, column=2, padx=10, pady=5)
    # row 3
    rb1 = tk.IntVar(value=1)
    rb1.trace_add("write", update_ScrolledText)
    rb_TDNR = tk.Radiobutton(
        root, text="TDNR", variable=rb1, value=1, highlightthickness=0
    )
    rb_TDNR.grid(row=3, column=0, sticky="SE")
    rb_TRNC = tk.Radiobutton(
        root, text="TRNN", variable=rb1, value=2, highlightthickness=0
    )
    rb_TRNC.grid(row=4, column=0, sticky="NE")

    text_area = scrolledtext.ScrolledText(
        root, wrap=tk.WORD, width=20, height=8
    )
    text_area.grid(row=3, column=1, pady=10, padx=10, rowspan=2)
    if rb1.get() == 1:
        default_text = (
            "xxxyyyyyyyyyy"
            + "\n"
            + "xxxyyyyyyyyyy"
            + "\n"
            + "."
            + "\n"
            + "."
            + "\n"
            + "xxxyyyyyyyyyy"
        )
    else:
        default_text = (
            "nnnnnn" + "\n" + "nnnnnn" + "\n" + "." + "\n" + "." + "\n" + "nnnnnn"
        )
    text_area.insert(tk.END, default_text)

    # text_area.get()

    # row 5
    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=5, column=1, padx=10, pady=10)

    submit_button = tk.Button(
        root, text="Exit", command=lambda: root.destroy()
    )
    submit_button.grid(row=5, column=2, padx=10, pady=10)

    root.mainloop()