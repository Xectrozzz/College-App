from datetime import datetime, date
import json, os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from backend.constants import SUBJECTS, TIMES, REQUIRED_ATTENDANCE, SPECIAL_SATURDAYS
from backend.storage import attendance_key, save_attendance, get_subject_prep
from backend.attendance_service import get_subject_stats, classes_can_skip, get_slot_subject, get_slot_type, is_class_cancelled, get_semester_status
from frontend.theme import *
from frontend.widgets.buttons import AppButton, make_stat_box, make_link_card
from frontend.widgets.navigation import BottomNav
from frontend.widgets.progress_ring import AttendanceRing
from frontend.popups.attendance_popup import AttendancePopup

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main = BoxLayout(orientation="vertical", padding=(ui(18),ui(12),ui(18),ui(8)), spacing=ui(10))
        rounded_background(self.main, UI_BG, 0)
        self.scroll = ScrollView(do_scroll_y=True, bar_width=ui(4))
        self.content = BoxLayout(orientation="vertical", spacing=ui(16), size_hint_y=None, padding=(0,ui(4),0,ui(20)))
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)
        self.main.add_widget(self.scroll)
        self.main.add_widget(BottomNav(current="home"))
        self.add_widget(self.main)
        self.refresh_event = Clock.schedule_interval(lambda dt:self.update_dashboard(), 30)

    def _label(self, text, size=14, color=UI_TEXT, bold=False, **kw):
        l=Label(text=text,font_size=fs(size),color=color,bold=bold,**kw)
        l.bind(size=lambda i,v:setattr(i,"text_size",v))
        return l

    def card(self, height=120):
        b=BoxLayout(orientation="vertical",padding=(ui(18),ui(14)),spacing=ui(8),size_hint_y=None,height=ui(height))
        rounded_background(b,UI_SURFACE,22,UI_BORDER)
        return b

    def update_dashboard(self):
        self.content.clear_widgets()
        today=date.today(); now=datetime.now()
        # Header
        header=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(76),spacing=ui(10))
        left=BoxLayout(orientation="vertical",spacing=ui(1))
        left.add_widget(self._label("B.ARCH SECTION A",12,UI_ACCENT,True,size_hint_y=None,height=ui(22)))
        left.add_widget(self._label(today.strftime("%A, %-d %B %Y") if os.name!='nt' else today.strftime("%A, %#d %B %Y"),24,UI_TEXT,True))
        header.add_widget(left)
        p=0;t=0
        for s in SUBJECTS:
            a,b,total,pct=get_subject_stats(s);p+=a;t+=total
        overall=(p/t*100) if t else 0
        pill=AppButton(text=f"●  {overall:.0f}%",font_size=fs(14),background_color=UI_SURFACE_2,size_hint_x=None,width=ui(92))
        pill.color=UI_SUCCESS if overall>=75 else UI_DANGER
        pill.bind(on_press=lambda x:setattr(self.manager,"current","subjects")); header.add_widget(pill)
        self.content.add_widget(header)
        status=get_semester_status(today)
        if status:
            c=self.card(58); c.add_widget(self._label("◈  ACADEMIC STATUS: "+status.replace("\n"," • "),12,UI_SPECIAL if "HOLIDAY" not in status else UI_SUCCESS,True)); self.content.add_widget(c)
        # Hero
        current=self._find_current(today,now); nxt=self._find_next(today,now)
        hero=self.card(178)
        target=current or nxt
        hero.add_widget(self._label("CURRENT CLASS" if current else "NEXT CLASS",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)))
        if target:
            subject,time,typ=target
            row=BoxLayout(orientation="horizontal",spacing=ui(12))
            info=BoxLayout(orientation="vertical")
            info.add_widget(self._label(subject,21,UI_TEXT,True,size_hint_y=None,height=ui(40)))
            info.add_widget(self._label(f"{time}  •  {typ or 'LECTURE'}",13,UI_ACCENT,True,size_hint_y=None,height=ui(28)))
            prep=get_subject_prep(subject)
            extra=[]
            if prep.get("what_to_bring"): extra.append("Bring: "+prep["what_to_bring"])
            if prep.get("notes"): extra.append(prep["notes"])
            info.add_widget(self._label("\n".join(extra) if extra else "Tap to mark attendance",12,UI_MUTED,False))
            row.add_widget(info)
            open_btn=AppButton(text="MARK",font_size=fs(12),background_color=UI_ACCENT_CONTAINER,size_hint_x=None,width=ui(70))
            open_btn.bind(on_press=lambda x,s=subject,tm=time,dt=today,tp=typ: AttendancePopup(s,dt.isoformat(),tm,tp).open())
            row.add_widget(open_btn); hero.add_widget(row)
        else: hero.add_widget(self._label("No upcoming class",17,UI_MUTED,True))
        self.content.add_widget(hero)
        # Unmarked
        unmarked=0; scheduled=0
        day=today.strftime("%A").upper() if today.weekday()<5 else SPECIAL_SATURDAYS.get(today)
        if day and not status:
            for i,s in enumerate([get_slot_subject(day,j) for j in range(len(TIMES))]):
                if s and s!="LUNCH BREAK" and not is_class_cancelled(today.isoformat(),s,TIMES[i]):
                    scheduled+=1
                    typ=get_slot_type(day,i) or "LECTURE"
                    if attendance_key(today.isoformat(),s,TIMES[i],typ) not in App.get_running_app().attendance_data and attendance_key(today.isoformat(),s,TIMES[i]) not in App.get_running_app().attendance_data: unmarked+=1
        c=self.card(82); c.add_widget(self._label(f"{unmarked} UNMARKED CLASSES TODAY",17,UI_TEXT,True,size_hint_y=None,height=ui(28))); c.add_widget(self._label("Tap Timetable to mark attendance" if unmarked else "All scheduled classes are marked",12,UI_MUTED)); self.content.add_widget(c)
        # Today schedule
        c=self.card(200); c.add_widget(self._label("TODAY'S SCHEDULE",17,UI_TEXT,True,size_hint_y=None,height=ui(26)))
        lines=[]
        if day and not status:
            for i,s in enumerate([get_slot_subject(day,j) for j in range(len(TIMES))]):
                if s=="LUNCH BREAK": lines.append(f"{TIMES[i]}   •   LUNCH")
                elif s: lines.append(f"{TIMES[i]}   •   {s}   •   {get_slot_type(day,i) or 'LECTURE'}")
        c.add_widget(self._label("\n".join(lines) if lines else "No classes scheduled",13,UI_MUTED))
        btn=AppButton(text="OPEN TIMETABLE  →",font_size=fs(12),background_color=UI_SURFACE_2,size_hint_y=None,height=ui(38)); btn.bind(on_press=lambda x:setattr(self.manager,"current","timetable")); c.add_widget(btn); self.content.add_widget(c)
        # quick links
        self.content.add_widget(self._label("QUICK ACCESS",17,UI_TEXT,True,size_hint_y=None,height=ui(26)))
        grid=GridLayout(cols=2,spacing=ui(10),size_hint_y=None,height=ui(92));
        grid.add_widget(make_link_card("SUBJECTS","Attendance & details",lambda x:setattr(self.manager,"current","subjects"),height=92))
        grid.add_widget(make_link_card("ASSIGNMENTS","Tasks & due dates",lambda x:setattr(self.manager,"current","assignments"),height=92)); self.content.add_widget(grid)
        # assignment preview
        assignments=self._load_assignments(); pending=[a for a in assignments if not a.get("completed")]; pending.sort(key=lambda a:a.get("due_date","9999"))
        c=self.card(145); c.add_widget(self._label(f"UPCOMING TASKS  •  {len(pending)} PENDING",16,UI_TEXT,True,size_hint_y=None,height=ui(25)))
        c.add_widget(self._label("\n".join(f"• {a.get('title','Untitled')}  —  {a.get('due_date','No date')}" for a in pending[:3]) or "No pending assignments",13,UI_MUTED))
        self.content.add_widget(c)

    def _find_current(self,today,now):
        day=today.strftime("%A").upper() if today.weekday()<5 else SPECIAL_SATURDAYS.get(today)
        if not day:return None
        m=now.hour*60+now.minute
        for i,s in enumerate([get_slot_subject(day,j) for j in range(len(TIMES))]):
            if not s or s=="LUNCH BREAK" or is_class_cancelled(today.isoformat(),s,TIMES[i]):continue
            a,b=TIMES[i].split(" - "); sm=sum(int(x)*v for x,v in zip(a.split(":"),(60,1))); em=sum(int(x)*v for x,v in zip(b.split(":"),(60,1)))
            if sm<=m<em:return s,TIMES[i],get_slot_type(day,i) or "LECTURE"
        return None
    def _find_next(self,today,now):
        day=today.strftime("%A").upper() if today.weekday()<5 else SPECIAL_SATURDAYS.get(today)
        if not day:return None
        m=now.hour*60+now.minute
        for i,s in enumerate([get_slot_subject(day,j) for j in range(len(TIMES))]):
            if not s or s=="LUNCH BREAK":continue
            a=TIMES[i].split(" - ")[0]; sm=int(a.split(":")[0])*60+int(a.split(":")[1])
            if sm>m and not is_class_cancelled(today.isoformat(),s,TIMES[i]):return s,TIMES[i],get_slot_type(day,i) or "LECTURE"
        return None
    def _load_assignments(self):
        f=os.path.join(App.get_running_app().user_data_dir,"assignments.json")
        try:
            with open(f) as h:return json.load(h)
        except Exception:return []
    def on_pre_enter(self,*a):self.update_dashboard()
