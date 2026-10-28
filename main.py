import re
import csv
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import database
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# -------------------- THEME --------------------
NAVY = "#0b1120"
SIDEBAR = "#101a2e"
PANEL = "#17243b"
PANEL_LIGHT = "#1d2e49"
BLUE = "#3b82f6"
BLUE_HOVER = "#2563eb"
CYAN = "#38bdf8"
WHITE = "#f1f5f9"
MUTED = "#9caec7"
GREEN = "#34d399"
RED = "#fb7185"
BORDER = "#2a3b55"

DARK_THEME = {
    "NAVY": "#0b1120", "SIDEBAR": "#101a2e",
    "PANEL": "#17243b", "PANEL_LIGHT": "#1d2e49",
    "BLUE": "#3b82f6", "BLUE_HOVER": "#2563eb",
    "CYAN": "#38bdf8", "WHITE": "#f1f5f9",
    "MUTED": "#9caec7", "GREEN": "#34d399",
    "RED": "#fb7185", "BORDER": "#2a3b55",
}
LIGHT_THEME = {
    "NAVY": "#f1f5f9", "SIDEBAR": "#ffffff",
    "PANEL": "#ffffff", "PANEL_LIGHT": "#e2e8f0",
    "BLUE": "#2563eb", "BLUE_HOVER": "#1d4ed8",
    "CYAN": "#0369a1", "WHITE": "#172033",
    "MUTED": "#526176", "GREEN": "#047857",
    "RED": "#be123c", "BORDER": "#cbd5e1",
}
class QuizManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizFlow | Quiz Management System")
        self.root.geometry("1180x760")
        self.root.minsize(950, 650)
        self.root.configure(bg=NAVY)
        database.initialize_database()
        database.initialize_student_accounts()
        self.student_name = ""
        self.student_username = ""
        self.questions = []
        self.answers = {}
        self.current_index = 0
        self.remaining_seconds = 120
        self.timer_job = None
        self.quiz_active = False
        self.last_score = 0
        self.last_total = 0
        self.last_percentage = 0.0
        self.quiz_mode = "MCQ Quiz"
        self.quiz_category = "All Categories"
        self.tf_claims = {}
        self.theme_mode = "dark"
        self.configure_styles()
        self.build_shell()
        self.show_student_auth()

    def show_student_auth(self):
        """Display the themed QuizFlow student sign-in and registration window."""
        dialog = tk.Toplevel(self.root)
        dialog.title("QuizFlow | Welcome")
        dialog.configure(bg=NAVY)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.protocol("WM_DELETE_WINDOW", self.root.destroy)
        # A two-panel layout gives the login screen a desktop-app feel.
        shell = tk.Frame(dialog, bg=PANEL, bd=0)
        shell.pack(fill="both", expand=True, padx=12, pady=12)
        brand = tk.Frame(shell, bg=SIDEBAR, width=300)
        brand.pack(side="left", fill="y")
        brand.pack_propagate(False)
        tk.Label(
            brand, text="Q", bg=BLUE, fg="white",
            font=("Segoe UI", 25, "bold"), width=2, height=1
        ).pack(anchor="w", padx=26, pady=(36, 16))
        tk.Label(
            brand, text="QuizFlow", bg=SIDEBAR, fg=CYAN,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w", padx=26)
        tk.Label(
            brand, text="LEARN. PRACTICE. IMPROVE.",
            bg=SIDEBAR, fg=MUTED, font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=28, pady=(5, 26))
        tk.Label(
            brand, text="Your next achievement\nstarts with one quiz.",
            bg=SIDEBAR, fg=WHITE, justify="left", wraplength=245,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=26, pady=(0, 12))
        tk.Label(
            brand,
            text="Build confidence, practise your skills, "
                 "and track your progress with every attempt.",
            bg=SIDEBAR, fg=MUTED, justify="left", wraplength=235,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=26)
        tk.Label(
            brand, text="STUDENT LEARNING PORTAL",
            bg=SIDEBAR, fg=CYAN, font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", anchor="w", padx=26, pady=26)
        form = tk.Frame(shell, bg=PANEL, padx=32, pady=26)
        form.pack(side="left", fill="both", expand=True)
        mode = {"value": "login"}
        visibility = {"shown": False}
        tk.Label(
            form, text="STUDENT ACCOUNT", bg=PANEL, fg=CYAN,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        heading = tk.Label(
            form, text="Welcome back", bg=PANEL, fg=WHITE,
            font=("Segoe UI", 22, "bold")
        )
        heading.pack(anchor="w", pady=(5, 4))
        subtitle = tk.Label(
            form, text="Sign in to continue to your dashboard.",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9)
        )
        subtitle.pack(anchor="w", pady=(0, 18))
        fields = tk.Frame(form, bg=PANEL)
        fields.pack(fill="x")
        def make_field(parent, label_text, secret=False):
            group = tk.Frame(parent, bg=PANEL)
            tk.Label(
                group, text=label_text, bg=PANEL, fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(0, 6))
            entry = tk.Entry(
                group, bg=PANEL_LIGHT, fg=WHITE,
                insertbackground=WHITE, relief="flat",
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=BLUE, font=("Segoe UI", 11),
                show="*" if secret else ""
            )
            entry.pack(fill="x", ipady=9)
            return group, entry
        username_group, username_entry = make_field(fields, "Username")
        username_group.pack(fill="x", pady=(0, 13))
        name_group, display_entry = make_field(fields, "Full name")
        # Only show this field in registration mode.
        name_group.pack_forget()
        password_group, password_entry = make_field(
            fields, "Password", secret=True
        )
        password_group.pack(fill="x", pady=(0, 5))
        confirm_group, confirm_entry = make_field(
            fields, "Confirm password", secret=True
        )
        confirm_group.pack_forget()
        def toggle_password():
            visibility["shown"] = not visibility["shown"]
            password_entry.configure(
                show="" if visibility["shown"] else "*"
            )
            reveal_button.configure(
                text="Hide" if visibility["shown"] else "Show"
            )
            password_entry.focus_set()
        reveal_row = tk.Frame(form, bg=PANEL)
        reveal_row.pack(fill="x", pady=(0, 7))
        reveal_button = tk.Button(
            reveal_row, text="Show", command=toggle_password,
            bg=PANEL, fg=CYAN, activebackground=PANEL,
            activeforeground=CYAN, relief="flat", bd=0,
            cursor="hand2", font=("Segoe UI", 9, "bold")
        )
        reveal_button.pack(side="right")
        status = tk.Label(
            form, text="", bg=PANEL, fg=RED,
            font=("Segoe UI", 9), justify="left",
            wraplength=350, anchor="w"
        )
        status.pack(fill="x", pady=(2, 7))
        def set_status(text, color=None):
            status.configure(text=text, fg=color or RED)
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                set_status("Enter your username and password.")
                return
            try:
                authenticated_name = database.authenticate_student(
                    username, password
                )
            except Exception as exc:
                messagebox.showerror(
                    "Login error",
                    f"Could not verify your account.\n\n{exc}",
                    parent=dialog
                )
                return
            if authenticated_name is None:
                set_status("Username or password is incorrect.")
                password_entry.delete(0, tk.END)
                password_entry.focus_set()
                return
            self.student_username = username.lower()
            self.student_name = authenticated_name
            dialog.grab_release()
            dialog.destroy()
            self.show_dashboard()
        def register():
            username = username_entry.get().strip()
            display_name = display_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_entry.get()
            if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username):
                set_status(
                    "Use 3-30 characters: letters, numbers, dot, "
                    "underscore or hyphen."
                )
                return
            if not display_name:
                set_status("Enter your full name.")
                display_entry.focus_set()
                return
            if len(password) < 8:
                set_status("Choose a password with at least 8 characters.")
                password_entry.focus_set()
                return
            if password != confirm_password:
                set_status("Passwords do not match. Please try again.")
                confirm_entry.delete(0, tk.END)
                confirm_entry.focus_set()
                return
            try:
                created = database.register_student(
                    username, display_name, password
                )
            except Exception as exc:
                messagebox.showerror(
                    "Registration error",
                    f"Could not create the account.\n\n{exc}",
                    parent=dialog
                )
                return
            if not created:
                set_status("That username is already registered.")
                username_entry.focus_set()
                return
            self.student_username = username.lower()
            self.student_name = display_name
            messagebox.showinfo(
                "Account created",
                "Your QuizFlow account is ready. Welcome!",
                parent=dialog
            )
            dialog.grab_release()
            dialog.destroy()
            self.show_dashboard()
        primary_button = tk.Button(
            form, text="Sign In", command=login,
            bg=BLUE, fg="white", activebackground=BLUE_HOVER,
            activeforeground="white", relief="flat", bd=0,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            pady=11
        )
        primary_button.pack(fill="x", pady=(3, 12))
        switch_row = tk.Frame(form, bg=PANEL)
        switch_row.pack(fill="x")
        switch_text = tk.Label(
            switch_row, text="New to QuizFlow?", bg=PANEL,
            fg=MUTED, font=("Segoe UI", 9)
        )
        switch_text.pack(side="left")
        def set_mode(new_mode):
            mode["value"] = new_mode
            status.configure(text="")
            password_entry.delete(0, tk.END)
            visibility["shown"] = False
            password_entry.configure(show="*")
            reveal_button.configure(text="Show")
            if new_mode == "register":
                heading.configure(text="Create account")
                subtitle.configure(
                    text="Create your student account to get started."
                )
                name_group.pack(fill="x", pady=(0, 13), before=password_group)
                confirm_group.pack(fill="x", pady=(0, 13), after=password_group)
                primary_button.configure(text="Create Account", command=register)
                switch_text.configure(text="Already have an account?")
                switch_button.configure(text="Sign in", command=lambda: set_mode("login"))
            else:
                heading.configure(text="Welcome back")
                subtitle.configure(
                    text="Sign in to continue to your dashboard."
                )
                name_group.pack_forget()
                confirm_group.pack_forget()
                confirm_entry.delete(0, tk.END)
                primary_button.configure(text="Sign In", command=login)
                switch_text.configure(text="New to QuizFlow?")
                switch_button.configure(
                    text="Create account",
                    command=lambda: set_mode("register")
                )
            dialog.update_idletasks()
            resize_dialog()
        switch_button = tk.Button(
            switch_row, text="Create account",
            command=lambda: set_mode("register"),
            bg=PANEL, fg=CYAN, activebackground=PANEL,
            activeforeground=CYAN, relief="flat", bd=0,
            cursor="hand2", font=("Segoe UI", 9, "bold")
        )
        switch_button.pack(side="left", padx=(5, 0))
        tk.Label(
            form, text="Your progress, saved securely.",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(24, 0))
        def resize_dialog():
            dialog.update_idletasks()
            width = 820
            height = 760 if mode["value"] == "register" else 550
            screen_w = dialog.winfo_screenwidth()
            screen_h = dialog.winfo_screenheight()
            x = max(0, (screen_w - width) // 2)
            y = max(0, (screen_h - height) // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        set_mode("login")
        resize_dialog()
        username_entry.focus_set()
        dialog.bind("<Return>", lambda _event: (
            register() if mode["value"] == "register" else login()
        ))
        dialog.grab_set()
        dialog.wait_visibility()
        dialog.focus_force()
    def toggle_theme(self):
        global NAVY, SIDEBAR, PANEL, PANEL_LIGHT
        global BLUE, BLUE_HOVER, CYAN, WHITE
        global MUTED, GREEN, RED, BORDER
        old_title = self.page_title.cget("text")
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        palette = LIGHT_THEME if self.theme_mode == "light" else DARK_THEME
        NAVY = palette["NAVY"]
        SIDEBAR = palette["SIDEBAR"]
        PANEL = palette["PANEL"]
        PANEL_LIGHT = palette["PANEL_LIGHT"]
        BLUE = palette["BLUE"]
        BLUE_HOVER = palette["BLUE_HOVER"]
        CYAN = palette["CYAN"]
        WHITE = palette["WHITE"]
        MUTED = palette["MUTED"]
        GREEN = palette["GREEN"]
        RED = palette["RED"]
        BORDER = palette["BORDER"]
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=NAVY)
        self.configure_styles()
        self.build_shell()
        if self.quiz_active:
            self.show_question()
        elif old_title == "Admin Panel":
            self.show_admin()
        elif old_title == "Leaderboard":
            self.show_leaderboard()
        elif old_title == "Performance Analytics":
            self.show_analytics()
        elif old_title == "Choose Your Quiz":
            self.start_quiz_prompt()
        elif old_title == "Quiz Result":
            self.show_result()
        else:
            self.show_dashboard()
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=WHITE,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=SIDEBAR,
            foreground=CYAN,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=8
        )
        style.map(
            "Treeview",
            background=[("selected", BLUE)],
            foreground=[("selected", "white")]
        )
        style.configure(
            "TCombobox",
            fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT,
            foreground=WHITE,
            arrowcolor=WHITE
        )
        style.configure(
            "QuizCategory.TCombobox",
            fieldbackground=PANEL,
            background=PANEL_LIGHT,
            foreground=WHITE,
            arrowcolor=CYAN,
            padding=6
        )
        style.map(
            "QuizCategory.TCombobox",
            fieldbackground=[("readonly", PANEL)],
            foreground=[("readonly", WHITE)],
            selectbackground=[("readonly", BLUE)],
            selectforeground=[("readonly", WHITE)]
        )
    def button(self, parent, text, command, primary=False, width=None):
        bg = BLUE if primary else PANEL_LIGHT
        active = BLUE_HOVER if primary else "#304563"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=WHITE,
            activebackground=active,
            activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=15,
            pady=10,
            width=width
        )
    def label(self, parent, text, size=11, color=WHITE, bold=False, **kwargs):
        return tk.Label(
            parent,
            text=text,
            bg=kwargs.pop("bg", PANEL),
            fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            **kwargs
        )
    def card(self, parent, padding=18):
        frame = tk.Frame(
            parent, bg=PANEL, padx=padding, pady=padding,
            highlightbackground=BORDER, highlightthickness=1
        )
        return frame
    def clear_content(self):
        if self.timer_job is not None and not self.quiz_active:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None
        for widget in self.content.winfo_children():
            widget.destroy()
    def build_shell(self):
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(27, 32))
        tk.Label(
            brand, text="QF", bg=BLUE, fg="white",
            font=("Segoe UI", 18, "bold"), width=3, height=1
        ).pack(side="left", padx=(0, 10))
        tk.Label(
            brand, text="QuizFlow", bg=SIDEBAR, fg=WHITE,
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")
        tk.Label(
            self.sidebar, text="WORKSPACE", bg=SIDEBAR, fg=MUTED,
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill="x", padx=22, pady=(0, 8))
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Take a Quiz", self.start_quiz_prompt),
            ("Performance", self.show_analytics),
            ("Leaderboard", self.show_leaderboard),
            ("Admin Panel", self.admin_login),
        ]
        for text, command in nav_items:
            btn = tk.Button(
                self.sidebar,
                text="   " + text,
                command=command,
                anchor="w",
                bg=SIDEBAR,
                fg=MUTED,
                activebackground=PANEL_LIGHT,
                activeforeground=WHITE,
                font=("Segoe UI", 11),
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=14,
                pady=13
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[text] = btn
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=18, pady=22
        )
        tk.Label(
            self.sidebar,
            text="PYTHON | TKINTER\nSQLITE DATABASE",
            bg=SIDEBAR,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left"
        ).pack(side="bottom", anchor="w", padx=22, pady=22)
        main_area = tk.Frame(self.root, bg=NAVY)
        main_area.pack(side="left", fill="both", expand=True)
        self.topbar = tk.Frame(
            main_area, bg=NAVY, height=70,
            highlightbackground=BORDER, highlightthickness=0
        )
        self.topbar.pack(fill="x", padx=28, pady=(12, 0))
        self.topbar.pack_propagate(False)
        self.page_title = tk.Label(
            self.topbar, text="Dashboard",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 20, "bold")
        )
        self.page_title.pack(side="left", anchor="center")
        self.top_status = tk.Label(
            self.topbar, text="SYSTEM READY",
            bg=NAVY, fg=GREEN, font=("Segoe UI", 9, "bold")
        )
        self.top_status.pack(side="right", anchor="center")
        self.theme_button = tk.Button(
            self.topbar,
            text=("Light Mode" if self.theme_mode == "dark" else "Dark Mode"),
            command=self.toggle_theme,
            bg=PANEL_LIGHT,
            fg=WHITE,
            activebackground=BLUE_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=7,
        )
        self.theme_button.pack(side="right", padx=(0, 12))
        self.content = tk.Frame(main_area, bg=NAVY)
        self.content.pack(fill="both", expand=True, padx=28, pady=18)
    def set_page(self, title, active=None):
        self.page_title.config(text=title)
        for name, btn in self.nav_buttons.items():
            if name == active:
                btn.config(bg=BLUE, fg=WHITE)
            else:
                btn.config(bg=SIDEBAR, fg=MUTED)
    def show_dashboard(self):
        if self.quiz_active:
            if not messagebox.askyesno(
                "Leave quiz",
                "Leave the current quiz? This attempt will not be saved."
            ):
                return
            self.quiz_active = False
        self.clear_content()
        self.set_page("Dashboard", "Dashboard")
        questions = database.get_questions()
        results = database.get_results_for_student(
            self.student_username, self.student_name
        )
        attempts = len(results)
        average = sum(row[4] for row in results) / attempts if attempts else 0
        best = max((row[4] for row in results), default=0)
        # Welcome banner
        hero = tk.Frame(
            self.content, bg=PANEL, padx=24, pady=19,
            highlightbackground=BORDER, highlightthickness=1
        )
        hero.pack(fill="x", pady=(0, 16))
        hero_left = tk.Frame(hero, bg=PANEL)
        hero_left.pack(side="left", fill="both", expand=True)
        tk.Label(
            hero_left,
            text=f"Welcome back, {self.student_name}!",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 21, "bold"),
            anchor="w"
        ).pack(anchor="w")
        tk.Label(
            hero_left,
            text="Your learning journey, all in one place.",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 10),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))
        self.button(
            hero, "Start a Quiz", self.start_quiz_prompt, True
        ).pack(side="right", padx=(12, 0), pady=5)
        # Key performance indicators
        stats = tk.Frame(self.content, bg=NAVY)
        stats.pack(fill="x", pady=(0, 16))
        self.stat_card(stats, "QUESTIONS AVAILABLE", str(len(questions)), CYAN)
        self.stat_card(stats, "QUIZ ATTEMPTS", str(attempts), BLUE)
        self.stat_card(stats, "AVERAGE SCORE", f"{average:.1f}%", GREEN)
        self.stat_card(stats, "PERSONAL BEST", f"{best:.1f}%", "#c084fc")
        # Lower dashboard: recent activity and score distribution
        lower = tk.Frame(self.content, bg=NAVY)
        lower.pack(fill="both", expand=True)
        recent = self.card(lower, 18)
        recent.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(
            recent, text="Recent Attempts",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")
        tk.Label(
            recent, text="Your latest quiz results",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 12))
        if not results:
            tk.Label(
                recent,
                text="No attempts yet.\\nComplete your first quiz to see your progress here.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 10),
                justify="left", wraplength=300
            ).pack(anchor="w", pady=(8, 12))
            self.button(
                recent, "Explore Quiz Modes", self.start_quiz_prompt, True
            ).pack(anchor="w", pady=(4, 0))
        else:
            for row in results[:5]:
                line = tk.Frame(recent, bg=PANEL)
                line.pack(fill="x", pady=6)
                tk.Frame(line, bg=BORDER, height=1).pack(
                    side="bottom", fill="x", pady=(7, 0)
                )
                tk.Label(
                    line, text=str(row[1]),
                    bg=PANEL, fg=WHITE,
                    font=("Segoe UI", 10, "bold"),
                    anchor="w", wraplength=220
                ).pack(side="left", fill="x", expand=True)
                score_color = GREEN if row[4] >= 50 else RED
                tk.Label(
                    line, text=f"{row[4]:.1f}%",
                    bg=PANEL, fg=score_color,
                    font=("Segoe UI", 10, "bold")
                ).pack(side="right", padx=(8, 0))
        distribution = self.card(lower, 18)
        distribution.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(
            distribution, text="Score Distribution",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")
        tk.Label(
            distribution,
            text="Attempts grouped by score range",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 8))
        if not results:
            tk.Label(
                distribution,
                text="Your chart will appear after your first quiz.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 10),
                wraplength=320, justify="left"
            ).pack(anchor="w", pady=20)
        else:
            ranges = [
                ("0-49%", 0, 50),
                ("50-69%", 50, 70),
                ("70-89%", 70, 90),
                ("90-100%", 90, 101),
            ]
            counts = [
                sum(1 for result in results if low <= result[4] < high)
                for _, low, high in ranges
            ]
            figure = Figure(figsize=(4.4, 2.0), dpi=100, facecolor=PANEL)
            axis = figure.add_subplot(111)
            axis.set_facecolor(PANEL)
            bar_colors = ["#fb7185", "#fbbf24", "#38bdf8", "#34d399"]
            bars = axis.bar(
                [item[0] for item in ranges],
                counts, color=bar_colors, width=0.58
            )
            max_count = max(counts, default=0)
            axis.set_ylim(0, max_count + max(1, max_count * 0.3))
            axis.tick_params(
                axis="x", colors=MUTED, labelsize=8, length=0, pad=6
            )
            axis.tick_params(axis="y", colors=MUTED, labelsize=8, length=0)
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)
            axis.spines["left"].set_color(BORDER)
            axis.spines["bottom"].set_color(BORDER)
            axis.grid(axis="y", color=BORDER, linewidth=0.7, alpha=0.65)
            axis.set_axisbelow(True)
            axis.set_ylabel("Attempts", color=MUTED, fontsize=8)
            axis.set_yticks(range(0, max_count + 1))
            for bar, count in zip(bars, counts):
                axis.annotate(
                    str(count),
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", color=WHITE, fontsize=8
                )
            figure.tight_layout(pad=1.0)
            canvas = FigureCanvasTkAgg(figure, master=distribution)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, pady=(4, 0))
            self.score_distribution_figure = figure
            self.score_distribution_canvas = canvas
        tk.Label(
            self.content,
            text=f"{len(questions)} questions available  |  Your results are saved to your account",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(10, 0))

    def stat_card(self, parent, title, value, accent):
        frame = tk.Frame(
            parent, bg=PANEL, padx=17, pady=17,
            highlightbackground=BORDER, highlightthickness=1
        )
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Frame(frame, bg=accent, height=4).pack(fill="x", pady=(0, 13))
        tk.Label(
            frame, text=title, bg=PANEL, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        tk.Label(
            frame, text=value, bg=PANEL, fg=WHITE,
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w", pady=(5, 0))
    def start_quiz_prompt(self):
        if self.quiz_active:
            messagebox.showinfo("Quiz in progress", "Finish the current quiz first.")
            return
        self.clear_content()
        self.set_page("Choose Your Quiz", "Take a Quiz")
        tk.Label(
            self.content, text="Choose Your Quiz Experience", bg=NAVY,
            fg=WHITE, font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            self.content,
            text="Choose a category and quiz mode, then press Start. Your name will be requested next.",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 10), wraplength=850, justify="left"
        ).pack(anchor="w", pady=(3, 15))

        modes = [
            ("MCQ Quiz", "Choose one correct answer from four options.", "Standard"),
            ("True / False", "Judge a statement based on each question's options.", "Quick"),
            ("Programming Quiz", "Focus on programming-related questions.", "Tech"),
            ("Timed Challenge", "Race the clock with a 60-second challenge.", "60 sec"),
            ("Practice Mode", "Learn at your own pace without a countdown timer.", "Relaxed"),
            ("Hard Mode", "Focus on questions with the highest mark values.", "Advanced"),
        ]
        selected_mode = tk.StringVar(value=getattr(self, "quiz_mode", "MCQ Quiz"))
        grid = tk.Frame(self.content, bg=NAVY)
        grid.pack(fill="x", pady=(0, 14))
        for i, (mode, description, tag) in enumerate(modes):
            r, c = divmod(i, 2)
            tile = tk.Frame(grid, bg=PANEL, padx=14, pady=12,
                            highlightbackground=BORDER, highlightthickness=1)
            tile.grid(row=r, column=c, sticky="nsew",
                      padx=(0, 8) if c == 0 else (8, 0), pady=6)
            tk.Radiobutton(
                tile, text=mode, variable=selected_mode, value=mode,
                bg=PANEL, fg=WHITE, selectcolor=PANEL_LIGHT,
                activebackground=PANEL, activeforeground=CYAN,
                font=("Segoe UI", 12, "bold"), cursor="hand2"
            ).pack(anchor="w")
            tk.Label(tile, text=description, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 9), wraplength=330, justify="left").pack(anchor="w", pady=(5, 7))
            tk.Label(tile, text=tag.upper(), bg=PANEL, fg=CYAN,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        form = self.card(self.content, 16)
        form.pack(fill="x", pady=(0, 8))
        tk.Label(form, text="Quiz category", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        category_options = ["All Categories", *database.CATEGORIES]
        selected_category = tk.StringVar(value=getattr(self, "quiz_category", "All Categories"))
        category_box = ttk.Combobox(
            form, textvariable=selected_category, values=category_options,
            state="readonly", font=("Segoe UI", 11),
            style="QuizCategory.TCombobox"
        )
        category_box.pack(fill="x", pady=(6, 12), ipady=4)

        def begin():
            chosen_mode = selected_mode.get()
            chosen_category = selected_category.get()
            name = self.student_name.strip()
            if not name:
                messagebox.showwarning(
                    "Login required", "Please log in before starting a quiz."
                )
                self.show_student_auth()
                return
            self.quiz_mode = chosen_mode
            self.quiz_category = chosen_category
            self.begin_quiz(name, chosen_mode, chosen_category)

        self.button(form, "Start Selected Quiz  ->", begin, True).pack(anchor="e")

    @staticmethod
    def category_for_question(question):
        text = str(question).casefold()
        if any(word in text for word in ("sqlite", "database", "sql", "query", "table", "key-value")):
            return "Database"
        if any(word in text for word in ("html", "css", "javascript", "web page", "website")):
            return "Web Development"
        if any(word in text for word in ("python", "def ", "list", "tuple", "dictionary", "exception", "loop", "comment", "function", "print()", "bool", "**")):
            return "Python"
        if any(word in text for word in ("program", "algorithm", "compiler", "code", "java", " c language", "variable")):
            return "Programming"
        return "General Knowledge"

    def _is_correct_answer(self, row, answer):
        if self.quiz_mode == "True / False":
            return answer == ("True" if self.tf_claims.get(row[0], {}).get("is_true") else "False")
        return answer == row[6]

    def begin_quiz(self, name, quiz_mode=None, quiz_category=None):
        questions = list(database.get_questions())
        if not questions:
            messagebox.showerror("No questions", "Ask the admin to add questions.")
            return
        if quiz_mode:
            self.quiz_mode = quiz_mode
        if quiz_category:
            self.quiz_category = quiz_category
        if self.quiz_category != "All Categories":
            filtered_by_category = [
                row for row in questions
                if database.get_question_category(row[0]) == self.quiz_category
            ]
            if not filtered_by_category:
                messagebox.showwarning(
                    "No questions in category",
                    f"No questions were found for {self.quiz_category}. Choose All Categories or add matching questions."
                )
                return
            questions = filtered_by_category
        if self.quiz_mode == "Programming Quiz":
            keywords = ("python", "java", "javascript", "program", "code", "sql", "query", "compiler", "loop", "function", "class", "variable", "algorithm", "database", "html", "css", "c language")
            filtered = [row for row in questions if any(word in str(row[1]).lower() for word in keywords)]
            if filtered:
                questions = filtered
            else:
                messagebox.showinfo(
                    "Programming questions not tagged",
                    "No programming-specific questions were detected by their question text, so all available questions will be used. For best results, include programming keywords in programming questions."
                )
        elif self.quiz_mode == "Hard Mode":
            highest_marks = max(int(row[7]) for row in questions)
            hard_questions = [row for row in questions if int(row[7]) == highest_marks]
            questions = hard_questions if len(hard_questions) >= 2 else questions
        random.shuffle(questions)
        self.questions = questions
        self.student_name = name
        self.answers = {}
        self.current_index = 0
        self.tf_claims = {}
        self.remaining_seconds = 60 if self.quiz_mode == "Timed Challenge" else 120
        if self.quiz_mode == "True / False":
            for row in self.questions:
                options = {"A": row[2], "B": row[3], "C": row[4], "D": row[5]}
                correct_letter = row[6]
                is_true = random.choice([True, False])
                if is_true:
                    claim_letter = correct_letter
                else:
                    claim_letter = random.choice([letter for letter in "ABCD" if letter != correct_letter])
                self.tf_claims[row[0]] = {
                    "claim": options[claim_letter],
                    "is_true": claim_letter == correct_letter,
                }
        self.quiz_active = True
        self.show_question()
        if self.quiz_mode != "Practice Mode":
            self.update_timer()
    def show_question(self):
        self.clear_content()
        self.set_page("Quiz in Progress", "Take a Quiz")
        row = self.questions[self.current_index]
        question_id, question, a, b, c, d, correct, marks = row
        head = tk.Frame(self.content, bg=NAVY)
        head.pack(fill="x", pady=(0, 15))
        tk.Label(
            head, text=f"Hello, {self.student_name}  |  {self.quiz_mode}",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 14, "bold")
        ).pack(side="left")
        self.timer_label = tk.Label(
            head,
            text="NO TIMER" if self.quiz_mode == "Practice Mode" else f"{self.remaining_seconds // 60:02d}:{self.remaining_seconds % 60:02d}",
            bg=NAVY, fg=CYAN, font=("Segoe UI", 14, "bold")
        )
        self.timer_label.pack(side="right")
        progress_area = tk.Frame(self.content, bg=NAVY)
        progress_area.pack(fill="x", pady=(0, 20))
        tk.Label(
            progress_area,
            text=f"QUESTION {self.current_index + 1} OF {len(self.questions)}  |  {self.quiz_mode.upper()}",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 7))
        progress = ttk.Progressbar(
            progress_area, maximum=len(self.questions),
            value=self.current_index + 1, length=400
        )
        progress.pack(fill="x")
        card = self.card(self.content, 28)
        card.pack(fill="both", expand=True)
        tk.Label(
            card, text=f"Question {self.current_index + 1}",
            bg=PANEL, fg=CYAN, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 12))
        if self.quiz_mode == "True / False":
            claim = self.tf_claims[question_id]["claim"]
            shown_question = f"{question}\n\nStatement to evaluate: {claim}"
            option_pairs = [("True", "True"), ("False", "False")]
        else:
            shown_question = question
            option_pairs = [(letter, f"{letter}.   {option}") for letter, option in zip("ABCD", [a, b, c, d])]
        tk.Label(
            card, text=shown_question, bg=PANEL, fg=WHITE,
            font=("Segoe UI", 16, "bold"), wraplength=780,
            justify="left"
        ).pack(anchor="w", pady=(0, 22))
        self.answer_var = tk.StringVar(
            master=self.root,
            value=self.answers.get(question_id, "")
        )
        for value, option_label in option_pairs:
            rb = tk.Radiobutton(
                card, text=option_label, variable=self.answer_var,
                value=value, indicatoron=True, tristatevalue="__none__",
                bg=PANEL, fg=WHITE, selectcolor=PANEL,
                activebackground=PANEL, activeforeground=CYAN,
                disabledforeground=MUTED, font=("Segoe UI", 12),
                anchor="w", padx=12, pady=8, cursor="hand2"
            )
            rb.pack(fill="x", anchor="w", pady=3)
        if self.quiz_mode == "Practice Mode":
            tk.Label(card, text="Practice mode: no countdown timer. Review your answers after submitting.",
                     bg=PANEL, fg=CYAN, font=("Segoe UI", 10)).pack(anchor="w", pady=(14, 0))
        bottom = tk.Frame(self.content, bg=NAVY)
        bottom.pack(fill="x", pady=(16, 0))
        self.button(
                bottom, "<- Previous", self.previous_question,
        ).pack(side="left")
        if self.current_index < len(self.questions) - 1:
            self.button(
                bottom, "Next ->", self.next_question, True
            ).pack(side="right")
        else:
            self.button(
                bottom, "Submit Quiz", self.submit_quiz, True
            ).pack(side="right")
        tk.Label(
            bottom, text="Select one answer for each question",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 9)
        ).pack(side="left", padx=20)
    def remember_answer(self):
        row = self.questions[self.current_index]
        self.answers[row[0]] = self.answer_var.get()
    def next_question(self):
        self.remember_answer()
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.show_question()
    def previous_question(self):
        self.remember_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()
    def update_timer(self):
        if not self.quiz_active or self.quiz_mode == "Practice Mode":
            return
        mins, secs = divmod(self.remaining_seconds, 60)
        if hasattr(self, "timer_label") and self.timer_label.winfo_exists():
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        if self.remaining_seconds <= 0:
            self.timer_job = None
            messagebox.showinfo("Time is up", "Your quiz will be submitted now.")
            self.submit_quiz(confirm=False)
            return
        self.remaining_seconds -= 1
        self.timer_job = self.root.after(1000, self.update_timer)
    def submit_quiz(self, confirm=True):
        if not self.quiz_active:
            return
        self.remember_answer()
        if confirm and not messagebox.askyesno(
            "Submit Quiz", "Are you sure you want to submit your answers?"
        ):
            return
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None
        score = sum(
            row[7] for row in self.questions
            if self._is_correct_answer(row, self.answers.get(row[0], ""))
        )
        total = sum(row[7] for row in self.questions)
        percentage = score / total * 100 if total else 0
        if self.quiz_mode != "Practice Mode":
            database.save_result(
            self.student_name, score, total, percentage,
            self.quiz_category, self.quiz_mode,
            student_username=self.student_username
        )
        self.last_score = score
        self.last_total = total
        self.last_percentage = percentage
        self.quiz_active = False
        self.show_result()
    def show_result(self):
        self.clear_content()
        self.set_page("Quiz Result")
        tk.Label(
            self.content, text="QUIZ COMPLETED",
            bg=NAVY, fg=CYAN, font=("Segoe UI", 12, "bold")
        ).pack(pady=(18, 6))
        tk.Label(
            self.content, text=f"Well done, {self.student_name}!",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 25, "bold")
        ).pack(pady=(0, 20))
        result_card = self.card(self.content, 30)
        result_card.pack(fill="x", padx=45, pady=5)
        tk.Label(
            result_card, text=f"{self.last_percentage:.1f}%",
            bg=PANEL, fg=GREEN if self.last_percentage >= 50 else RED,
            font=("Segoe UI", 38, "bold")
        ).pack(pady=(0, 5))
        tk.Label(
            result_card, text=f"Score: {self.last_score} / {self.last_total}",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 15, "bold")
        ).pack(pady=5)
        tk.Label(
            result_card,
            text="Excellent work!" if self.last_percentage >= 80
            else "Good effort!" if self.last_percentage >= 50
            else "Keep practising. You can improve!",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 11)
        ).pack(pady=5)
        actions = tk.Frame(self.content, bg=NAVY)
        actions.pack(pady=18)
        self.button(
            actions, "Review Answers", self.review_answers
        ).pack(side="left", padx=5)
        self.button(
            actions, "Back to Dashboard", self.show_dashboard, True
        ).pack(side="left", padx=5)
        self.button(
            actions, "Try Again", self.start_quiz_prompt
        ).pack(side="left", padx=5)
    def review_answers(self):
        window = tk.Toplevel(self.root)
        window.title("Answer Review")
        window.geometry("800x600")
        window.configure(bg=NAVY)
        tk.Label(
            window, text="Answer Review", bg=NAVY, fg=WHITE,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=20, pady=18)
        text = tk.Text(
            window, bg=PANEL, fg=WHITE, insertbackground=WHITE,
            font=("Segoe UI", 11), wrap="word", padx=15, pady=12,
            relief="flat"
        )
        text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for number, row in enumerate(self.questions, 1):
            qid, question, a, b, c, d, correct, marks = row
            options = {"A": a, "B": b, "C": c, "D": d}
            selected = self.answers.get(qid, "")
            text.insert("end", f"{number}. {question}\n")
            if self.quiz_mode == "True / False":
                claim = self.tf_claims.get(qid, {})
                text.insert("end", f"Statement: {claim.get('claim', '')}\n")
                text.insert("end", f"Your answer: {selected or 'Not answered'}\n")
                text.insert("end", f"Correct answer: {'True' if claim.get('is_true') else 'False'}\n\n")
            else:
                text.insert(
                    "end",
                    f"Your answer: {selected + '. ' + options[selected] if selected in options else 'Not answered'}\n"
                )
                text.insert("end", f"Correct answer: {correct}. {options[correct]}\n\n")
        text.config(state="disabled")
    def admin_login(self):
        if self.quiz_active:
            messagebox.showinfo("Quiz in progress", "Finish the current quiz first.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Admin Login")
        dialog.geometry("390x340")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(
            dialog, text="ADMIN ACCESS", bg=PANEL, fg=CYAN,
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(25, 5))
        tk.Label(
            dialog, text="Sign in to manage QuizFlow",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 17, "bold")
        ).pack(pady=(0, 18))
        tk.Label(
            dialog, text="Username", bg=PANEL, fg=MUTED
        ).pack(anchor="w", padx=35)
        username = tk.Entry(
            dialog, bg=PANEL_LIGHT, fg=WHITE, insertbackground=WHITE,
            relief="flat", font=("Segoe UI", 11)
        )
        username.pack(fill="x", padx=35, pady=(5, 12), ipady=7)
        tk.Label(
            dialog, text="Password", bg=PANEL, fg=MUTED
        ).pack(anchor="w", padx=35)
        password = tk.Entry(
            dialog, show="*", bg=PANEL_LIGHT, fg=WHITE,
            insertbackground=WHITE, relief="flat", font=("Segoe UI", 11)
        )
        password.pack(fill="x", padx=35, pady=(5, 18), ipady=7)
        def verify():
            if username.get().strip() == "admin" and password.get() == "admin123":
                dialog.destroy()
                self.show_admin()
            else:
                messagebox.showerror(
                    "Login failed", "Incorrect username or password.",
                    parent=dialog
                )
        self.button(dialog, "Sign In", verify, True).pack(fill="x", padx=35)
        password.bind("<Return>", lambda event: verify())
        username.focus_set()
    def show_admin(self):
        self.clear_content()
        self.set_page("Admin Panel", "Admin Panel")
        notebook = ttk.Notebook(self.content)
        notebook.pack(fill="both", expand=True)
        questions_tab = tk.Frame(notebook, bg=NAVY)
        results_tab = tk.Frame(notebook, bg=NAVY)
        notebook.add(questions_tab, text="  Question Management  ")
        notebook.add(results_tab, text="  Student Results  ")
        self.build_questions_tab(questions_tab)
        self.build_results_tab(results_tab)
    def build_questions_tab(self, parent):
        header = tk.Frame(parent, bg=NAVY)
        header.pack(fill="x", padx=14, pady=14)
        tk.Label(
            header, text="Manage Questions",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 17, "bold")
        ).pack(side="left")
        self.question_search = tk.StringVar()
        search = tk.Entry(
            header, textvariable=self.question_search,
            bg=PANEL, fg=WHITE, insertbackground=WHITE,
            relief="flat", width=28, font=("Segoe UI", 10)
        )
        search.pack(side="right", ipady=7)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda event: self.refresh_questions())
        tk.Label(
            parent, text="Search questions by text or ID",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="e", padx=20, pady=(0, 5))
        columns = ("id", "question", "category", "correct", "marks")
        self.question_tree = ttk.Treeview(
            parent, columns=columns, show="headings"
        )
        for col, title, width in [
            ("id", "ID", 55),
            ("question", "Question", 430),
            ("category", "Category", 150),
            ("correct", "Answer", 90),
            ("marks", "Marks", 80)
        ]:
            self.question_tree.heading(col, text=title)
            self.question_tree.column(col, width=width, anchor="w")
        self.question_tree.pack(
            fill="both", expand=True, padx=14, pady=(0, 12)
        )
        actions = tk.Frame(parent, bg=NAVY)
        actions.pack(fill="x", padx=14, pady=(0, 14))
        self.button(
            actions, "+ Add Question", self.add_question_dialog, True
        ).pack(side="left", padx=(0, 8))
        self.button(
            actions, "Delete Selected", self.remove_question
        ).pack(side="left")
        self.refresh_questions()
    def refresh_questions(self):
        if not hasattr(self, "question_tree"):
            return
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        search = self.question_search.get().strip().lower()
        for row in database.get_questions():
            if search and search not in str(row[0]).lower() and search not in row[1].lower():
                continue
            self.question_tree.insert(
                "", "end", values=(row[0], row[1], database.get_question_category(row[0]), row[6], row[7])
            )
    def add_question_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Question")
        dialog.geometry("500x590")
        dialog.configure(bg=PANEL)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(
            dialog, text="Create a Question", bg=PANEL, fg=WHITE,
            font=("Segoe UI", 19, "bold")
        ).pack(pady=(18, 12))
        form = tk.Frame(dialog, bg=PANEL)
        form.pack(fill="both", expand=True, padx=25)
        def add_field(title):
            tk.Label(
                form, text=title, bg=PANEL, fg=MUTED,
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(6, 3))
            entry = tk.Entry(
                form, bg=PANEL_LIGHT, fg=WHITE,
                insertbackground=WHITE, relief="flat",
                font=("Segoe UI", 11)
            )
            entry.pack(fill="x", ipady=6)
            return entry
        q = add_field("Question")
        tk.Label(form, text="Category", bg=PANEL, fg=MUTED).pack(anchor="w", pady=(6, 3))
        category = ttk.Combobox(form, values=database.CATEGORIES, state="readonly")
        category.set("Python")
        category.pack(fill="x")
        a = add_field("Option A")
        b = add_field("Option B")
        c = add_field("Option C")
        d = add_field("Option D")
        tk.Label(
            form, text="Correct option", bg=PANEL, fg=MUTED
        ).pack(anchor="w", pady=(8, 3))
        correct = ttk.Combobox(
            form, values=["A", "B", "C", "D"], state="readonly"
        )
        correct.set("A")
        correct.pack(fill="x")
        tk.Label(
            form, text="Marks", bg=PANEL, fg=MUTED
        ).pack(anchor="w", pady=(8, 3))
        marks = tk.Entry(
            form, bg=PANEL_LIGHT, fg=WHITE,
            insertbackground=WHITE, relief="flat"
        )
        marks.insert(0, "1")
        marks.pack(fill="x", ipady=5)
        def save():
            values = [e.get().strip() for e in (q, a, b, c, d)]
            if not all(values):
                messagebox.showwarning(
                    "Missing fields", "Fill in the question and all options.",
                    parent=dialog
                )
                return
            try:
                points = int(marks.get())
                if points <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Invalid marks", "Enter a positive whole number.",
                    parent=dialog
                )
                return
            try:
                database.add_question(
                    values[0], values[1], values[2], values[3], values[4],
                    correct.get(), points, category.get()
                )
            except Exception as error:
                messagebox.showerror(
                    "Database error", str(error), parent=dialog
                )
                return
            dialog.destroy()
            self.refresh_questions()
            messagebox.showinfo("Saved", "Question added successfully.")
        self.button(
            dialog, "Save Question", save, True
        ).pack(fill="x", padx=25, pady=15)
    def remove_question(self):
        selected = self.question_tree.selection()
        if not selected:
            messagebox.showwarning(
                "Select a question", "Select a question to delete."
            )
            return
        values = self.question_tree.item(selected[0], "values")
        question_id = int(values[0])
        if messagebox.askyesno(
            "Delete question",
            f"Delete question #{question_id}? This cannot be undone."
        ):
            database.delete_question(question_id)
            self.refresh_questions()
    def build_results_tab(self, parent):
        top = tk.Frame(parent, bg=NAVY)
        top.pack(fill="x", padx=14, pady=12)
        tk.Label(top, text="Student Performance", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        self.button(top, "Export Filtered CSV", self.export_results, True).pack(side="right")
        filters = tk.Frame(parent, bg=NAVY)
        filters.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(filters, text="Category", bg=NAVY, fg=MUTED).pack(side="left", padx=(0, 5))
        self.admin_category_filter = tk.StringVar(value="All Categories")
        ttk.Combobox(filters, textvariable=self.admin_category_filter,
                     values=["All Categories", *database.CATEGORIES, "Uncategorized"],
                     state="readonly", width=20).pack(side="left", padx=(0, 14))
        tk.Label(filters, text="Quiz type", bg=NAVY, fg=MUTED).pack(side="left", padx=(0, 5))
        self.admin_mode_filter = tk.StringVar(value="All Quiz Types")
        ttk.Combobox(filters, textvariable=self.admin_mode_filter,
                     values=["All Quiz Types", "MCQ Quiz", "True / False", "Programming Quiz", "Timed Challenge", "Practice Mode", "Hard Mode", "Legacy"],
                     state="readonly", width=20).pack(side="left", padx=(0, 10))
        self.button(filters, "Apply Filters", self.refresh_results, True).pack(side="left")
        columns = ("id", "name", "category", "mode", "score", "total", "percentage", "date")
        self.results_tree = ttk.Treeview(parent, columns=columns, show="headings")
        headings = {"id": ("ID", 45), "name": ("Student", 145), "category": ("Category", 130),
                    "mode": ("Quiz Type", 130), "score": ("Score", 70), "total": ("Total", 70),
                    "percentage": ("Percentage", 95), "date": ("Date and Time", 155)}
        for col, (title, width) in headings.items():
            self.results_tree.heading(col, text=title)
            self.results_tree.column(col, width=width, anchor="center")
        self.results_tree.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        self.refresh_results()

    def filtered_admin_results(self):
        rows = database.get_results()
        cat = getattr(self, "admin_category_filter", tk.StringVar(value="All Categories")).get()
        mode = getattr(self, "admin_mode_filter", tk.StringVar(value="All Quiz Types")).get()
        return [r for r in rows if (cat == "All Categories" or (r[6] or "Uncategorized") == cat)
                and (mode == "All Quiz Types" or (r[7] or "Legacy") == mode)]

    def refresh_results(self):
        if not hasattr(self, "results_tree"):
            return
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for row in self.filtered_admin_results():
            self.results_tree.insert("", "end", values=(row[0], row[1], row[6] or "Uncategorized",
                row[7] or "Legacy", row[2], row[3], f"{row[4]:.2f}%", row[5]))

    def export_results(self):
        results = self.filtered_admin_results()
        if not results:
            messagebox.showinfo("No results", "There are no results matching these filters.")
            return
        path = filedialog.asksaveasfilename(title="Export student results", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], initialfile="quiz_results.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Student Name", "Quiz Category", "Quiz Type", "Score", "Total Marks", "Percentage", "Date and Time"])
                for row in results:
                    writer.writerow([row[0], row[1], row[6] or "Uncategorized", row[7] or "Legacy", row[2], row[3], f"{row[4]:.2f}%", row[5]])
            messagebox.showinfo("Export complete", f"Results exported successfully:\n{path}")
        except OSError as error:
            messagebox.showerror("Export failed", str(error))

    def show_leaderboard(self, category_filter=None, mode_filter=None):
        if self.quiz_active:
            messagebox.showinfo("Quiz in progress", "Finish the current quiz first.")
            return

        if category_filter is None:
            category_filter = getattr(self, "leaderboard_category_filter", "All Categories")
        if mode_filter is None:
            mode_filter = getattr(self, "leaderboard_mode_filter", "All Quiz Types")
        self.leaderboard_category_filter = category_filter
        self.leaderboard_mode_filter = mode_filter

        self.clear_content()
        self.set_page("Leaderboard", "Leaderboard")
        all_results = database.get_results()
        results = [
            row for row in all_results
            if (category_filter == "All Categories" or row[6] == category_filter)
            and (mode_filter == "All Quiz Types" or row[7] == mode_filter)
        ]

        tk.Label(
            self.content, text="QuizFlow Leaderboard",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")
        tk.Label(
            self.content,
            text="Rankings show each student's best result within the selected category and quiz type.",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 10), wraplength=850, justify="left"
        ).pack(anchor="w", pady=(5, 12))

        filters = self.card(self.content, 12)
        filters.pack(fill="x", pady=(0, 12))
        tk.Label(filters, text="Category", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        category_var = tk.StringVar(value=category_filter)
        category_box = ttk.Combobox(
            filters, textvariable=category_var,
            values=["All Categories", "Python", "Programming", "Database", "Web Development", "General Knowledge", "Uncategorized"],
            state="readonly", width=22
        )
        category_box.pack(side="left", padx=(0, 18))
        tk.Label(filters, text="Quiz type", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        mode_var = tk.StringVar(value=mode_filter)
        mode_box = ttk.Combobox(
            filters, textvariable=mode_var,
            values=["All Quiz Types", "MCQ Quiz", "True / False", "Programming Quiz",
                    "Timed Challenge", "Practice Mode", "Hard Mode", "Legacy"],
            state="readonly", width=20
        )
        mode_box.pack(side="left", padx=(0, 12))
        self.button(
            filters, "Apply Filters",
            lambda: self.show_leaderboard(category_var.get(), mode_var.get()), True
        ).pack(side="left")

        if not results:
            empty = self.card(self.content, 28)
            empty.pack(fill="both", expand=True)
            tk.Label(empty, text="No results", bg=PANEL, fg="#fbbf24",
                     font=("Segoe UI", 34)).pack(pady=(28, 10))
            tk.Label(empty, text="No rankings for these filters yet",
                     bg=PANEL, fg=WHITE, font=("Segoe UI", 17, "bold")).pack()
            tk.Label(
                empty,
                text="Complete a saved quiz in this category and quiz type to appear here. Old results are kept under Uncategorized / Legacy.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 10), wraplength=700,
                justify="center"
            ).pack(pady=(8, 28))
            return

        best_by_student = {}
        for row in results:
            student_name = str(row[1]).strip()
            key = student_name.casefold()
            candidate = {
                "name": student_name, "score": row[2], "total": row[3],
                "percentage": float(row[4]), "taken_at": row[5], "id": row[0],
                "category": row[6], "mode": row[7]
            }
            current = best_by_student.get(key)
            if current is None or (
                candidate["percentage"], candidate["score"], -candidate["id"]
            ) > (
                current["percentage"], current["score"], -current["id"]
            ):
                best_by_student[key] = candidate

        rankings = sorted(
            best_by_student.values(),
            key=lambda item: (-item["percentage"], -item["score"],
                              item["taken_at"], item["name"].casefold())
        )

        podium = tk.Frame(self.content, bg=NAVY)
        podium.pack(fill="x", pady=(0, 14))
        medals = [
            ("1ST PLACE", "#fbbf24"),
            ("2ND PLACE", "#cbd5e1"),
            ("3RD PLACE", "#d97745"),
        ]
        for index in range(min(3, len(rankings))):
            item = rankings[index]
            card = self.card(podium, 14)
            card.pack(side="left", fill="both", expand=True,
                      padx=(0 if index == 0 else 8, 8 if index < 2 else 0))
            tk.Label(card, text=medals[index][0], bg=PANEL, fg=medals[index][1],
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(card, text=item["name"], bg=PANEL, fg=WHITE,
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(8, 3))
            tk.Label(card, text=f'{item["percentage"]:.1f}%',
                     bg=PANEL, fg=medals[index][1],
                     font=("Segoe UI", 22, "bold")).pack(anchor="w")
            tk.Label(card, text=f'Score: {item["score"]} / {item["total"]}',
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        table_card = self.card(self.content, 14)
        table_card.pack(fill="both", expand=True)
        tk.Label(table_card, text="Rankings", bg=PANEL, fg=WHITE,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))
        columns = ("rank", "student", "category", "mode", "score", "percentage", "date")
        tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)
        for col, title, width in [
            ("rank", "Rank", 55), ("student", "Student", 145),
            ("category", "Category", 125), ("mode", "Quiz Type", 135),
            ("score", "Best Score", 100), ("percentage", "Percentage", 100),
            ("date", "Best Attempt Date", 160),
        ]:
            tree.heading(col, text=title)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True)
        tree.tag_configure("first", foreground="#fbbf24")
        tree.tag_configure("second", foreground="#cbd5e1")
        tree.tag_configure("third", foreground="#d97745")
        for rank, item in enumerate(rankings, 1):
            tag = "first" if rank == 1 else "second" if rank == 2 else "third" if rank == 3 else ""
            tree.insert(
                "", "end", tags=(tag,) if tag else (),
                values=(rank, item["name"], item["category"], item["mode"],
                        f'{item["score"]} / {item["total"]}',
                        f'{item["percentage"]:.1f}%', item["taken_at"])
            )

        actions = tk.Frame(self.content, bg=NAVY)
        actions.pack(fill="x", pady=(10, 0))
        self.button(actions, "Refresh Leaderboard",
                    lambda: self.show_leaderboard(category_var.get(), mode_var.get()), True).pack(side="left")
        self.button(actions, "Back to Dashboard", self.show_dashboard).pack(side="left", padx=10)

    def show_analytics(self):
        if self.quiz_active:
            messagebox.showinfo("Quiz in progress", "Finish the current quiz first.")
            return
        self.clear_content()
        self.set_page("Performance Analytics", "Performance")
        results = database.get_results_for_student(
            self.student_username, self.student_name
        )
        attempts = len(results)
        average = sum(r[4] for r in results) / attempts if attempts else 0
        best = max((r[4] for r in results), default=0)
        passed = sum(1 for r in results if r[4] >= 50)
        tk.Label(
            self.content, text="Performance Overview",
            bg=NAVY, fg=WHITE, font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")
        tk.Label(
            self.content,
            text="Review your saved quiz attempts and personal score history.",
            bg=NAVY, fg=MUTED, font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(5, 20))
        stats = tk.Frame(self.content, bg=NAVY)
        stats.pack(fill="x", pady=(0, 20))
        self.stat_card(stats, "TOTAL ATTEMPTS", str(attempts), CYAN)
        self.stat_card(stats, "AVERAGE SCORE", f"{average:.1f}%", BLUE)
        self.stat_card(stats, "BEST SCORE", f"{best:.1f}%", GREEN)
        self.stat_card(stats, "SCORES >= 50%", str(passed), "#c084fc")
        history = self.card(self.content, 18)
        history.pack(fill="both", expand=True)
        tk.Label(
            history, text="Your Quiz History",
            bg=PANEL, fg=WHITE, font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", pady=(0, 12))
        if not results:
            tk.Label(
                history, text="No results recorded yet. Take a quiz to begin.",
                bg=PANEL, fg=MUTED, font=("Segoe UI", 11)
            ).pack(anchor="w", pady=12)
        else:
            columns = ("name", "score", "total", "percentage", "date")
            tree = ttk.Treeview(
                history, columns=columns, show="headings", height=9
            )
            headings = [
                ("name", "Student", 180),
                ("score", "Score", 90),
                ("total", "Total", 90),
                ("percentage", "Percentage", 120),
                ("date", "Date and Time", 200)
            ]
            for col, title, width in headings:
                tree.heading(col, text=title)
                tree.column(col, width=width, anchor="center")
            tree.pack(fill="both", expand=True)
            for row in results:
                tree.insert(
                    "", "end",
                    values=(
                        row[1], row[2], row[3],
                        f"{row[4]:.2f}%", row[5]
                    )
                )
        actions = tk.Frame(self.content, bg=NAVY)
        actions.pack(fill="x", pady=(15, 0))
        self.button(
            actions, "Refresh Analytics", self.show_analytics, True
        ).pack(side="left")
        self.button(
            actions, "Export Results to CSV", self.export_results
        ).pack(side="left", padx=10)
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizManagementSystem(root)
    root.mainloop()


