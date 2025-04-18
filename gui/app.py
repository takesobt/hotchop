# gui/app.py
import os, pdb
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox  
from hotchop.extractor import HOTchopper

def main():
    root = tk.Tk()
    root.title("HOT Chopper")
    #root.geometry("800x600")

    def on_submit():
        # Input HOT File path
        input_path = input_path_entry.get()
        if not os.path.exists(input_path):
            messagebox.showerror(
                "Error", f"Input HOT File path: {input_path} could not be found."
            )
            return
        # Chopped HOT File path
        output_path = output_path_entry.get()
        if os.path.exists(output_path):
            if not messagebox.askyesno(
                "Confirmation", f"Output File : {output_path} is already exist.\nDo you want to overwrite it?"
                ):
                return
        # criteria type
        if rb1.get() == 1:
            criteria_type = "TDNR"
        else:
            criteria_type = "TRNN"
        # chop_criteria
        chop_criteria = criteria_error_check(
            text_area.get("1.0", tk.END).strip().split("\n")
        )
        if chop_criteria == "ERR":
            return
        # Call main program
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

    def criteria_error_check(wk_criteria_list: list) -> dict:
        # initialize dictionaries
        chop_criteria = {}
        error_item = {}
        # if criteria is empty
        if wk_criteria_list == [""]:
            messagebox.showerror("Error", "Please input criteria!")
            return "ERR"
        # if criteria is default value
        if wk_criteria_list[0] == "xxxyyyyyyyyyy" or wk_criteria_list[0] == "nnnnnn":
            messagebox.showerror("Error", "Please input criteria!")
            return "ERR"

        # Criteria error check
        for i in range(0, len(wk_criteria_list)):
            wk_criteria_list[i] = wk_criteria_list[i].replace(" OK", "")
            wk_criteria_list[i] = wk_criteria_list[i].replace(" ", "")
            if not wk_criteria_list[i].isnumeric():  # Numeric error
                error_item[i] = [
                    wk_criteria_list[i],
                    "Numeric ERR",
                ]  # add to error_item dictionary
            elif rb1.get() == 1 and len(wk_criteria_list[i]) != 13:  # Length error
                error_item[i] = [
                    wk_criteria_list[i],
                    "Length ERR (not 13 digit)",
                ]  # add to error_item dictionary
            elif rb1.get() == 2 and (
                len(wk_criteria_list[i]) < 1 or len(wk_criteria_list[i]) > 6
            ):  # Length error
                error_item[i] = [
                    wk_criteria_list[i],
                    "Length ERR (1<n<999999)",
                ]  # add to error_item dictionary
            else:  # so far no error
                if rb1.get() == 1:
                    wk_len = 13
                else:
                    wk_len = 6
                if (
                    wk_criteria_list[i].zfill(wk_len) in chop_criteria
                ):  # Duplicate error
                    error_item[i] = [
                        wk_criteria_list[i],
                        "Duplicate ERR",
                    ]  # add to duplicate dictionary
                else:  # No error is detected
                    chop_criteria[wk_criteria_list[i].zfill(wk_len)] = (
                        ""  # add to chop criteria
                    )

        # if error item found, output error message
        if len(error_item) > 0:
            wk_msg = "Criteria error found!"
            for c1, [c2, c3] in error_item.items():
                wk_msg += "\n L:" + str(c1 + 1) + " Val:" + c2 + " " + c3
            messagebox.showerror("Error", wk_msg)
            return "ERR"  # return error message
        # No errors
        return chop_criteria

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
    tk.Label(root, text="HOT Chopper", font=("time", 20)).grid(
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