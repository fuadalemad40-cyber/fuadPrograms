import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Database file name
DB_FILE = "appointments.json"

class AppointmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة وحجز المواعيد الذكي")
        self.root.geometry("850x650")
        self.root.configure(bg="#f4f6f9")
        
        # Set Arabic font
        self.title_font = ("Segoe UI", 16, "bold")
        self.label_font = ("Segoe UI", 11)
        self.button_font = ("Segoe UI", 11, "bold")
        self.data_font = ("Segoe UI", 10)
        
        # Internal Data list
        self.appointments = []
        self.load_data()
        
        # Build UI Elements
        self.create_widgets()
        self.refresh_table()
        
        # Run periodic status check
        self.check_appointments_alerts()

    def load_data(self):
        """Load appointments from JSON file."""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    self.appointments = json.load(f)
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تحميل البيانات: {e}")
                self.appointments = []
        else:
            # Seed initial sample data for demonstration
            today_str = datetime.today().strftime("%Y-%m-%d")
            self.appointments = [
                {
                    "id": 1,
                    "name": "أحمد العتيبي",
                    "type": "single",
                    "start_date": today_str,
                    "end_date": "",
                    "notified_today": False
                },
                {
                    "id": 2,
                    "name": "سارة أحمد",
                    "type": "range",
                    "start_date": "2026-07-01",
                    "end_date": "2026-07-10",
                    "notified_today": False
                },
                {
                    "id": 3,
                    "name": "خالد الحربي",
                    "type": "single",
                    "start_date": "2026-12-25",
                    "end_date": "",
                    "notified_today": False
                }
            ]
            self.save_data()

    def save_data(self):
        """Save appointments to JSON file."""
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.appointments, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ البيانات: {e}")

    def create_widgets(self):
        # Header Banner
        header_frame = tk.Frame(self.root, bg="#1a365d", height=70)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame, 
            text="نظام إدارة وحجز المواعيد الذكي", 
            font=self.title_font, 
            fg="white", 
            bg="#1a365d"
        )
        header_label.pack(pady=15)

        # Main Layout (Right side for entry form, Left side for database list)
        main_frame = tk.Frame(self.root, bg="#f4f6f9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Form Frame (Right Column)
        form_frame = tk.LabelFrame(
            main_frame, 
            text=" إضافة حجز جديد ", 
            font=self.title_font, 
            bg="white", 
            fg="#1a365d", 
            padx=15, 
            pady=15,
            relief=tk.GROOVE
        )
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, width=320, padx=(10, 0))

        # Client Name Input
        tk.Label(form_frame, text="اسم العميل:", font=self.label_font, bg="white").pack(anchor="e", pady=(5, 2))
        self.name_entry = tk.Entry(form_frame, font=self.label_font, justify="right", bd=1, relief=tk.SOLID)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        # Booking Type Selector
        tk.Label(form_frame, text="نوع الحجز:", font=self.label_font, bg="white").pack(anchor="e", pady=(5, 2))
        self.type_var = tk.StringVar(value="single")
        
        radio_frame = tk.Frame(form_frame, bg="white")
        radio_frame.pack(fill=tk.X, pady=(0, 10))
        
        rb_single = tk.Radiobutton(
            radio_frame, 
            text="يوم محدد", 
            variable=self.type_var, 
            value="single", 
            command=self.toggle_date_fields, 
            bg="white", 
            font=self.label_font
        )
        rb_range = tk.Radiobutton(
            radio_frame, 
            text="فترة (من - إلى)", 
            variable=self.type_var, 
            value="range", 
            command=self.toggle_date_fields, 
            bg="white", 
            font=self.label_font
        )
        rb_single.pack(side=tk.RIGHT, padx=10)
        rb_range.pack(side=tk.RIGHT, padx=10)

        # Date Pickers/Entry fields (Y-M-D)
        self.date_single_frame = tk.Frame(form_frame, bg="white")
        self.date_single_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.date_single_frame, text="التاريخ (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
        self.date_single_entry = tk.Entry(self.date_single_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
        self.date_single_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_single_entry.pack(fill=tk.X, pady=(2, 10))

        # Date Range inputs (initially hidden or collapsed via grid/pack)
        self.date_range_frame = tk.Frame(form_frame, bg="white")
        
        tk.Label(self.date_range_frame, text="من تاريخ (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
        self.date_start_entry = tk.Entry(self.date_range_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
        self.date_start_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_start_entry.pack(fill=tk.X, pady=(2, 5))

        tk.Label(self.date_range_frame, text="إلى تاريخ (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
        self.date_end_entry = tk.Entry(self.date_range_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
        self.date_end_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.date_end_entry.pack(fill=tk.X, pady=(2, 10))

        # Submit Button
        btn_submit = tk.Button(
            form_frame, 
            text="إضافة الحجز وتفعيل التتبع", 
            command=self.add_appointment, 
            bg="#2b6cb0", 
            fg="white", 
            font=self.button_font,
            bd=0,
            cursor="hand2"
        )
        btn_submit.pack(fill=tk.X, pady=(15, 5))

        # List Frame (Left Column)
        list_frame = tk.LabelFrame(
            main_frame, 
            text=" المواعيد المحجوزة وتنبيهات الحالة ", 
            font=self.title_font, 
            bg="white", 
            fg="#1a365d", 
            padx=10, 
            pady=10,
            relief=tk.GROOVE
        )
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Top interactive bar in table frame
        actions_bar = tk.Frame(list_frame, bg="white")
        actions_bar.pack(fill=tk.X, pady=(0, 10))
        
        btn_delete = tk.Button(
            actions_bar, 
            text="حذف الموعد المحدد", 
            command=self.delete_appointment, 
            bg="#e53e3e", 
            fg="white", 
            font=self.data_font,
            bd=0,
            cursor="hand2"
        )
        btn_delete.pack(side=tk.RIGHT, padx=5)
        
        btn_reschedule = tk.Button(
            actions_bar, 
            text="إعادة حجز للموعد المنتهي", 
            command=self.reschedule_appointment, 
            bg="#319795", 
            fg="white", 
            font=self.data_font,
            bd=0,
            cursor="hand2"
        )
        btn_reschedule.pack(side=tk.RIGHT, padx=5)

        # Table (Treeview)
        columns = ("id", "name", "type", "dates", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Style treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=self.data_font, rowheight=30, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=self.label_font, background="#e2e8f0", foreground="#1a365d")
        
        self.tree.heading("id", text="الرقم")
        self.tree.heading("name", text="اسم الشخص")
        self.tree.heading("type", text="نوع الحجز")
        self.tree.heading("dates", text="الموعد / الفترة")
        self.tree.heading("status", text="الحالة الفورية")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=180, anchor="e")
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("dates", width=220, anchor="center")
        self.tree.column("status", width=130, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind row selection to update button availability if needed
        # and simple responsive behavior
        
    def toggle_date_fields(self):
        """Dynamically switches inputs depending on Booking Type selection."""
        if self.type_var.get() == "single":
            self.date_range_frame.pack_forget()
            self.date_single_frame.pack(fill=tk.X, pady=5)
        else:
            self.date_single_frame.pack_forget()
            self.date_range_frame.pack(fill=tk.X, pady=5)

    def parse_date(self, date_str):
        """Helper to parse standard date string format safely."""
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    def calculate_status(self, appt):
        """Helper to return (status_text, color) according to real-time calculation against Today."""
        today = datetime.today().date()
        
        if appt["type"] == "single":
            appt_date = self.parse_date(appt["start_date"])
            if not appt_date:
                return "خطأ في التاريخ", "#e53e3e"
            if today < appt_date:
                return "🟢 قادم", "#48bb78"
            elif today == appt_date:
                return "🟡 حان الآن", "#ecc94b"
            else:
                return "🔴 مضى (يتطلب إعادة جدولة)", "#f56565"
        else:
            start_date = self.parse_date(appt["start_date"])
            end_date = self.parse_date(appt["end_date"])
            if not start_date or not end_date:
                return "خطأ في التواريخ", "#e53e3e"
                
            if today < start_date:
                return "🟢 قادم", "#48bb78"
            elif start_date <= today <= end_date:
                return "🟡 حان الآن", "#ecc94b"
            else:
                return "🔴 مضى (يتطلب إعادة جدولة)", "#f56565"

    def refresh_table(self):
        """Clears table and populates it with recalculated dynamic statuses."""
        # Clear entries
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for appt in self.appointments:
            # Recalculate status dynamically
            status_text, color = self.calculate_status(appt)
            
            # Format display strings
            type_display = "يوم محدد" if appt["type"] == "single" else "خلال فترة"
            dates_display = appt["start_date"] if appt["type"] == "single" else f"من {appt['start_date']} إلى {appt['end_date']}"
            
            # Insert to UI table
            self.tree.insert(
                "", 
                tk.END, 
                values=(appt["id"], appt["name"], type_display, dates_display, status_text),
                tags=(status_text,)
            )

    def check_appointments_alerts(self):
        """Runs automatically to alert users via popups when an active/expired condition changes today."""
        today = datetime.today().date()
        modified = False
        
        for appt in self.appointments:
            status_text, _ = self.calculate_status(appt)
            
            # Check for Alert Triggers (Only notify once per session/day state to avoid annoying user repeatedly)
            if "حان الآن" in status_text and not appt.get("notified_today", False):
                messagebox.showinfo(
                    "تنبيه موعد نشط", 
                    f"العميل: {appt['name']}\nلديه موعد نشط اليوم {appt['start_date']}!"
                )
                appt["notified_today"] = True
                modified = True
            elif "مضى" in status_text and not appt.get("notified_today_expired", False):
                # Prompt automatically for rescheduling
                answer = messagebox.askyesno(
                    "موعد منتهي",
                    f"موعد العميل '{appt['name']}' قد انتهى ومضى.\nهل تود إعادة حجز موعد جديد له الآن؟"
                )
                appt["notified_today_expired"] = True
                modified = True
                if answer:
                    self.trigger_reschedule_dialog(appt)
                    break # Break to allow refresh and save

        if modified:
            self.save_data()
            self.refresh_table()
            
        # Run every 60 seconds (for background monitoring)
        self.root.after(60000, self.check_appointments_alerts)

    def add_appointment(self):
        """Extract fields, validate, save to database and refresh."""
        name = self.name_entry.get().strip()
        booking_type = self.type_var.get()
        
        if not name:
            messagebox.showwarning("تنبيه", "يرجى كتابة اسم الشخص أولاً!")
            return
            
        if booking_type == "single":
            start_date = self.date_single_entry.get().strip()
            end_date = ""
            if not self.parse_date(start_date):
                messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة، يرجى كتابتها بالشكل: YYYY-MM-DD")
                return
        else:
            start_date = self.date_start_entry.get().strip()
            end_date = self.date_end_entry.get().strip()
            
            s_dt = self.parse_date(start_date)
            e_dt = self.parse_date(end_date)
            
            if not s_dt or not e_dt:
                messagebox.showerror("خطأ", "يرجى التحقق من صياغة تاريخ البداية والنهاية (YYYY-MM-DD)")
                return
            if s_dt > e_dt:
                messagebox.showerror("خطأ", "تاريخ بداية الفترة لا يمكن أن يكون بعد تاريخ نهايتها!")
                return
                
        # Generate new unique ID
        new_id = max([a["id"] for a in self.appointments], default=0) + 1
        
        new_appt = {
            "id": new_id,
            "name": name,
            "type": booking_type,
            "start_date": start_date,
            "end_date": end_date,
            "notified_today": False
        }
        
        self.appointments.append(new_appt)
        self.save_data()
        self.refresh_table()
        
        # Reset form fields
        self.name_entry.delete(0, tk.END)
        messagebox.showinfo("نجاح", f"تم تسجيل حجز العميل '{name}' بنجاح وتفعيل التتبع!")
        self.check_appointments_alerts()

    def delete_appointment(self):
        """Deletes selected appointment from database."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار حجز من الجدول لحذفه.")
            return
            
        item_data = self.tree.item(selected[0])
        appt_id = item_data["values"][0]
        
        # Confirmation
        confirm = messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من رغبتك في حذف هذا الحجز نهائياً؟")
        if confirm:
            self.appointments = [a for a in self.appointments if a["id"] != appt_id]
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("تم الحذف", "تم حذف الحجز بنجاح.")

    def reschedule_appointment(self):
        """Trigger reschedule for selected row manually."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "الرجاء اختيار حجز منتهٍ من الجدول لإعادة جدولته.")
            return
            
        item_data = self.tree.item(selected[0])
        appt_id = item_data["values"][0]
        
        appt = next((a for a in self.appointments if a["id"] == appt_id), None)
        if appt:
            self.trigger_reschedule_dialog(appt)

    def trigger_reschedule_dialog(self, appt):
        """Opens a custom pop-up dialog window to request the new date(s) for rescheduling."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"إعادة حجز موعد جديد للعميل: {appt['name']}")
        dialog.geometry("400x320")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog, 
            text=f"تعديل موعد: {appt['name']}", 
            font=self.label_font, 
            bg="white", 
            fg="#1a365d"
        ).pack(pady=15)
        
        # New inputs frame
        inputs_frame = tk.Frame(dialog, bg="white")
        inputs_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Use simple date input
        if appt["type"] == "single":
            tk.Label(inputs_frame, text="التاريخ الجديد (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
            new_date_entry = tk.Entry(inputs_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
            new_date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
            new_date_entry.pack(fill=tk.X, pady=(5, 15))
            
            def save_new():
                nd = new_date_entry.get().strip()
                if not self.parse_date(nd):
                    messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة", parent=dialog)
                    return
                appt["start_date"] = nd
                appt["end_date"] = ""
                appt["notified_today"] = False # Reset alerts
                appt.pop("notified_today_expired", None)
                self.save_data()
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("تم التحديث", f"تمت إعادة جدولة الموعد بنجاح إلى تاريخ {nd}!")
                
        else:
            tk.Label(inputs_frame, text="تاريخ البداية الجديد (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
            new_start_entry = tk.Entry(inputs_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
            new_start_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
            new_start_entry.pack(fill=tk.X, pady=(5, 10))
            
            tk.Label(inputs_frame, text="تاريخ النهاية الجديد (YYYY-MM-DD):", font=self.label_font, bg="white").pack(anchor="e")
            new_end_entry = tk.Entry(inputs_frame, font=self.label_font, justify="center", bd=1, relief=tk.SOLID)
            new_end_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
            new_end_entry.pack(fill=tk.X, pady=(5, 15))
            
            def save_new():
                ns = new_start_entry.get().strip()
                ne = new_end_entry.get().strip()
                s_dt = self.parse_date(ns)
                e_dt = self.parse_date(ne)
                
                if not s_dt or not e_dt:
                    messagebox.showerror("خطأ", "صيغة التاريخ غير صحيحة", parent=dialog)
                    return
                if s_dt > e_dt:
                    messagebox.showerror("خطأ", "تاريخ البداية يجب أن يسبق النهاية", parent=dialog)
                    return
                    
                appt["start_date"] = ns
                appt["end_date"] = ne
                appt["notified_today"] = False # Reset alerts
                appt.pop("notified_today_expired", None)
                self.save_data()
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("تم التحديث", f"تمت إعادة جدولة الموعد بنجاح للفترة من {ns} إلى {ne}!")
                
        # Save button in dialog
        btn_save = tk.Button(
            dialog, 
            text="تحديث وحفظ الموعد", 
            command=save_new, 
            bg="#319795", 
            fg="white", 
            font=self.button_font,
            bd=0,
            cursor="hand2"
        )
        btn_save.pack(fill=tk.X, padx=20, pady=(0, 20))


if __name__ == "__main__":
    root = tk.Tk()
    app = AppointmentApp(root)
    root.mainloop()
