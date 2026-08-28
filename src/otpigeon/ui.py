from __future__ import annotations

import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import Any

from .clipboard import ClipboardError
from .i18n import LANGUAGE_NAMES, text, translate_event, translate_status


PROJECT_URL = "https://github.com/Eric-H-h/Pigeon"
PROJECT_URL_DISPLAY = "github.com/Eric-H-h/Pigeon"
AUTHOR_CREDIT = "@eric"


class PigeonWindow:
    def __init__(self, root: tk.Tk, controller: Any) -> None:
        self.root = root
        self.controller = controller
        self._token_visible = False
        self._language = controller.snapshot().language

        root.title(text(self._language, "app_name"))
        root.geometry("680x470")
        root.minsize(620, 430)
        root.protocol("WM_DELETE_WINDOW", self._close)

        frame = ttk.Frame(root, padding=18)
        frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

        self.app_name_label = ttk.Label(frame, font=("Segoe UI", 20, "bold"))
        self.app_name_label.grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        language_frame = ttk.Frame(frame)
        language_frame.grid(row=0, column=2, sticky="e", pady=(0, 12))
        ttk.Label(language_frame, text="Language").pack(side="left", padx=(0, 6))
        self.language_var = tk.StringVar(value=LANGUAGE_NAMES[self._language])
        self.language_box = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=tuple(LANGUAGE_NAMES.values()),
            state="readonly",
            width=8,
        )
        self.language_box.pack(side="left")
        self.language_box.bind("<<ComboboxSelected>>", self._change_language)

        self.status_label = ttk.Label(frame)
        self.status_label.grid(row=1, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=1, column=1, columnspan=2, sticky="w", pady=5
        )

        self.url_label = ttk.Label(frame)
        self.url_label.grid(row=2, column=0, sticky="w", pady=5)
        self.address_var = tk.StringVar()
        address_entry = ttk.Entry(frame, textvariable=self.address_var, state="readonly")
        address_entry.grid(row=2, column=1, sticky="ew", padx=(10, 8), pady=5)
        self.copy_url_button = ttk.Button(frame, command=self._copy_url)
        self.copy_url_button.grid(
            row=2, column=2, sticky="e", pady=5
        )

        self.token_label = ttk.Label(frame)
        self.token_label.grid(row=3, column=0, sticky="w", pady=5)
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(
            frame, textvariable=self.token_var, state="readonly", show="•"
        )
        self.token_entry.grid(row=3, column=1, sticky="ew", padx=(10, 8), pady=5)
        token_buttons = ttk.Frame(frame)
        token_buttons.grid(row=3, column=2, sticky="e", pady=5)
        self.show_button = ttk.Button(token_buttons, width=7, command=self._toggle_token)
        self.show_button.pack(side="left", padx=(0, 4))
        self.copy_token_button = ttk.Button(
            token_buttons, width=7, command=self._copy_token
        )
        self.copy_token_button.pack(side="left")

        self.addresses_label = ttk.Label(frame)
        self.addresses_label.grid(row=4, column=0, sticky="nw", pady=(10, 5))
        self.addresses = tk.Text(frame, height=6, wrap="word", state="disabled")
        self.addresses.grid(
            row=4, column=1, columnspan=2, sticky="nsew", padx=(10, 0), pady=(10, 5)
        )

        self.event_label = ttk.Label(frame)
        self.event_label.grid(row=5, column=0, sticky="nw", pady=(10, 5))
        self.event_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.event_var, wraplength=470).grid(
            row=5, column=1, columnspan=2, sticky="nw", padx=(10, 0), pady=(10, 5)
        )

        actions = ttk.Frame(frame)
        actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(18, 0))
        actions.columnconfigure(1, weight=1)

        left_actions = ttk.Frame(actions)
        left_actions.grid(row=0, column=0, sticky="w")
        self.help_button = ttk.Button(left_actions, command=self._show_setup_help)
        self.help_button.pack(side="left")
        self.regenerate_button = ttk.Button(
            left_actions, command=self._regenerate_token
        )
        self.regenerate_button.pack(side="left", padx=8)

        footer = ttk.Frame(actions)
        footer.grid(row=0, column=1)
        self.project_link = ttk.Label(
            footer,
            text=PROJECT_URL_DISPLAY,
            foreground="#0067c0",
            cursor="hand2",
        )
        self.project_link.pack(side="left")
        self.project_link.bind("<Button-1>", self._open_project_url)
        ttk.Label(footer, text=AUTHOR_CREDIT).pack(side="left", padx=(8, 0))

        self.exit_button = ttk.Button(actions, command=self._close)
        self.exit_button.grid(row=0, column=2, sticky="e")

        self._apply_language()
        self._refresh()

    def _refresh(self) -> None:
        snapshot = self.controller.snapshot()
        if snapshot.language != self._language:
            self._language = snapshot.language
            self.language_var.set(LANGUAGE_NAMES[self._language])
            self._apply_language()

        self.status_var.set(translate_status(self._language, snapshot.status))
        self.address_var.set(snapshot.shortcut_url)
        self.copy_url_button.configure(
            state="normal" if snapshot.shortcut_url else "disabled"
        )
        self.token_var.set(snapshot.token)
        self.event_var.set(translate_event(self._language, snapshot.last_event))

        lines = snapshot.numeric_addresses or (
            text(self._language, "no_private_ip"),
        )
        if snapshot.network_error:
            lines = lines + (
                text(self._language, "network_error", error=snapshot.network_error),
            )
        self.addresses.configure(state="normal")
        self.addresses.delete("1.0", "end")
        self.addresses.insert("1.0", "\n".join(lines))
        self.addresses.configure(state="disabled")

        self.root.after(500, self._refresh)

    def _copy_url(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.address_var.get())
        self.root.update()

    def _copy_token(self) -> None:
        try:
            self.controller.copy_token()
        except ClipboardError as exc:
            messagebox.showerror(
                text(self._language, "clipboard_error"), str(exc), parent=self.root
            )

    def _toggle_token(self) -> None:
        self._token_visible = not self._token_visible
        self.token_entry.configure(show="" if self._token_visible else "•")
        self.show_button.configure(
            text=text(self._language, "hide" if self._token_visible else "show")
        )

    def _regenerate_token(self) -> None:
        confirmed = messagebox.askyesno(
            text(self._language, "regenerate_title"),
            text(self._language, "regenerate_message"),
            parent=self.root,
        )
        if not confirmed:
            return
        try:
            self.controller.regenerate_token()
        except Exception as exc:
            messagebox.showerror(
                text(self._language, "regenerate_error"),
                type(exc).__name__,
                parent=self.root,
            )

    def _show_setup_help(self) -> None:
        messagebox.showinfo(
            text(self._language, "setup_title"),
            text(self._language, "setup_message"),
            parent=self.root,
        )

    def _open_project_url(self, _event: object) -> None:
        webbrowser.open(PROJECT_URL, new=2)

    def _change_language(self, _event: object) -> None:
        selected = self.language_var.get()
        language = next(
            code for code, display_name in LANGUAGE_NAMES.items()
            if display_name == selected
        )
        if language == self._language:
            return
        try:
            self.controller.set_language(language)
        except Exception as exc:
            self.language_var.set(LANGUAGE_NAMES[self._language])
            messagebox.showerror(
                text(self._language, "language_error"),
                type(exc).__name__,
                parent=self.root,
            )
            return
        self._language = language
        self._apply_language()

    def _apply_language(self) -> None:
        app_name = text(self._language, "app_name")
        self.root.title(app_name)
        self.app_name_label.configure(text=app_name)
        self.status_label.configure(text=text(self._language, "status"))
        self.url_label.configure(text=text(self._language, "shortcut_url"))
        self.token_label.configure(text=text(self._language, "pairing_token"))
        self.addresses_label.configure(text=text(self._language, "available_ips"))
        self.event_label.configure(text=text(self._language, "last_event"))
        self.copy_url_button.configure(text=text(self._language, "copy"))
        self.copy_token_button.configure(text=text(self._language, "copy"))
        self.show_button.configure(
            text=text(self._language, "hide" if self._token_visible else "show")
        )
        self.help_button.configure(text=text(self._language, "setup_help"))
        self.regenerate_button.configure(text=text(self._language, "regenerate_token"))
        self.exit_button.configure(text=text(self._language, "exit"))

    def _close(self) -> None:
        self.root.destroy()


def run_ui(controller: Any) -> None:
    root = tk.Tk()
    PigeonWindow(root, controller)
    root.mainloop()
