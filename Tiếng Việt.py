import tkinter as tk
from tkinter import filedialog
import random
import pygame
import os
import pandas as pd
import copy

class Game:
    def __init__(self, root, appCon, settings, profile):
        self.appCon = appCon
        self.debug_mode = settings.debug_mode

        self.root = root

        self.test_mode = False
        
        self.profile = profile

        self.course = Course(self.profile.course_path)
        self.course.get_course_info()
        
        self.level = None
        self.level_progress = None
        self.item = None
        
        self.in_game = False

        self.label1 = tk.Label(self.root, text="", font=("Times", 48, 'bold'), wraplength=750, pady=20, bg="#2e2e2e", fg="#FFFFFF")
        self.label2 = tk.Label(self.root, text="", font=("Times", 36), wraplength=750, bg="#2e2e2e", fg="#FFFFFF")
        self.entry = tk.Entry(self.root, font=("Times", 48), bg="#444444", fg="#FFFFFF", insertbackground="white")

        self.button_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.enter_button = tk.Button(self.button_frame, text="Enter", command=self.sample_item, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.play_button = tk.Button(self.button_frame, text="Repeat", command=self.play_audio_helper, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

        self.bottom_left_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.return_button = tk.Button(self.bottom_left_frame, command=self.game_return, text="Return", width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

        self.levelselect_button = tk.Button(self.bottom_left_frame, command=self.level_select, text="Level Select", width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.test_button = tk.Button(self.bottom_left_frame, command=self.begin_test, text="Test", width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

        self.level_label = tk.Label(self.root, text="Level: ?/20", font=("Times", 18), bg="#2e2e2e", fg="#FFFFFF")

        self.level_progress_label = tk.Label(self.root, text="PRACTICE", font=("Times", 18, 'bold'), bg="#2e2e2e", fg="#FFFFFF")
        self.level_progress_label2 = tk.Label(self.root, text="1/?", font=("Times", 18, 'bold'), bg="#2e2e2e", fg="#FFFFFF")
        
        self.level_progress_label.config(fg="#FFFFFF")
        self.level_progress_label2.config(fg="#FFFFFF")

        self.entry.bind("<Return>", self.on_enter_pressed)
        self.entry.bind("<Control_L>", self.on_ctrl_pressed)
        
    def on_enter_pressed(self, event):
        self.sample_item()

    def on_ctrl_pressed(self, event):
        self.play_audio_helper()

    def display(self):
        self.label1.pack()
        self.label2.pack()
        self.entry.pack()
        self.button_frame.pack(pady=20)

        self.enter_button.pack(side=tk.LEFT, padx=10)
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.bottom_left_frame.pack(side=tk.BOTTOM, anchor="sw", pady=20, padx=10)
        self.return_button.pack(side=tk.LEFT, padx=10)
        self.levelselect_button.pack(side=tk.LEFT, padx=10)
        self.test_button.pack(side=tk.LEFT, padx=10)

        self.level_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-20)

        self.level_progress_label.place(relx=0.5, rely=1.0, anchor="s", y=-50)
        self.level_progress_label2.place(relx=0.5, rely=1.0, anchor="s", y=-20)

    def sample_item(self):
        entered_text = self.entry.get()

        #Correct
        if entered_text.rstrip() == self.item[0] or (self.debug_mode == 'True' and entered_text.rstrip() != "X"):
            if DEBUG: print("Correct Answer.")

            self.entry.config(fg="#FFFFFF")
            self.level_progress += 1

            if self.level_progress == len(self.level):
                
                if self.test_mode == True:
                    if DEBUG: print("Passed Test.")

                    if self.profile.current_level == self.profile.level_reached:
                        if DEBUG: print("Passed Highest Level.")
                        self.unlock_level()
                        return

                    else:
                        self.profile.current_level += 1
                        self.begin_test()
                        return

                else:
                    self.level_progress = 0
                    random.shuffle(self.level)

            self.item = self.level[self.level_progress]

            self.play_audio_helper()

            if self.test_mode == True:
                self.label1.config(text='--------')
            else:
                self.label1.config(text=self.item[0])

            self.label2.config(text=self.item[1])

            self.level_progress_label2.config(text=str(self.level_progress+1)+"/"+str(len(self.level)))
            
            self.entry.delete(0, tk.END)

        #Incorrect
        else:
            if DEBUG: print("Inorrect Answer.")

            if self.test_mode == True:
                self.begin_practice()
            else:
                self.entry.config(fg="#FF6347")

    def play_audio(self, text):
        path = self.course.course_path+"/audio/"+text.replace('/', '--').replace('\\', '__').replace('\t', '____').replace('?', '')+".wav"
        sound = pygame.mixer.Sound(path)
        sound.play()

    def play_audio_helper(self):
        self.play_audio(self.item[0])
        if DEBUG: print("playing audio:", self.item[0])

    def begin_practice(self):
        self.test_mode = False

        self.entry.delete(0, tk.END)
        self.entry.config(fg="#FFFFFF")

        self.level_progress = 0
        self.level = copy.deepcopy(self.course.lessons[self.profile.current_level-1])
        random.shuffle(self.level)

        self.item = self.level[self.level_progress]
        self.label1.config(text=self.item[0])
        self.label2.config(text=self.item[1])

        self.level_progress_label.config(text="PRACTICE", fg="#FFFFFF")
        self.level_progress_label2.config(fg="#FFFFFF")

        self.level_progress_label2.config(text=str(self.level_progress+1)+"/"+str(len(self.level)))
        self.level_label.config(text=str(self.profile.current_level)+"/"+str(self.profile.total_levels))

        self.play_audio_helper()

    def begin_test(self):
        self.test_mode = True

        self.level_progress_label.config(text="TEST", fg="#FF6347")
        self.level_progress_label2.config(fg="#FF6347")

        self.entry.delete(0, tk.END)
        self.entry.config(fg="#FFFFFF")

        self.level_progress = 0
        self.level = copy.deepcopy(self.course.lessons[self.profile.current_level-1])
        random.shuffle(self.level)

        self.item = self.level[self.level_progress]
        self.label1.config(text='--------')
        self.label2.config(text=self.item[1])

        self.level_progress_label2.config(text=str(self.level_progress+1)+"/"+str(len(self.level)))
        self.level_label.config(text=str(self.profile.current_level)+"/"+str(self.profile.total_levels))

        self.play_audio_helper()

        if DEBUG: print("Testing with", self.profile.name, self.profile.current_level)

    def unlock_level(self):
        profiles_df = pd.read_csv("./profiles/profiles.csv")

        if self.profile.level_reached == self.profile.total_levels:
            if DEBUG: print("Course Completed.")

            profiles_df.loc[profiles_df['name'] == self.profile.name, 'completed'] = True
            profiles_df.to_csv("./profiles/profiles.csv", index=False)

            self.begin_practice()
        
        else:
            self.profile.level_reached += 1
            self.profile.current_level += 1

            profiles_df.loc[profiles_df['name'] == self.profile.name, 'level_reached'] += 1
            profiles_df.to_csv("./profiles/profiles.csv", index=False)

            self.begin_practice()

    def level_select(self):
        self.label1.destroy()
        self.label2.destroy()
        self.button_frame.destroy()
        self.bottom_left_frame.destroy()
        self.level_progress_label.destroy()
        self.level_progress_label2.destroy()
        self.level_label.destroy()
        self.entry.destroy()

        self.appCon.game_transition(['level_select', self.profile])

    def game_return(self):
        self.label1.destroy()
        self.label2.destroy()
        self.button_frame.destroy()
        self.bottom_left_frame.destroy()
        self.level_progress_label.destroy()
        self.level_progress_label2.destroy()
        self.level_label.destroy()
        self.entry.destroy()

        self.appCon.game_transition(['return', None])

class Profile:
    def __init__(self, name):
        self.name = name
        self.course_path = None
        self.total_levels = None
        self.level_reached = None
        self.current_level = None

    def get_profile_info(self):
        profiles_df = pd.read_csv("./profiles/profiles.csv")

        profile = (profiles_df[profiles_df['name'] == self.name].iloc[0]).tolist()
        self.course_path = profile[1]
        self.total_levels = profile[2]
        self.level_reached = profile[3]
        self.current_level = self.level_reached

class Course:
    def __init__(self, course_path):
        self.course_path = course_path
        self.total_levels = None
        self.lessons = []
        self.lesson_names = None

    def get_course_info(self):
        lesson_plan_df = pd.read_csv(self.course_path+"/lesson_plan.csv")
        course_info_df = pd.read_csv(self.course_path+"/course_info.csv")

        self.total_levels = len(course_info_df)

        for i in range(1, self.total_levels+1):
            self.lessons.append((lesson_plan_df[lesson_plan_df['lesson'] == i])[['vi', 'en']].values.tolist())

class LevelSelectMenu:
    def __init__(self, root, appCon, profile):
        self.appCon = appCon

        self.profile = profile

        self.select_frame = tk.Frame(root, bg="#2e2e2e")

        self.canvas = tk.Canvas(self.select_frame, bg="#2e2e2e", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.select_frame, orient="vertical", command=self.canvas.yview, bg="#2e2e2e")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.canvas, bg="#2e2e2e")
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")

    def display(self):
        self.select_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        levels = list(range(1, self.profile.level_reached+1))

        for level in levels:
            level_button = tk.Button(self.button_frame, text=str(level), command=lambda lvl=level: self.level_selected(lvl), width=25, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
            level_button.pack(pady=10, padx=10, fill=tk.X)

        self.button_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.canvas.create_window((self.canvas.winfo_width() // 2, 0), window=self.button_frame, anchor="n")

    def level_selected(self, lvl):
        self.select_frame.destroy()

        self.profile.current_level = lvl

        self.appCon.level_select_menu_transition(self.profile)

class MainMenu:
    def __init__(self, root, appCon):
        self.appCon = appCon

        self.menu_label = tk.Label(root, text="Tiếng Việt", font=("Times", 72, 'bold'), wraplength=750, pady=20, bg="#2e2e2e", fg="#FFFFFF")
        
        self.menu_button_frame = tk.Frame(root, bg="#2e2e2e")
        self.start_button = tk.Button(self.menu_button_frame, text="Start", command=self.select, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.create_button = tk.Button(self.menu_button_frame, text="Create", command=self.create, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.delete_button = tk.Button(self.menu_button_frame, text="Delete", command=self.delete, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

        self.menu_button_frame2 = tk.Frame(root, bg="#2e2e2e")
        self.settings_button = tk.Button(self.menu_button_frame2, text="Settings", command=self.settings, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

    def display(self):
        self.menu_label.pack(pady=25)
        self.menu_button_frame.pack(pady=25)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.create_button.pack(side=tk.LEFT, padx=10)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.menu_button_frame2.pack(pady=20)
        self.settings_button.pack(side=tk.LEFT, padx=10)

    def undisplay(self):
        self.menu_label.pack_forget()
        self.menu_button_frame.pack_forget()
        self.start_button.pack_forget()
        self.create_button.pack_forget()
        self.delete_button.pack_forget()

        self.menu_button_frame2.pack_forget()
        self.settings_button.pack_forget()

    def select(self):
        self.undisplay()
        self.appCon.main_menu_transition("select")

    def create(self):
        self.undisplay()
        self.appCon.main_menu_transition("create")

    def delete(self):
        self.undisplay()
        self.appCon.main_menu_transition("delete")

    def settings(self):
        self.undisplay()
        self.appCon.main_menu_transition("settings")

class SelectMenu:
    def __init__(self, root, appCon):
        self.appCon = appCon

        self.select_frame = tk.Frame(root, bg="#2e2e2e")

        self.canvas = tk.Canvas(self.select_frame, bg="#2e2e2e", bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.select_frame, orient="vertical", command=self.canvas.yview, bg="#2e2e2e")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.button_frame = tk.Frame(self.canvas, bg="#2e2e2e")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.bottom_left_frame = tk.Frame(self.canvas, bg="#2e2e2e")
        self.return_button = tk.Button(self.bottom_left_frame, command=self.select_menu_return, text="Return", width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

    def display(self):
        if DEBUG: print("Displaying Profile Selection")

        self.select_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")

        self.button_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.create_window((self.canvas.winfo_width() // 2, 0), window=self.button_frame, anchor="n")
        
        self.bottom_left_frame.pack(side=tk.BOTTOM, anchor="sw", pady=0, padx=10)
        self.return_button.pack(side=tk.LEFT, padx=10)

        profiles_df = pd.read_csv("./profiles/profiles.csv")
        profiles = profiles_df['name'].tolist()
        completeds = profiles_df['completed'].tolist()

        for i, profile in enumerate(profiles):
            profile_button = tk.Button(self.button_frame, text=profile, command=lambda name=profile: self.profile_selected(name, self.select_frame), width=25, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

            if completeds[i] == True:
                profile_button.config(bg="#9c7114", activebackground="#c48e1a")

            profile_button.pack(pady=10, padx=10, fill=tk.X)

    def select_menu_return(self):
        self.select_frame.destroy()

        self.appCon.select_menu_transition("return", None)

    def profile_selected(self, name, widget):
        widget.destroy()

        self.appCon.select_menu_transition("profile_selected", name)

class CreateMenu:
    def __init__(self, root, appCon):
        self.appCon = appCon

        self.entry_frame = tk.Frame(root, bg="#2e2e2e")

        self.label1 = tk.Label(self.entry_frame, text="Profile Name:", font=("Times", 32), bg="#2e2e2e", fg="#FFFFFF")
        self.label2 = tk.Label(self.entry_frame, text="Course Path:", font=("Times", 32), bg="#2e2e2e", fg="#FFFFFF")

        self.label1.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.label2.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.name_var = tk.StringVar(value="")
        self.course_path_var = tk.StringVar(value="./courses/my_course")

        self.name_entry = tk.Entry(self.entry_frame, textvariable=self.name_var, font=("Times", 32), bg="#444444", fg="#FFFFFF", insertbackground="white")
        self.course_path_entry = tk.Entry(self.entry_frame, textvariable=self.course_path_var, font=("Times", 18), width=50, bg="#444444", fg="#FFFFFF", insertbackground="white")
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.course_path_entry.grid(row=1, column=1, padx=10, pady=10)

        self.choose_folder_button = tk.Button(self.entry_frame, text="Choose", command=self.choose_folder, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.choose_folder_button.grid(row=1, column=2, padx=10, pady=10)

        self.form_button_frame = tk.Frame(root, bg="#2e2e2e")
        self.submit_button = tk.Button(self.form_button_frame, text="Submit", command=lambda: self.submit_create([self.name_entry, self.course_path_entry, self.label1, self.label2, self.entry_frame, self.submit_button, self.cancel_button, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.cancel_button = tk.Button(self.form_button_frame, text="Cancel", command=lambda: self.cancel_create([self.name_entry, self.course_path_entry, self.label1, self.label2, self.entry_frame, self.submit_button, self.cancel_button, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

    def display(self):
        self.entry_frame.pack(pady=20)
        self.form_button_frame.pack(pady=20)
        self.submit_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button.pack(side=tk.LEFT, padx=10)

    def choose_folder(self):
        folder_path = filedialog.askdirectory(title="Select a Folder", initialdir='./courses/')

        if folder_path:
            self.course_path_entry.delete(0, tk.END)
            self.course_path_entry.insert(0, folder_path)

    def submit_create(self, widgets):
        name = self.name_entry.get()
        path = self.course_path_entry.get()

        profiles_df = pd.read_csv("./profiles/profiles.csv")

        course_df = pd.read_csv(path+"/course_info.csv")
        total_levels = len(course_df)

        #input error
        if (not name) or (not path):
            self.appCon.create_menu_transition()

        #input error
        if name in profiles_df['name']:
            self.appCon.create_menu_transition()

        new_df = pd.DataFrame({'name': [name], 'course_path': [path], 'total_levels': [total_levels], 'level_reached': [1], 'completed': [False]})

        profiles_df = pd.concat([profiles_df, new_df])

        profiles_df.to_csv("./profiles/profiles.csv", index=False)

        for widget in widgets:
            widget.destroy()

        self.appCon.create_menu_transition()

    def cancel_create(self, widgets):
        for widget in widgets:
            widget.destroy()
    
        self.appCon.create_menu_transition()

class DeleteMenu:
    def __init__(self, root, appCon):
        self.appCon = appCon

        self.entry_frame = tk.Frame(root, bg="#2e2e2e")
        self.entry_frame.pack(pady=20)

        self.label1 = tk.Label(self.entry_frame, text="Name:", font=("Times", 32), bg="#2e2e2e", fg="#FFFFFF")

        self.name_var = tk.StringVar(value="")

        self.name_entry = tk.Entry(self.entry_frame, textvariable=self.name_var, font=("Times", 32), bg="#444444", fg="#FFFFFF", insertbackground="white")

        self.form_button_frame = tk.Frame(root, bg="#2e2e2e")
        self.submit_button = tk.Button(self.form_button_frame, text="Delete", command=lambda: self.submit_delete([self.name_entry, self.label1, self.entry_frame, self.submit_button, self.cancel_button, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.cancel_button = tk.Button(self.form_button_frame, text="Cancel", command=lambda: self.cancel_delete([self.name_entry, self.label1, self.entry_frame, self.submit_button, self.cancel_button, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

        self.label1.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

    def display(self):
        self.entry_frame.pack(pady=20)
        self.form_button_frame.pack(pady=20)
        self.submit_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button.pack(side=tk.LEFT, padx=10)

    def submit_delete(self, widgets):
        name = self.name_entry.get()

        profiles_df = pd.read_csv("./profiles/profiles.csv")
        profiles_df = profiles_df[profiles_df['name'] != name]
        profiles_df.to_csv("./profiles/profiles.csv", index=False)

        for widget in widgets:
            widget.destroy()

        self.appCon.delete_menu_transition()

    def cancel_delete(self, widgets):
        for widget in widgets:
            widget.destroy()

        self.appCon.delete_menu_transition()

class SettingsMenu:
    def __init__(self, root, appCon, settings):
        self.debug_mode = settings.debug_mode
        self.settings = settings

        self.appCon = appCon

        self.entry_frame = tk.Frame(root, bg="#2e2e2e")

        #Debug Mode
        self.label2 = tk.Label(self.entry_frame, text="Debug Mode:", font=("Times", 32), bg="#2e2e2e", fg="#FFFFFF")
        self.label2.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.debug_mode_button = tk.Button(self.entry_frame, text=self.debug_mode, command=self.toggle_debug_mode, width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.debug_mode_button.grid(row=0, column=1, padx=10, pady=10)

        self.form_button_frame = tk.Frame(root, bg="#2e2e2e")
        self.save_button = tk.Button(self.form_button_frame, text="Submit", command=lambda: self.save_settings([self.entry_frame, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")
        self.cancel_button = tk.Button(self.form_button_frame, text="Cancel", command=lambda: self.cancel_settings([self.entry_frame, self.form_button_frame]), width=10, height=2, font=("Times", 18), bg="#444444", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF")

    def toggle_debug_mode(self):
        if self.debug_mode_button.cget('text') == "True":
            self.debug_mode_button.config(text="False")
        else:
            self.debug_mode_button.config(text="True")

    def display(self):
        self.entry_frame.pack(pady=20)

        self.form_button_frame.pack(pady=20)
        self.save_button.pack(side=tk.LEFT, padx=0)
        self.cancel_button.pack(side=tk.RIGHT, padx=10)
        
    def save_settings(self, widgets):
        with open("./cfg/settings", 'w') as file:
            file.write("debug_mode="+self.debug_mode_button.cget('text')+'\n')

        self.settings.debug_mode = self.debug_mode_button.cget('text')

        for widget in widgets:
            widget.destroy()
    
        self.appCon.settings_menu_transition()

    def cancel_settings(self, widgets):
        for widget in widgets:
            widget.destroy()
    
        self.appCon.settings_menu_transition()

class Settings:
    def __init__(self):
        self.debug_mode = None

    def update_settings(self):
        with open("./cfg/settings", 'r') as file:
            lines = file.readlines()

        self.debug_mode = lines[0][:-1].replace("debug_mode=", '')

class ApplicationController:
    def __init__(self, root):
        self.root = root
        
        self.settings = Settings()
        self.settings.update_settings()
        self.main_menu = MainMenu(root, self)

    def main_menu_display(self):
        if DEBUG: print("Displaying Main Menu...")

        self.main_menu.display()
    
    def main_menu_transition(self, type):
        if type == "select":
            select_menu = SelectMenu(self.root, self)
            select_menu.display()

        elif type == "create":
            create_menu = CreateMenu(self.root, self)
            create_menu.display()

        elif type == "delete":
            delete_menu = DeleteMenu(self.root, self)
            delete_menu.display()

        elif type == "settings":
            settings_menu = SettingsMenu(self.root, self, self.settings)
            settings_menu.display()

    def select_menu_transition(self, type, arg):
        if type == "profile_selected":
            if DEBUG: print("Profile Selected:", arg)
            profile = Profile(arg)
            profile.get_profile_info()

            game = Game(self.root, self, self.settings, profile)
            game.display()
            game.begin_practice()

        elif type == "return":
            if DEBUG: print("return")
            self.main_menu_display()

    def create_menu_transition(self):
        self.main_menu.display()

    def delete_menu_transition(self):
        self.main_menu.display()

    def settings_menu_transition(self):
        self.main_menu.display()

    def game_transition(self, args):
        if args[0] == "return":
            self.main_menu_display()
        
        elif args[0] == "level_select":
            level_select_menu = LevelSelectMenu(self.root, self, args[1])
            level_select_menu.display()

    def level_select_menu_transition(self, profile):
        game = Game(self.root, self, self.settings, profile)
        game.display()
        game.begin_practice()

def block_f10(event):
    return "break"

DEBUG = False
def main():
    pygame.mixer.init()
    random.seed(None)

    root = tk.Tk()
    root.configure(bg="#2e2e2e")
    root.title("Tiếng Việt")
    root.minsize(1200, 750)
    root.geometry("1200x750")

    root.bind("<F10>", block_f10)

    controller = ApplicationController(root)
    controller.main_menu_display()

    root.mainloop()

if __name__ == "__main__":
    main()