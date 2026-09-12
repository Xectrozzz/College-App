from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from backend.storage import attendance_key,cancellation_key,save_attendance,save_cancellations,load_cancellations
from backend.attendance_service import is_class_cancelled
from frontend.theme import *
from frontend.widgets.buttons import AppButton
class AttendancePopup(Popup):
    def __init__(self,subject,class_date,time,class_type="LECTURE",**kwargs):
        self.subject,self.class_date,self.time,self.class_type=subject,class_date,time,class_type or "LECTURE"
        box=BoxLayout(orientation="vertical",padding=ui(22),spacing=ui(12)); rounded_background(box,UI_SURFACE,22,UI_BORDER)
        for text,size,color,bold in [(subject,21,UI_TEXT,True),(f"{class_date}  •  {time}",13,UI_MUTED,False),(self.class_type,11,UI_ACCENT,True)]: box.add_widget(Label(text=text,font_size=fs(size),color=color,bold=bold,size_hint_y=None,height=ui(28)))
        p=AppButton(text="PRESENT",font_size=fs(14),background_color=UI_SUCCESS,size_hint_y=None,height=ui(48)); a=AppButton(text="ABSENT",font_size=fs(14),background_color=UI_DANGER,size_hint_y=None,height=ui(48)); p.bind(on_press=lambda x:self.mark("present")); a.bind(on_press=lambda x:self.mark("absent")); box.add_widget(p);box.add_widget(a)
        cancelled=is_class_cancelled(class_date,subject,time); p.disabled=a.disabled=cancelled
        c=AppButton(text="RESTORE CLASS" if cancelled else "CANCEL CLASS",font_size=fs(13),background_color=UI_WARNING,size_hint_y=None,height=ui(44));c.bind(on_press=lambda x:self.toggle_cancellation());box.add_widget(c)
        super().__init__(title="",content=box,size_hint=(.88,.56),separator_height=0,background="",**kwargs)
    def mark(self,status):
        app=App.get_running_app(); key=attendance_key(self.class_date,self.subject,self.time,self.class_type); app.attendance_data[key]={"subject":self.subject,"date":self.class_date,"time":self.time,"type":self.class_type,"status":status};save_attendance(app.attendance_data);self.dismiss();
        try: app.root.get_screen("timetable").refresh_grid();app.root.get_screen("home").update_dashboard()
        except Exception:pass
    def toggle_cancellation(self):
        app=App.get_running_app(); data=getattr(app,"cancellations_data",load_cancellations());key=cancellation_key(self.class_date,self.subject,self.time)
        if key in data:data.pop(key,None)
        else:
            data[key]={"subject":self.subject,"date":self.class_date,"time":self.time};app.attendance_data.pop(attendance_key(self.class_date,self.subject,self.time,self.class_type),None);app.attendance_data.pop(attendance_key(self.class_date,self.subject,self.time),None);save_attendance(app.attendance_data)
        save_cancellations(data);self.dismiss()
        try:app.root.get_screen("timetable").refresh_grid();app.root.get_screen("home").update_dashboard()
        except Exception:pass
