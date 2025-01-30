import tkinter as tk
from tkinter import ttk, font


# Parse the data into a structured format
def parse_data(data):
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    schedule = {day: {f"Slot {i+1}": [] for i in range(5)} for day in days}
    current_day = None
    current_slot = 0

    for line in data.strip().split("\n"):
        line = line.strip()
        if line in days:
            current_day = line
            current_slot = 0
        elif line.startswith("**"):
            current_slot += 1
        elif line != "Free":
            # Split the line into components
            parts = line.split()
            if len(parts) >= 4:
                course_code = parts[0]
                group = parts[1]
                location = parts[2]
                course_name = " ".join(parts[3:])
                entry = f"{course_code} {group} {location} {course_name}"
                schedule[current_day][f"Slot {current_slot+1}"].append(entry)
    return schedule


# Combine multiple schedules
def combine_schedules(*schedules):
    combined = {}
    days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    for day in days:
        combined[day] = {f"Slot {i+1}": [] for i in range(5)}
        for schedule in schedules:
            for slot in schedule[day]:
                combined[day][slot].extend(schedule[day][slot])
    return combined

# Extract unique tutorial numbers for core courses
def extract_core_tutorials(schedule):
    tutorials = set()
    for day in schedule:
        for slot in schedule[day]:
            for entry in schedule[day][slot]:
                if "-EL" not in entry and "-Seminar" not in entry:
                    group = entry.split()[1]  # Extract group (e.g., T009, P008)
                    if group[0] in ["T", "P"]:  # Only consider T and P groups
                        tutorials.add(group[1:])  # Add the number part (e.g., 009, 008)
    return sorted(tutorials)

# Extract unique course names for electives and seminars (without suffixes)
def extract_course_names(schedule, course_type):
    course_names = set()
    for day in schedule:
        for slot in schedule[day]:
            for entry in schedule[day][slot]:
                if course_type == "elective" and "-EL" in entry:
                    course_name = " ".join(entry.split()[3:])  # Full course name
                    base_name = " ".join(course_name.split()[:-1])  # Remove suffix (e.g., "Lecture", "Lab")
                    course_names.add(base_name)
                elif course_type == "seminar" and "-Seminar" in entry:
                    course_name = " ".join(entry.split()[3:])  # Full course name
                    base_name = " ".join(course_name.split()[:-1])  # Remove suffix (e.g., "Lecture", "Lab")
                    course_names.add(base_name)
    return sorted(course_names)

# Extract unique tutorial numbers for electives
def extract_elective_tutorials(schedule, elective_name):
    tutorials = set()
    for day in schedule:
        for slot in schedule[day]:
            for entry in schedule[day][slot]:
                if "-EL" in entry:
                    course_name = " ".join(entry.split()[3:])  # Full course name
                    base_name = " ".join(course_name.split()[:-1])  # Remove suffix
                    if base_name == elective_name:
                        group = entry.split()[1]  # Extract group (e.g., T009, P008)
                        if group[0] in ["T", "P"]:  # Only consider T and P groups
                            tutorials.add(group[1:])  # Add the number part (e.g., 009, 008)
    return sorted(tutorials)

def filter_schedules(schedule, core_filter=None, elective1=None, elective1_tut=None, elective2=None, elective2_tut=None, seminar=None):
    filtered_schedule = {day: {slot: [] for slot in schedule[day]} for day in schedule}

    for day in schedule:
        for slot in schedule[day]:
            for entry in schedule[day][slot]:
                entry_split = entry.split()
                cell_text = f"{entry_split[1]} {' '.join(entry_split[3:])} {entry_split[2]}"
                if "-EL" not in entry and "-Seminar" not in entry:
                    # Always include core lectures
                    if "Lecture" in entry:
                        filtered_schedule[day][slot].append(cell_text)
                    # Include core tutorials and labs if core_filter matches
                    elif core_filter is None or core_filter in entry:
                        filtered_schedule[day][slot].append(cell_text)
                elif "-EL" in entry:
                    course_name = " ".join(entry_split[3:])  # Full course name
                    base_name = " ".join(course_name.split()[:-1])  # Remove suffix
                    group = entry_split[1]  # Extract group (e.g., T009, P008)
                    if (elective1 is not None and elective1 == base_name and (elective1_tut is None or elective1_tut == "All" or group[1:] == elective1_tut or 'lecture' in course_name.lower())) or \
                       (elective2 is not None and elective2 == base_name and (elective2_tut is None or elective2_tut == "All" or group[1:] == elective2_tut or 'lecture' in course_name.lower())):
                        filtered_schedule[day][slot].append(cell_text)
                elif "-Seminar" in entry:
                    course_name = " ".join(entry_split[3:])  # Full course name
                    base_name = " ".join(course_name.split()[:-1])  # Remove suffix
                    if seminar is not None and seminar == base_name:
                        filtered_schedule[day][slot].append(cell_text)
    return filtered_schedule


# GUI Application
class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Schedule Explorer")
        if len(data) == 0:
            raise ValueError("No data provided")
        
        self.schedule = parse_data(data[0])
        for i in range(1, len(data)):
            self.schedule = combine_schedules(self.schedule, parse_data(data[i]))
        self.core_tutorials = extract_core_tutorials(self.schedule)
        self.elective_courses = extract_course_names(self.schedule, "elective")
        self.seminar_courses = extract_course_names(self.schedule, "seminar")
        self.font_size = 10  # Default font size
        self.label_font = font.Font(size=14)

        # UI Components
        self.core_filter = tk.StringVar(value="None")
        self.elective1 = tk.StringVar(value="None")
        self.elective1_tut = tk.StringVar(value="All")
        self.elective2 = tk.StringVar(value="None")
        self.elective2_tut = tk.StringVar(value="All")
        self.seminar = tk.StringVar(value="None")

        self.create_widgets()

    def create_widgets(self):
        # Dropdowns and Button
        ttk.Label(self.root, text="Core Filter:", font=self.label_font).grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(self.root, textvariable=self.core_filter, values=["None"] + self.core_tutorials, font=self.label_font).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.root, text="Elective 1:", font=self.label_font).grid(row=0, column=2, padx=5, pady=5)
        ttk.Combobox(self.root, textvariable=self.elective1, values=["None"] + self.elective_courses, state="readonly", font=self.label_font).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(self.root, text="Tutorial:", font=self.label_font).grid(row=0, column=4, padx=5, pady=5)
        self.elective1_tut_dropdown = ttk.Combobox(self.root, textvariable=self.elective1_tut, values=["All"], state="readonly", font=self.label_font)
        self.elective1_tut_dropdown.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(self.root, text="Elective 2:", font=self.label_font).grid(row=1, column=1, padx=5, pady=5)
        ttk.Combobox(self.root, textvariable=self.elective2, values=["None"] + self.elective_courses, state="readonly", font=self.label_font).grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(self.root, text="Tutorial:").grid(row=1, column=3, padx=5, pady=5)
        self.elective2_tut_dropdown = ttk.Combobox(self.root, textvariable=self.elective2_tut, values=["All"], state="readonly", font=self.label_font)
        self.elective2_tut_dropdown.grid(row=1, column=4, padx=5, pady=5)

        ttk.Label(self.root, text="Seminar:", font=self.label_font).grid(row=1, column=5, padx=5, pady=5)
        ttk.Combobox(self.root, textvariable=self.seminar, values=["None"] + self.seminar_courses, state="readonly", font=self.label_font).grid(row=1, column=6, padx=5, pady=5)

        # Create a style object
        style = ttk.Style()

        # Configure the style for the button
        style.configure("Custom.TButton", background="#0cb370", foreground="white", font=("Arial", 12, "bold"))
        # Configure the hover color for the button
        style.map("Custom.TButton",
          background=[("active", "#0a8f5c")],  # Hover background color
          foreground=[("active", "#d1d1d1")])  # Hover foreground color
        ttk.Button(self.root, text="Apply Filters", command=self.update_table, style="Custom.TButton").grid(row=2, column=6, padx=5, pady=5)

        # Font Size Controller
        ttk.Label(self.root, text="Font Size:").grid(row=2, column=2, padx=5, pady=5)
        self.font_size_var = tk.IntVar(value=self.font_size)
        ttk.Combobox(self.root, textvariable=self.font_size_var, values=[8, 10, 12, 14, 16], width=5).grid(row=2, column=3, padx=5, pady=5)
        ttk.Button(self.root, text="Apply Font Size", command=self.apply_font_size).grid(row=2, column=4, padx=5, pady=5)

        # Table Frame
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.grid(row=3, column=0, columnspan=16, sticky="nsew", padx=5, pady=5)

        # Configure grid weights for dynamic resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a grid of Text widgets for the table
        self.text_widgets = {}
        days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        for i, day in enumerate(["Day", "Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5"]):
            self.table_frame.grid_columnconfigure(i, weight=1)
            label = ttk.Label(self.table_frame, text=day, font=("Arial", 11, "bold"))
            label.grid(row=0, column=i, sticky="nsew")
            for j, day_name in enumerate(days):
                self.table_frame.grid_rowconfigure(j + 1, weight=1)
                text = tk.Text(self.table_frame, width=20, height=5, wrap=tk.WORD, font=("Arial", self.font_size))
                text.grid(row=j + 1, column=i, sticky="nsew")
                text.config(state=tk.DISABLED)  # Make it read-only
                self.text_widgets[(j + 1, i)] = text

        # Bind elective dropdowns to update tutorial dropdowns
        self.elective1.trace_add("write", self.update_elective1_tutorials)
        self.elective2.trace_add("write", self.update_elective2_tutorials)

    def update_elective1_tutorials(self, *args):
        elective_name = self.elective1.get()
        if elective_name == "None":
            self.elective1_tut_dropdown["values"] = ["All"]
            self.elective1_tut.set("All")
        else:
            tutorials = extract_elective_tutorials(self.schedule, elective_name)
            self.elective1_tut_dropdown["values"] = ["All"] + tutorials
            self.elective1_tut.set("All")

    def update_elective2_tutorials(self, *args):
        elective_name = self.elective2.get()
        if elective_name == "None":
            self.elective2_tut_dropdown["values"] = ["All"]
            self.elective2_tut.set("All")
        else:
            tutorials = extract_elective_tutorials(self.schedule, elective_name)
            self.elective2_tut_dropdown["values"] = ["All"] + tutorials
            self.elective2_tut.set("All")

    def update_table(self):
        # Clear the table
        for widget in self.text_widgets.values():
            widget.config(state=tk.NORMAL)
            widget.delete(1.0, tk.END)
            widget.config(state=tk.DISABLED)

        # Apply filters
        filtered_schedule = filter_schedules(
            self.schedule,
            core_filter=self.core_filter.get() if self.core_filter.get() != "None" else None,
            elective1=self.elective1.get() if self.elective1.get() != "None" else None,
            elective1_tut=self.elective1_tut.get() if self.elective1_tut.get() != "None" else None,
            elective2=self.elective2.get() if self.elective2.get() != "None" else None,
            elective2_tut=self.elective2_tut.get() if self.elective2_tut.get() != "None" else None,
            seminar=self.seminar.get() if self.seminar.get() != "None" else None
        )

        self.apply_font_size()
        # Populate the table
        days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        for i, day in enumerate(days):
            self.text_widgets[(i + 1, 0)].config(state=tk.NORMAL)
            self.text_widgets[(i + 1, 0)].delete("1.0", tk.END)  # Clear existing text
            self.text_widgets[(i + 1, 0)].insert(tk.END, day, "boldy")
            for j, slot in enumerate(["Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5"]):
                self.text_widgets[(i + 1, j + 1)].config(state=tk.NORMAL)
                entries = filtered_schedule[day][slot]
                for entry in entries:
                    if "Lecture" in entry and "-EL" not in entry and "-Seminar" not in entry:
                        self.text_widgets[(i + 1, j + 1)].insert(tk.END, entry + "\n", "regular")
                    else:
                        self.text_widgets[(i + 1, j + 1)].insert(tk.END, entry + "\n", "bold")
                self.text_widgets[(i + 1, j + 1)].config(state=tk.DISABLED)

        self.apply_font_size()

    def apply_font_size(self):
        # Update font size for all text widgets
        self.font_size = self.font_size_var.get()
        for widget in self.text_widgets.values():
            widget.config(font=("Arial", self.font_size))
            widget.tag_configure("regular", font=("Arial", self.font_size))
            widget.tag_configure("bold", font=("Arial", self.font_size, "bold"))
            widget.tag_configure("boldy", font=("Arial", self.font_size+5, "bold"))



data = ["""
Saturday	
Free
**********
Free
**********
Free
**********
Free
**********
Free
**********


Sunday	
10MET P008	C7.217	CSEN 1002 Lab
10MET P006	C7.203	CSEN 1002 Lab
10MET P015	C7.220	CSEN 1002 Lab
10MET T009	D4.101	CSEN 1003 Tut
10MET T012	B4.211	HUMA 1001 Tut
10MET T010	B4.212	HUMA 1001 Tut
10MET T007	B4.213	HUMA 1001 Tut
10MET-EL T001	C3.306	NETW 1009 Tut
10MET-EL T009	B2.111	DMET 1001 Tut
**********
10MET P008	C7.217	CSEN 1002 Lab
10MET P006	C7.203	CSEN 1002 Lab
10MET P015	C7.220	CSEN 1002 Lab
10MET-EL P001	C7.201	ELCT 1018 Lab
10MET-EL T003	C2.306	MCTR 1024 Tut
10MET-EL T002	C3.306	NETW 1009 Tut
10MET-EL T010	B2.111	DMET 1001 Tut
10MET T013	D4.106	CSEN 1001 Tut
10MET T009	B4.207	CSEN 1001 Tut
10MET T012	B4.206	CSEN 1003 Tut
**********
10MET-EL T003	C3.306	NETW 1009 Tut
10MET-EL T011	B2.110	DMET 1001 Tut
10MET-EL T001	B2.112	DMET 1067 Tut
10MET-EL L001	H18	NETW 1009 Lecture
**********
10MET-EL P002	C7.201	ELCT 1018 Lab
10MET-EL T012	C2.312	DMET 1001 Tut
10MET-EL L001	H10	DMET 1067 Lecture
**********
10MET-EL T004	C3.306	NETW 1009 Tut
10MET-EL T013	C5.301	DMET 1001 Tut
10MET-EL T002	C5.108	DMET 1067 Tut
**********


Monday	
10MET P013	C7.201	CSEN 1002 Lab
10MET T006	D4.101	CSEN 1003 Tut
10MET-EL T008	C3.306	NETW 1009 Tut
10MET-EL T001	C6.204	DMET 1001 Tut
10MET-EL L001	C4.101	DMET 1075 Lecture
10MET-EL L001	H9	ELCT 1018 Lecture
**********
10MET P013	C7.201	CSEN 1002 Lab
10MET T006	D4.101	CSEN 1001 Tut
10MET-EL T005	C3.306	NETW 1009 Tut
10MET-EL T002	C6.204	DMET 1001 Tut
10MET-EL T002	C7.305	CSEN 1076 Tut
10MET-EL L001	C4.101	DMET 1075 Lecture
**********
10MET-EL T006	C3.306	NETW 1009 Tut
10MET-EL T003	C2.312	DMET 1001 Tut
10MET-EL L001	H16	CSEN 1076 Lecture
10MET-EL L001	C6.104	DMET 1042 Lecture
**********
10MET-EL T007	C3.306	NETW 1009 Tut
10MET-EL T004	C2.311	DMET 1001 Tut
10MET-EL T001	C7.305	CSEN 1076 Tut
10MET-EL L001	C6.104	DMET 1042 Lecture
10MET-EL L001	H17	MCTR 1024 Lecture
**********
10MET-Seminar L001	C5.101	CSEN 1135 Lecture
10MET-Seminar L001	C5.102	CSEN 1142 Lecture
10MET-Seminar L001	C5.104	DMET 1076 Lecture
10MET-Seminar L001	C5.106	CSEN 1126 Lecture
10MET-Seminar L001	C5.105	CSEN 1118 Lecture
**********


Tuesday	
10MET-EL T009	C3.306	NETW 1009 Tut
10MET-EL T005	C5.301	DMET 1001 Tut
**********
10MET L001	H13	CSEN 1003 Lecture
**********
10MET-Seminar L002	C5.206	DMET 1076 Lecture
10MET-Seminar L002	C5.212	CSEN 1118 Lecture
10MET-Seminar L001	C5.301	CSEN 1088 Lecture
10MET-Seminar L001	C5.302	CSEN 1127 Lecture
10MET-Seminar L001	C2.308	CSEN 1141 Lecture
10MET-Seminar L001	C2.306	CSEN 1139 Lecture
10MET-Seminar L001	C2.309	CSEN 1008 Lecture
10MET-Seminar L001	C2.311	DMET 1057 Lecture
10MET-Seminar L001	C2.312	CSEN 1034 Lecture
10MET-Seminar L001	C6.204	DMET 1061 Lecture
**********
10MET P009	C7.217	CSEN 1002 Lab
10MET P010	C7.201	CSEN 1002 Lab
10MET P014	C7.203	CSEN 1002 Lab
10MET T008	D4.101	CSEN 1001 Tut
10MET T011	D4.110	CSEN 1001 Tut
10MET T006	B4.211	HUMA 1001 Tut
10MET T005	D4.105	CSEN 1003 Tut
10MET T013	C5.101	CSEN 1003 Tut
10MET T015	D4.108	CSEN 1003 Tut
**********
10MET P009	C7.217	CSEN 1002 Lab
10MET P010	C7.201	CSEN 1002 Lab
10MET P014	C7.203	CSEN 1002 Lab
10MET T012	D4.101	CSEN 1001 Tut
10MET T005	D4.105	CSEN 1001 Tut
10MET T011	D4.106	CSEN 1003 Tut
10MET T013	B4.212	HUMA 1001 Tut
10MET-EL T010	C3.306	NETW 1009 Tut
10MET-EL T006	C5.301	DMET 1001 Tut
**********


Wednesday	
10MET-Seminar L002	C2.301	CSEN 1088 Lecture
10MET-Seminar L002	C2.302	CSEN 1127 Lecture
10MET-Seminar L001	C2.312	CSEN 1134 Lecture
10MET-Seminar L002	C2.311	CSEN 1034 Lecture
10MET-Seminar L001	C2.309	CSEN 1140 Lecture
10MET-Seminar L001	C2.308	DMET 1077 Lecture
10MET-Seminar L001	C2.306	CSEN 1143 Lecture
10MET-Seminar L001	C2.305	CSEN 1128 Lecture
**********
10MET P011	C7.203	CSEN 1002 Lab
10MET P012	C7.201	CSEN 1002 Lab
10MET T015	C5.101	CSEN 1001 Tut
10MET T008	C5.102	CSEN 1003 Tut
10MET T010	D4.106	CSEN 1003 Tut
10MET T007	D4.108	CSEN 1001 Tut
10MET T009	B4.211	HUMA 1001 Tut
**********
10MET P011	C7.203	CSEN 1002 Lab
10MET P012	C7.201	CSEN 1002 Lab
10MET T010	D4.101	CSEN 1001 Tut
10MET T015	B4.211	HUMA 1001 Tut
10MET T007	D4.105	CSEN 1003 Tut
10MET T014	D4.108	CSEN 1003 Tut
10MET T008	B4.212	HUMA 1001 Tut
**********
10MET L001	H19	HUMA 1001 Lecture
10MET-EL L001	C3.110	CSEN 1038 Lecture
**********
10MET-EL P001	C7.303	CSEN 1038 Lab
10MET L001	H19	CSEN 1001 Lecture
**********


Thursday	
10MET-EL T015	C3.306	NETW 1009 Tut
10MET-EL L002	H16	DMET 1001 Lecture
**********
10MET T005	B1.01	HUMA 1001 Tut
10MET-EL T014	C5.301	DMET 1001 Tut
**********
10MET T011	B4.211	HUMA 1001 Tut
10MET-EL T011	C4.206	NETW 1009 Tut
10MET-EL T012	C3.306	NETW 1009 Tut
10MET-EL L001	H16	DMET 1001 Lecture
**********
10MET P007	C7.201	CSEN 1002 Lab
10MET P005	C7.203	CSEN 1002 Lab
10MET T014	C5.101	CSEN 1001 Tut
10MET-EL T013	C3.306	NETW 1009 Tut
10MET-EL T007	C2.312	DMET 1001 Tut
10MET-EL L001	C6.203	DMET 1072 Lecture
10MET-EL L001	C6.204	CSEN 907 Lecture
**********
10MET P007	C7.201	CSEN 1002 Lab
10MET P005	C7.203	CSEN 1002 Lab
10MET T014	B4.211	HUMA 1001 Tut
10MET-EL T014	C3.306	NETW 1009 Tut
10MET-EL T008	C2.312	DMET 1001 Tut
10MET-EL L001	C6.206	DMET 1072 Lecture
10MET-EL L001	C6.204	CSEN 907 Lecture
**********


Friday
Free
**********
Free
**********
Free
**********
Free
**********
Free
**********
""",
"""
Saturday	
Free
**********
Free
**********
Free
**********
Free
**********
Free
**********


Sunday
Free
**********
10MET T017	B4.211	HUMA 1001 Tut
**********
Free
**********
10MET P020	D3.306	CSEN 1002 Lab
10MET P021	C7.203	CSEN 1002 Lab
10MET P022	C7.217	CSEN 1002 Lab
10MET T024	D4.106	CSEN 1001 Tut
10MET T017	D4.108	CSEN 1001 Tut
10MET T016	D4.110	CSEN 1003 Tut
10MET-EL T016	C3.306	NETW 1009 Tut
**********
10MET P020	D3.306	CSEN 1002 Lab
10MET P021	C7.203	CSEN 1002 Lab
10MET P022	C7.217	CSEN 1002 Lab
10MET T016	D4.101	CSEN 1001 Tut
10MET T019	D4.105	CSEN 1001 Tut
10MET T017	D4.106	CSEN 1003 Tut
10MET T024	D4.108	CSEN 1003 Tut
**********


Monday	
10MET P023	C7.203	CSEN 1002 Lab
10MET T026	D4.105	CSEN 1001 Tut
**********
10MET P023	C7.203	CSEN 1002 Lab
10MET T026	D4.105	CSEN 1003 Tut
**********
10MET T022	D4.101	CSEN 1003 Tut
**********
10MET T022	D4.101	CSEN 1001 Tut
**********
Free
**********


Tuesday	
10MET P016	C7.201	CSEN 1002 Lab
10MET T019	B4.211	HUMA 1001 Tut
10MET T020	B4.212	HUMA 1001 Tut
**********
10MET P016	C7.201	CSEN 1002 Lab
10MET T019	C5.101	CSEN 1003 Tut
10MET T022	B4.211	HUMA 1001 Tut
10MET T021	D4.105	CSEN 1001 Tut
10MET T023	D4.106	CSEN 1001 Tut
10MET T018	C6.204	CSEN 1003 Tut
**********
Free
**********
10MET L002	H13	CSEN 1003 Lecture
**********
10MET T024	B4.213	HUMA 1001 Tut
**********


Wednesday	
Free
**********
10MET L002	H4	CSEN 1001 Lecture
**********
10MET L002	H19	HUMA 1001 Lecture
**********
10MET P017	C7.217	CSEN 1002 Lab
10MET P018	C7.201	CSEN 1002 Lab
10MET P019	C7.203	CSEN 1002 Lab
10MET T020	D4.101	CSEN 1001 Tut
10MET T021	C2.308	CSEN 1003 Tut
10MET T023	C2.306	CSEN 1003 Tut
10MET T025	B4.211	HUMA 1001 Tut
**********
10MET P017	C7.217	CSEN 1002 Lab
10MET P018	C7.201	CSEN 1002 Lab
10MET P019	C7.203	CSEN 1002 Lab
10MET T020	D4.101	CSEN 1003 Tut
10MET T021	B4.211	HUMA 1001 Tut
10MET T023	B4.212	HUMA 1001 Tut
10MET T025	C5.101	CSEN 1003 Tut
**********


Thursday	
10MET P025	C6.209	CSEN 1002 Lab
10MET P026	C7.201	CSEN 1002 Lab
**********
10MET P025	C6.209	CSEN 1002 Lab
10MET P026	C7.201	CSEN 1002 Lab
10MET-EL L002	H16	NETW 1009 Lecture
**********
Free
**********
10MET P024	C7.217	CSEN 1002 Lab
10MET T025	D4.105	CSEN 1001 Tut
10MET T018	B4.211	HUMA 1001 Tut
10MET T026	B4.212	HUMA 1001 Tut
**********
10MET P024	C7.217	CSEN 1002 Lab
10MET T018	C5.301	CSEN 1001 Tut
10MET T016	B4.212	HUMA 1001 Tut
**********

"""
]


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()