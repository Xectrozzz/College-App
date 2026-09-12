from datetime import date,timedelta,datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.app import App
from backend.constants import TIMES,SUBJECTS,CLASS_TYPES,SPECIAL_SATURDAYS
from backend.storage import load_timetable,save_timetable,get_slot_entry,attendance_key
from backend.attendance_service import get_slot_subject,get_slot_type,is_class_cancelled,get_semester_status
from frontend.theme import *
from frontend.widgets.buttons import AppButton,IconButton
from frontend.widgets.navigation import BottomNav
from frontend.popups.attendance_popup import AttendancePopup

class TimetableScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs);self.week_offset=0;self.selected_day_index=date.today().weekday();self.filter_mode="ALL";self.edit_mode=False
        self.main=BoxLayout(orientation="vertical",padding=(ui(18),ui(10),ui(18),ui(8)),spacing=ui(8));rounded_background(self.main,UI_BG,0)
        top=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(60),spacing=ui(7));back=IconButton(text="‹");back.bind(on_press=lambda x:self.go_back());top.add_widget(back)
        tb=BoxLayout(orientation="vertical",spacing=0);self.title=Label(text="TIMETABLE",font_size=fs(21),bold=True,color=UI_TEXT,size_hint_y=None,height=ui(30));self.month=Label(text="",font_size=fs(11),bold=True,color=UI_MUTED,size_hint_y=None,height=ui(20));tb.add_widget(self.title);tb.add_widget(self.month);top.add_widget(tb)
        self.edit=AppButton(text="EDIT",font_size=fs(11),background_color=UI_SURFACE_2,size_hint_x=None,width=ui(66));self.edit.bind(on_press=lambda x:self.toggle_edit());top.add_widget(self.edit)
        today=AppButton(text="TODAY",font_size=fs(11),background_color=UI_ACCENT_CONTAINER,size_hint_x=None,width=ui(74));today.bind(on_press=lambda x:self.go_today());top.add_widget(today);self.main.add_widget(top)
        nav=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(40),spacing=ui(7));p=IconButton(text="‹");p.bind(on_press=lambda x:self.change_week(-1));n=IconButton(text="›");n.bind(on_press=lambda x:self.change_week(1));self.week=Label(text="",font_size=fs(13),bold=True,color=UI_TEXT,halign="center",valign="middle");self.week.bind(size=lambda i,v:setattr(i,"text_size",v));nav.add_widget(p);nav.add_widget(self.week);nav.add_widget(n);self.main.add_widget(nav)
        self.days=BoxLayout(orientation="horizontal",spacing=ui(5),size_hint_y=None,height=ui(68));self.main.add_widget(self.days)
        hdr=BoxLayout(orientation="horizontal",spacing=ui(6),size_hint_y=None,height=ui(44));self.selected=Label(text="",font_size=fs(16),bold=True,color=UI_TEXT);self.selected.bind(size=lambda i,v:setattr(i,"text_size",v));hdr.add_widget(self.selected)
        self.filters={};
        for mode,w in [("ALL",55),("UNMARKED",82),("MARKED",65)]:
            b=AppButton(text=mode,font_size=fs(9),background_color=UI_SURFACE_2,size_hint_x=None,width=ui(w));b.bind(on_press=lambda x,m=mode:self.set_filter(m));self.filters[mode]=b;hdr.add_widget(b)
        self.main.add_widget(hdr)
        self.scroll=ScrollView(do_scroll_y=True,bar_width=ui(4));self.timeline=BoxLayout(orientation="vertical",spacing=ui(9),size_hint_y=None,padding=(0,ui(2),0,ui(18)));self.timeline.bind(minimum_height=self.timeline.setter("height"));self.scroll.add_widget(self.timeline);self.main.add_widget(self.scroll);self.main.add_widget(BottomNav(current="timetable"));self.add_widget(self.main)
    def go_back(self):self.manager.current="home"
    def go_today(self):self.week_offset=0;self.selected_day_index=max(0,min(6,date.today().weekday()));self.refresh_grid()
    def change_week(self,n):self.week_offset+=n;self.refresh_grid()
    def select_day(self,i):self.selected_day_index=i;self.refresh_grid()
    def set_filter(self,m):self.filter_mode=m;self.refresh_grid()
    def toggle_edit(self):self.edit_mode=not self.edit_mode;self.edit.text="DONE" if self.edit_mode else "EDIT";self.refresh_grid()
    def monday(self):return date.today()-timedelta(days=date.today().weekday())+timedelta(days=self.week_offset*7)
    def timetable_day(self,d):
        if d.weekday()==6:return None
        if d.weekday()==5:return SPECIAL_SATURDAYS.get(d)
        return d.strftime("%A").upper()
    def refresh_grid(self):
        m=self.monday();self.week.text=f"{m.strftime('%d %b')}  –  {(m+timedelta(days=6)).strftime('%d %b %Y')}";self.month.text=m.strftime("%B %Y");self.build_days(m);self.timeline.clear_widgets();d=m+timedelta(days=self.selected_day_index);self.selected.text=f"{d.strftime('%A')}  •  {d.strftime('%d %B')}"
        for k,b in self.filters.items():b.background_color=UI_ACCENT_CONTAINER if k==self.filter_mode else UI_SURFACE_2
        status=get_semester_status(d)
        if status:
            c=self.card(110);c.add_widget(self.lab(status.replace("\n"," • "),20,UI_TEXT,True));c.add_widget(self.lab("No classes can be marked on this date.",12,UI_MUTED));self.timeline.add_widget(c);return
        day=self.timetable_day(d)
        if not day:self.empty("No classes scheduled for Sunday.");return
        added=0
        for i in range(len(TIMES)):
            entry=get_slot_entry(day,i);s=entry.get("subject","");typ=entry.get("type","");tm=TIMES[i]
            if not s:
                if self.edit_mode:self.add_slot(d,day,i,tm,None,None)
                elif self.filter_mode=="ALL":self.add_free(tm)
                continue
            if s=="LUNCH BREAK":
                if self.filter_mode=="ALL":self.add_special(tm,"LUNCH BREAK",UI_LUNCH)
                continue
            rec=self.attendance_record(d,s,tm,typ);marked=rec is not None
            if self.filter_mode=="MARKED" and not marked:continue
            if self.filter_mode=="UNMARKED" and marked:continue
            self.add_slot(d,day,i,tm,s,typ,rec);added+=1
        if not added and not self.edit_mode:self.empty("No classes match this filter.")
    def build_days(self,m):
        self.days.clear_widgets()
        for i,name in enumerate(["MON","TUE","WED","THU","FRI","SAT","SUN"]):
            d=m+timedelta(days=i);active=i==self.selected_day_index;today=d==date.today();txt=f"{name}\n{d.day}"+("\nTODAY" if today else "")
            b=AppButton(text=txt,font_size=fs(10),background_color=UI_ACCENT_CONTAINER if active else UI_SURFACE_2,size_hint_x=1);b.color=UI_ACCENT if active else UI_MUTED;b.bind(on_press=lambda x,j=i:self.select_day(j));self.days.add_widget(b)
    def attendance_record(self,d,s,tm,typ):
        app=App.get_running_app();return app.attendance_data.get(attendance_key(d.isoformat(),s,tm,typ)) or app.attendance_data.get(attendance_key(d.isoformat(),s,tm))
    def card(self,h):c=BoxLayout(orientation="vertical",padding=(ui(16),ui(12)),spacing=ui(5),size_hint_y=None,height=ui(h));rounded_background(c,UI_SURFACE,20,UI_BORDER);return c
    def lab(self,t,size=13,color=UI_TEXT,bold=False):l=Label(text=t,font_size=fs(size),color=color,bold=bold,halign="left",valign="middle");l.bind(size=lambda i,v:setattr(i,"text_size",v));return l
    def empty(self,msg):c=self.card(92);c.add_widget(self.lab(msg,14,UI_MUTED,True));self.timeline.add_widget(c)
    def add_free(self,tm):self.add_special(tm,"FREE PERIOD",UI_FREE)
    def add_special(self,tm,title,color):
        c=BoxLayout(orientation="horizontal",spacing=ui(12),size_hint_y=None,height=ui(74));c.add_widget(self.lab(tm.replace(" - ","\n"),11,UI_MUTED,True));b=BoxLayout(orientation="vertical",padding=(ui(14),ui(10)),size_hint_x=1);rounded_background(b,UI_SURFACE_2,16);b.add_widget(self.lab(title,14,color,True));c.add_widget(b);self.timeline.add_widget(c)
    def add_slot(self,d,day,i,tm,s,typ,rec=None):
        row=BoxLayout(orientation="horizontal",spacing=ui(10),size_hint_y=None,height=ui(86));row.add_widget(self.lab(tm.replace(" - ","\n"),11,UI_MUTED,True,size_hint_x=None,width=ui(68)))
        if self.edit_mode:
            b=AppButton(text=("ADD CLASS" if not s else f"{s}\n{typ or 'LECTURE'}"),font_size=fs(12),background_color=UI_SURFACE_2,size_hint_x=1);b.bind(on_press=lambda x:self.open_editor(day,i));row.add_widget(b)
        else:
            b=AppButton(text=f"{s}\n{typ or 'LECTURE'}\n"+("✓ PRESENT" if rec and rec.get("status")=="present" else "✕ ABSENT" if rec else "UNMARKED"),font_size=fs(11),background_color=UI_SUCCESS_CONTAINER if rec and rec.get("status")=="present" else UI_DANGER_CONTAINER if rec else UI_SURFACE_2,size_hint_x=1);b.color=UI_SUCCESS if rec and rec.get("status")=="present" else UI_DANGER if rec else UI_TEXT;b.bind(on_press=lambda x,ss=s,tt=tm,ty=typ:self.open_attendance(d,ss,tt,ty));row.add_widget(b)
        self.timeline.add_widget(row)
    def open_attendance(self,d,s,tm,typ):AttendancePopup(s,d.isoformat(),tm,typ).open()
    def open_editor(self,day,i):
        entry=get_slot_entry(day,i);box=BoxLayout(orientation="vertical",padding=ui(18),spacing=ui(10));rounded_background(box,UI_SURFACE,20,UI_BORDER)
        subj=Spinner(text=entry.get("subject") or "FREE PERIOD",values=["FREE PERIOD"]+SUBJECTS,font_size=fs(13),size_hint_y=None,height=ui(46));typ=Spinner(text=entry.get("type") or "LECTURE",values=CLASS_TYPES,font_size=fs(13),size_hint_y=None,height=ui(46));box.add_widget(self.lab("SUBJECT",11,UI_MUTED,True));box.add_widget(subj);box.add_widget(self.lab("CLASS TYPE",11,UI_MUTED,True));box.add_widget(typ)
        buttons=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(46));cancel=AppButton(text="CANCEL",font_size=fs(12),background_color=UI_SURFACE_2);save=AppButton(text="SAVE",font_size=fs(12),background_color=UI_ACCENT);clear=AppButton(text="CLEAR",font_size=fs(12),background_color=UI_DANGER_CONTAINER);buttons.add_widget(cancel);buttons.add_widget(clear);buttons.add_widget(save);box.add_widget(buttons);pop=Popup(title="EDIT CLASS",content=box,size_hint=(.9,.55),separator_height=0,background="",auto_dismiss=False);cancel.bind(on_press=lambda x:pop.dismiss());clear.bind(on_press=lambda x:(self.save_slot(day,i,"",""),pop.dismiss()));save.bind(on_press=lambda x:(self.save_slot(day,i,"" if subj.text=="FREE PERIOD" else subj.text,typ.text),pop.dismiss()));pop.open()
    def save_slot(self,day,i,subject,typ):
        data=load_timetable();data.setdefault(day,[{"subject":"","type":""} for _ in TIMES]);data[day][i]={"subject":subject,"type":typ if subject else ""};save_timetable(data);self.refresh_grid()
    def on_pre_enter(self,*a):self.refresh_grid()
