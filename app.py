import customtkinter as ctk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import plotting
import pandas as pd
import os

COLORS = ["#E7298A", "#D95F02", "#66A61E", "#7570B3", "#1B9E77"]

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('dark')

        # LOGIC SETTINGS
        self.channel_metadata = []
        self.checkboxes = []
        self.data_metrics = []
        self.data = pd.DataFrame()
        self.current_data = pd.DataFrame()
        self.fig = None
        self.threshold = 0
        self.x_unit = ""
        self.y_unit = ""
        self.file_name = ""

        # UI SETTINGS
        self.title('Graph-Plotting')
        self.geometry('800x600')
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=3)  # (plot)
        self.grid_columnconfigure(1, weight=1)  # (buttons)
        self.grid_rowconfigure(0, weight=3)  # (plot/buttons)
        self.grid_rowconfigure(1, weight=1, minsize=100)  # (data display)

        self.setup_plot()
        self.setup_buttons()
        self.setup_data_display()
    
    def setup_plot(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.plot_frame = frame
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10) 

    def setup_data_display(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.data_display_frame = frame

    def setup_buttons(self):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        options_label = ctk.CTkLabel(frame, text="Options", font=("Arial", 16, "bold"), anchor="w")
        options_label.pack(pady=5, padx=5, fill="x")

        load_button = ctk.CTkButton(frame, text="Load File", command=self.load_file, fg_color="#ff006e")
        load_button.pack(padx=5, pady=5, fill="x")

        save_button = ctk.CTkButton(frame, text="Save Plot", command=self.save_plot, fg_color="#ff006e").pack(padx=5, pady=5, fill="x")

        check_label = ctk.CTkLabel(frame, text="Columns to plot", font=("Arial", 12), anchor='w')
        check_label.pack(pady=5, padx=5, fill="x")

        check_frame = ctk.CTkFrame(frame, corner_radius=10)
        check_frame.pack(pady=5, padx=5, fill='x')
        self.check_frame = check_frame

        self.update_checkboxes()

        crop_label = ctk.CTkLabel(frame, text="Crop Borders", font=("Arial", 12), anchor='w')
        crop_label.pack(pady=5, padx=5, fill="x")

        toggle_button = ctk.CTkSwitch(
        frame,
        text="Toggle Threshold",
        command=self.toggle_threshold,
        fg_color="#808080",
        progress_color="#ff006e")   
        toggle_button.pack(padx=5, pady=5)


    def toggle_threshold(self):
        if self.threshold == 0:
            self.threshold = 1
        else:
            self.threshold = 0
        print(self.threshold)
        self.update_plot()
        return

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("CSV files", "*.csv"), ("XML files", "*.xml"))
        )
        
        if file_path:
            self.data, self.x_unit, self.y_unit, self.file_name = plotting.load_data(file_path)
            self.generate_channel_metadata(self.data)
            self.update_checkboxes()
            self.update_plot()
        else:
            pass

    def generate_channel_metadata(self, data):
        if data.empty:
            return
        
        self.channel_metadata = []
        for i, column in enumerate(data.columns):
            # collect the unit, its the inside the parenthesis
            info = {
                "column_name": column,
                "column_color": COLORS[i],
                "selected": False,
            }
            self.channel_metadata.append(info)
        
    def update_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.destroy()

        for i, channel in enumerate(self.channel_metadata):
            checkbox = ctk.CTkCheckBox(
                self.check_frame, 
                text=channel["column_name"], 
                command=lambda index=i: self.activate_channel(index),
                checkbox_height=20, 
                checkbox_width=20, 
                fg_color=channel["column_color"],

            )
            checkbox.pack(pady=5, padx=5, expand=True, fill="x")
            self.checkboxes.append(checkbox)

    def activate_channel(self, index):
        self.channel_metadata[index]["selected"] = not self.channel_metadata[index]["selected"]
        self.update_plot()

    def update_plot(self):
        self.fig, self.current_data = plotting.plot_data(self.data, self.channel_metadata, self.threshold, self.x_unit, self.y_unit, self.file_name)

        if hasattr(self, 'canvas'):    
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)
        self.update_data_display()

    def update_data_display(self):
        for data_info in self.data_display_frame.winfo_children():
            data_info.destroy()

        self.data_metrics = []

        for channel in self.channel_metadata:
            if channel['selected']:
                column_name = channel['column_name']
                column_data = self.current_data[column_name]
                mean = column_data.mean()
                std = column_data.std()

                frame = ctk.CTkFrame(self.data_display_frame, corner_radius=10, border_width=2, border_color=channel["column_color"])
                frame.pack(side= "left", pady=5, padx=5, fill="x")
                
                label = ctk.CTkLabel(frame, text=f"{column_name}", font=("Arial", 14, "bold"), text_color=channel["column_color"]).pack(pady=5, padx=5)
                avg_label = ctk.CTkLabel(frame, text=f"Mean [{self.y_unit}]", font=("Arial", 12, "bold")).pack(pady=1, padx=1)

                avg_data_label = ctk.CTkLabel(frame, text=f"{mean}", font=("Arial", 12)).pack(pady=5, padx=5)

                std_label = ctk.CTkLabel(frame, text=f"Std [{self.y_unit}]", font=("Arial", 12, "bold")).pack(pady=5, padx=5)

                std_data_label = ctk.CTkLabel(frame, text=f"{std}", font=("Arial", 12)).pack(pady=5, padx=5)

                data_metric = {'name': column_name, 'mean': mean, 'std': std}
                self.data_metrics.append(data_metric)

    def find_unique_name(self, name, path, extension):
        #Function that checks if the name already exists in the folder, if it does, add a number to the end of the name
        i = 1
        while os.path.exists(f"{path}/{name}.{extension}"):
            name = name.split("(")[0]
            name = f"{name}({i})"
            i += 1
        return name

    def save_plot(self):        
        destination = f"plots/{self.file_name}"
        os.makedirs(destination, exist_ok=True)

        if self.fig:
            image_name = self.find_unique_name(self.file_name, destination, "png")
            self.fig.savefig(f"{destination}/{image_name}.png")

            txt_name = self.find_unique_name(self.file_name, destination, "txt")
            with open(f"{destination}/{txt_name}.txt", "w") as f:
                for data_metric in self.data_metrics:
                    f.write(f"{data_metric['name']}\n")
                    f.write(f"Mean: {data_metric['mean']} {self.y_unit}\n")
                    f.write(f"Std: {data_metric['std']} {self.y_unit}\n\n")
                    f.write("-----------------\n")

if __name__ == '__main__':
    app = App()
    app.mainloop()