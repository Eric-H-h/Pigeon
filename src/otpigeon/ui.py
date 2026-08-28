from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from .clipboard import ClipboardError


class OTPigeonWindow:
    def __init__(self, root: tk.Tk, controller: Any) -> None:
        self.root = root
        self.controller = controller
        self._token_visible = False

        root.title("OTPigeon")
        root.geometry("680x470")
        root.minsize(620, 430)
        root.protocol("WM_DELETE_WINDOW", self._close)

        frame = ttk.Frame(root, padding=18)
        frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="OTPigeon", font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        ttk.Label(frame, text="Status").grid(row=1, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.status_var).grid(
            row=1, column=1, columnspan=2, sticky="w", pady=5
        )

        ttk.Label(frame, text="PC address (current IP)").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.address_var = tk.StringVar()
        address_entry = ttk.Entry(frame, textvariable=self.address_var, state="readonly")
        address_entry.grid(row=2, column=1, sticky="ew", padx=(10, 8), pady=5)
        ttk.Button(frame, text="Copy", command=self._copy_address).grid(
            row=2, column=2, sticky="e", pady=5
        )

        ttk.Label(frame, text="Pairing token").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(
            frame, textvariable=self.token_var, state="readonly", show="•"
        )
        self.token_entry.grid(row=3, column=1, sticky="ew", padx=(10, 8), pady=5)
        token_buttons = ttk.Frame(frame)
        token_buttons.grid(row=3, column=2, sticky="e", pady=5)
        self.show_button = ttk.Button(
            token_buttons, text="Show", width=7, command=self._toggle_token
        )
        self.show_button.pack(side="left", padx=(0, 4))
        ttk.Button(token_buttons, text="Copy", width=7, command=self._copy_token).pack(
            side="left"
        )

        ttk.Label(frame, text="Available links").grid(
            row=4, column=0, sticky="nw", pady=(10, 5)
        )
        self.addresses = tk.Text(frame, height=6, wrap="word", state="disabled")
        self.addresses.grid(
            row=4, column=1, columnspan=2, sticky="nsew", padx=(10, 0), pady=(10, 5)
        )

        ttk.Label(frame, text="Last event").grid(
            row=5, column=0, sticky="nw", pady=(10, 5)
        )
        self.event_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.event_var, wraplength=470).grid(
            row=5, column=1, columnspan=2, sticky="nw", padx=(10, 0), pady=(10, 5)
        )

        actions = ttk.Frame(frame)
        actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(18, 0))
        ttk.Button(actions, text="Setup help", command=self._show_setup_help).pack(
            side="left"
        )
        ttk.Button(
            actions, text="Regenerate token", command=self._regenerate_token
        ).pack(side="left", padx=8)
        ttk.Button(actions, text="Exit", command=self._close).pack(side="right")

        self._refresh()

    def _refresh(self) -> None:
        snapshot = self.controller.snapshot()
        self.status_var.set(snapshot.status)
        self.address_var.set(snapshot.address)
        self.token_var.set(snapshot.token)
        self.event_var.set(snapshot.last_event)

        lines = snapshot.numeric_addresses or (
            "No private IPv4 address detected. Enable Windows Mobile Hotspot.",
        )
        if snapshot.network_error:
            lines = lines + (f"Network: {snapshot.network_error}",)
        self.addresses.configure(state="normal")
        self.addresses.delete("1.0", "end")
        self.addresses.insert("1.0", "\n".join(lines))
        self.addresses.configure(state="disabled")

        self.root.after(500, self._refresh)

    def _copy_address(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.address_var.get())
        self.root.update()

    def _copy_token(self) -> None:
        try:
            self.controller.copy_token()
        except ClipboardError as exc:
            messagebox.showerror("Clipboard error", str(exc), parent=self.root)

    def _toggle_token(self) -> None:
        self._token_visible = not self._token_visible
        self.token_entry.configure(show="" if self._token_visible else "•")
        self.show_button.configure(text="Hide" if self._token_visible else "Show")

    def _regenerate_token(self) -> None:
        confirmed = messagebox.askyesno(
            "Regenerate pairing token?",
            "The existing iPhone Shortcut will stop working until you update its token.",
            parent=self.root,
        )
        if not confirmed:
            return
        try:
            self.controller.regenerate_token()
        except Exception as exc:
            messagebox.showerror(
                "Could not regenerate token", type(exc).__name__, parent=self.root
            )

    def _show_setup_help(self) -> None:
        messagebox.showinfo(
            "OTPigeon setup",
            "1. Set the Windows Wi-Fi network profile to Private.\n"
            "2. Allow OTPigeon through Windows Firewall on Private networks only.\n"
            "3. Connect the iPhone to the same trusted router or Windows hotspot.\n"
            "4. Enter the current PC address and pairing token in the Shortcut.\n"
            "5. Run the Shortcut once, then create a Message Personal Automation.",
            parent=self.root,
        )

    def _close(self) -> None:
        self.root.destroy()


def run_ui(controller: Any) -> None:
    root = tk.Tk()
    OTPigeonWindow(root, controller)
    root.mainloop()
