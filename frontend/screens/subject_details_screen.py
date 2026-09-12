import json,os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.app import App
from backend.constants import SUBJECT_INFO,CLASS_TYPES,REQUIRED_ATTENDANCE,SUBJECTS
from backend.storage import get_teacher,save_teachers,get_subject_prep,save_subject_prep_for_subject,get_subject_assignments
from backend.attendance_service import get_subject_stats,classes_can_skip
from frontend.theme import *
from frontend.widgets.buttons import AppButton,IconButton
from frontend.widgets.navigation import BottomNav

class SubjectDetailsScreen(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs);self.subject=None;self.main=BoxLayout(orientation="vertical",padding=(ui(18),ui(8)),spacing=ui(10));rounded_background(self.main,UI_BG,0);self.scroll=ScrollView(do_scroll_y=True,bar_width=ui(4));self.box=BoxLayout(orientation="vertical",spacing=ui(16),size_hint_y=None,padding=(0,ui(2),0,ui(20)));self.box.bind(minimum_height=self.box.setter("height"));self.scroll.add_widget(self.box);self.main.add_widget(self.scroll);self.main.add_widget(BottomNav(current="subjects"));self.add_widget(self.main)
    def lab(self,t,size=14,color=UI_TEXT,bold=False,**kw):l=Label(text=t,font_size=fs(size),color=color,bold=bold,halign="left",valign="middle",**kw);l.bind(size=lambda i,v:setattr(i,"text_size",v));return l
    def card(self,h):c=BoxLayout(orientation="vertical",padding=(ui(20),ui(16)),spacing=ui(8),size_hint_y=None,height=ui(h));rounded_background(c,UI_SURFACE,22,UI_BORDER);return c
    def show_subject(self,s):self.subject=s;self.refresh()
    def refresh(self):
        if not self.subject:return
        s=self.subject;p,a,total,pct=get_subject_stats(s);pct=pct or 0;safe=pct>=75;col=UI_SUCCESS if safe else UI_DANGER;info=SUBJECT_INFO.get(s,{});self.box.clear_widgets()
        top=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(60));back=IconButton(text="‹");back.bind(on_press=lambda x:setattr(self.manager,"current","subjects"));top.add_widget(back);t=BoxLayout(orientation="vertical");t.add_widget(self.lab(f"{s}  •  {info.get('credits',0)} CREDITS",11,UI_ACCENT,True,size_hint_y=None,height=ui(20)));t.add_widget(self.lab(s,19,UI_TEXT,True));top.add_widget(t);self.box.add_widget(top)
        c=self.card(230);r=BoxLayout(orientation="horizontal",size_hint_y=None,height=ui(76));r.add_widget(self.lab("ATTENDANCE METRICS\n\n"+f"{pct:.0f}%",11,UI_ACCENT,True));r.add_widget(self.lab("REQUIRED\n75%",15,UI_TEXT,True,halign="right",size_hint_x=None,width=ui(80)));c.add_widget(r);counts=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(62));
        for name,val,color in [("PRESENT",p,UI_SUCCESS),("ABSENT",a,UI_DANGER),("MARKED",total,UI_ACCENT)]:
            b=BoxLayout(orientation="vertical",padding=(ui(8),ui(5)));rounded_background(b,UI_SURFACE_2,14);b.add_widget(self.lab(name,10,color,True,halign="center"));b.add_widget(self.lab(str(val),18,UI_TEXT,True,halign="center"));counts.add_widget(b)
        c.add_widget(counts);skip=classes_can_skip(p,total);msg=f"You can skip {skip} more {'class' if skip==1 else 'classes'} safely." if skip else (f"Need {max(0,int((.75*total-p)/(1-.75))+1)} consecutive attended classes to reach 75%." if total and pct<75 else "No safe skips remaining.");c.add_widget(self.lab(msg,12,col if skip or pct<75 else UI_MUTED,True,size_hint_y=None,height=ui(40)));self.box.add_widget(c)
        # instructor
        c=self.card(86);r=BoxLayout(orientation="horizontal");r.add_widget(self.lab("●  COURSE INSTRUCTOR\n"+str(get_teacher(s) or info.get("teacher") or "Teacher not set"),13,UI_TEXT,True));b=AppButton(text="EDIT",font_size=fs(11),background_color=UI_SURFACE_2,size_hint_x=None,width=ui(62));b.bind(on_press=lambda x:self.edit_teacher(s));r.add_widget(b);c.add_widget(r);self.box.add_widget(c)
        self.box.add_widget(self.lab("SYLLABUS",18,UI_TEXT,True,size_hint_y=None,height=ui(28)));c=self.card(220);c.add_widget(self.lab("\n".join(f"• {x}" for x in info.get("syllabus",[])),13,UI_MUTED));self.box.add_widget(c)
        prep=get_subject_prep(s);c=self.card(130);c.add_widget(self.lab("NEXT CLASS PREPARATION",17,UI_TEXT,True,size_hint_y=None,height=ui(26)));c.add_widget(self.lab("Bring: "+(prep.get("what_to_bring") or "Not set")+"\n"+(prep.get("notes") or "No notes"),12,UI_MUTED));e=AppButton(text="EDIT PREP",font_size=fs(10),background_color=UI_SURFACE_2,size_hint_y=None,height=ui(34));e.bind(on_press=lambda x:self.edit_prep(s));c.add_widget(e);self.box.add_widget(c)
        assigns=get_subject_assignments(s);c=self.card(max(90,70+len(assigns)*50));c.add_widget(self.lab(f"ASSIGNMENTS ({len(assigns)})",17,UI_TEXT,True,size_hint_y=None,height=ui(26)));c.add_widget(self.lab("\n".join(f"• {a.get('title','Untitled')} — {a.get('due_date','No date')}" for a in assigns) or "No assignments recorded.",12,UI_MUTED));self.box.add_widget(c)
    def edit_teacher(self,s):
        box=BoxLayout(orientation="vertical",padding=ui(16),spacing=ui(10));inp=TextInput(text=get_teacher(s) or "",multiline=False,font_size=fs(14),size_hint_y=None,height=ui(46));box.add_widget(self.lab("COURSE INSTRUCTOR",11,UI_MUTED,True));box.add_widget(inp);b=BoxLayout(orientation="horizontal",spacing=ui(8),size_hint_y=None,height=ui(44));cancel=AppButton(text="CANCEL",font_size=fs(11));save=AppButton(text="SAVE",font_size=fs(11),background_color=UI_ACCENT);b.add_widget(cancel);b.add_widget(save);box.add_widget(b);p=Popup(title="EDIT INSTRUCTOR",content=box,size_hint=(.9,.38),separator_height=0,background="",auto_dismiss=False);cancel.bind(on_press=lambda x:p.dismiss());save.bind(on_press=lambda x:self.save_teacher(p,s,inp.text));p.open()
    def save_teacher(self,p,s,v):
        data={};f=os.path.join(App.get_running_app().user_data_dir,"teachers.json")
        try:
            with open(f) as h:data=json.load(h)
        except Exception:pass
        data[s]=v.strip();save_teachers(data);p.dismiss();self.refresh()
    def edit_prep(self,s):
        old=get_subject_prep(s);box=BoxLayout(orientation="vertical",padding=ui(16),spacing=ui(8));bring=TextInput(text=old.get("what_to_bring", ""),multiline=False,font_size=fs(13),size_hint_y=None,height=ui(44));notes=TextInput(text=old.get("notes", ""),multiline=True,font_size=fs(13));box.add_widget(self.lab("WHAT TO BRING",11,UI_MUTED,True));box.add_widget(bring);box.add_widget(self.lab("NOTES",11,UI_MUTED,True));box.add_widget(notes);b=AppButton(text="SAVE",font_size=fs(12),background_color=UI_ACCENT,size_hint_y=None,height=ui(44));box.add_widget(b);p=Popup(title="EDIT PREPARATION",content=box,size_hint=(.92,.58),separator_height=0,background="",auto_dismiss=False);b.bind(on_press=lambda x:(save_subject_prep_for_subject(s,bring.text,notes.text),p.dismiss(),self.refresh()));p.open()
    def on_pre_enter(self,*a):self.refresh()
