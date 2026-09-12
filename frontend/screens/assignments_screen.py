import json,os
from datetime import date
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from backend.constants import SUBJECTS
from frontend.theme import *
from frontend.widgets.buttons import AppButton
from frontend.widgets.navigation import BottomNav

class AssignmentsScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs);main=BoxLayout(orientation="vertical",padding=(ui(18),ui(12),ui(18),ui(8)),spacing=ui(10));rounded_background(main,UI_BG,0);scroll=ScrollView(bar_width=ui(4));self.box=BoxLayout(orientation="vertical",spacing=ui(16),size_hint_y=None,padding=(0,ui(4),0,ui(18)));self.box.bind(minimum_height=self.box.setter("height"));scroll.add_widget(self.box);main.add_widget(scroll);main.add_widget(BottomNav(current="assignments"));self.add_widget(main)
    def lab(self,t,size=14,color=UI_TEXT,bold=False,**kw):l=Label(text=t,font_size=fs(size),color=color,bold=bold,halign="left",valign="middle",**kw);l.bind(size=lambda i,v:setattr(i,"text_size",v));return l
    def card(self,h):c=BoxLayout(orientation="vertical",padding=(ui(20),ui(16)),spacing=ui(8),size_hint_y=None,height=ui(h));rounded_background(c,UI_SURFACE,22,UI_BORDER);return c
    def file(self):return os.path.join(App.get_running_app().user_data_dir,"assignments.json")
    def load(self):
        try:
            with open(self.file()) as h:return json.load(h)
        except Exception:return []
    def save(self,a):
        os.makedirs(os.path.dirname(self.file()),exist_ok=True)
        with open(self.file(),"w") as h:json.dump(a,h,indent=2)
    def refresh_assignments(self):
        self.box.clear_widgets();a=self.load();a.sort(key=lambda x:(x.get("completed",False),x.get("due_date","9999")));pending=sum(not x.get("completed") for x in a);done=len(a)-pending
        c=self.card(112);c.add_widget(self.lab("ASSIGNMENTS",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)));c.add_widget(self.lab("Tasks & due dates",24,UI_TEXT,True,size_hint_y=None,height=ui(36)));r=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(35));r.add_widget(self.lab(f"{pending} Pending",12,UI_WARNING,True));r.add_widget(self.lab(f"{done} Completed",12,UI_SUCCESS,True));r.add_widget(self.lab(f"{len(a)} Total",12,UI_ACCENT,True));c.add_widget(r);self.box.add_widget(c)
        add=AppButton(text="＋  ADD ASSIGNMENT",font_size=fs(13),background_color=UI_ACCENT,size_hint_y=None,height=ui(48));add.bind(on_press=lambda x:self.open_add());self.box.add_widget(add)
        if not a:
            c=self.card(150);c.add_widget(self.lab("NO TASKS YET",18,UI_TEXT,True));c.add_widget(self.lab("Add studio work, drawings, submissions and theory tasks here.",13,UI_MUTED));self.box.add_widget(c);return
        for i,item in enumerate(a):self.add_card(item,i,a)
    def add_card(self,item,index,ordered):
        completed=item.get("completed",False);due=item.get("due_date","No date");title=item.get("title","Untitled Assignment");subject=item.get("subject","No subject");priority=item.get("priority","Medium")
        try:
            d=date.fromisoformat(due);today=date.today();status="COMPLETED" if completed else ("OVERDUE" if d<today else "DUE TODAY" if d==today else "DUE TOMORROW" if (d-today).days==1 else f"DUE IN {(d-today).days} DAYS")
        except Exception:status="COMPLETED" if completed else "DUE DATE UNKNOWN"
        c=self.card(155);r=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(35));r.add_widget(self.lab(title,17,UI_TEXT,not completed));r.add_widget(self.lab(priority.upper(),10,UI_WARNING if priority=="High" else UI_MUTED,True,halign="right",size_hint_x=None,width=ui(70)));c.add_widget(r);c.add_widget(self.lab(f"{subject}   •   Due {due}\n{status}",12,UI_SUCCESS if completed else UI_DANGER if status=="OVERDUE" else UI_MUTED,size_hint_y=None,height=ui(42)));r=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(40));b=AppButton(text="UNDO" if completed else "MARK DONE",font_size=fs(11),background_color=UI_ACCENT_CONTAINER);d=AppButton(text="DELETE",font_size=fs(11),background_color=UI_SURFACE_2);b.bind(on_press=lambda x:self.toggle(index));d.bind(on_press=lambda x:self.delete(index));r.add_widget(b);r.add_widget(d);c.add_widget(r);self.box.add_widget(c)
    def open_add(self):
        box=BoxLayout(orientation="vertical",padding=ui(18),spacing=ui(9));title=TextInput(hint_text="Assignment title",multiline=False,font_size=fs(14),size_hint_y=None,height=ui(44));sub=Spinner(text=SUBJECTS[0],values=SUBJECTS,font_size=fs(13),size_hint_y=None,height=ui(44));due=TextInput(hint_text="Due date (YYYY-MM-DD)",multiline=False,font_size=fs(14),size_hint_y=None,height=ui(44));pri=Spinner(text="Medium",values=["Low","Medium","High"],font_size=fs(13),size_hint_y=None,height=ui(44));box.add_widget(title);box.add_widget(sub);box.add_widget(due);box.add_widget(pri);r=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(44));c=AppButton(text="CANCEL",font_size=fs(11));s=AppButton(text="SAVE",font_size=fs(11),background_color=UI_ACCENT);r.add_widget(c);r.add_widget(s);box.add_widget(r);p=Popup(title="ADD ASSIGNMENT",content=box,size_hint=(.92,.62),separator_height=0,background="",auto_dismiss=False);c.bind(on_press=lambda x:p.dismiss());s.bind(on_press=lambda x:self.save_new(p,title.text,sub.text,due.text,pri.text));p.open()
    def save_new(self,p,title,subject,due,priority):
        if not title.strip():return
        try:date.fromisoformat(due.strip())
        except Exception:return
        a=self.load();a.append({"title":title.strip(),"subject":subject,"due_date":due.strip(),"priority":priority,"completed":False});self.save(a);p.dismiss();self.refresh_assignments()
    def toggle(self,i):a=self.load();a.sort(key=lambda x:(x.get("completed",False),x.get("due_date","9999")));a[i]["completed"]=not a[i].get("completed",False);self.save(a);self.refresh_assignments()
    def delete(self,i):a=self.load();a.sort(key=lambda x:(x.get("completed",False),x.get("due_date","9999")));a.pop(i);self.save(a);self.refresh_assignments()
    def on_pre_enter(self,*a):self.refresh_assignments()
