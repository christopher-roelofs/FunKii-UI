# -*- coding: utf-8 -*-


try: #Python 2 imports
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog
    from HTMLParser import HTMLParser
    
except ImportError: #Python 3 imports
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from html.parser import HTMLParser
    
import os    
import FunKiiU as fnku
import json
import zipfile
from AutoComplete import AutocompleteCombobox
from distutils.version import LooseVersion
import binascii
import sys
import sqlite3

urlopen=fnku.urlopen
URLError=fnku.URLError
HTTPError=fnku.HTTPError
PhotoImage=tk.PhotoImage
py_ver=sys.version_info[0]

__VERSION__="2.1.2"
targetversion="FunKiiU v2.2"
current_gui=LooseVersion(__VERSION__)

DEBUG = True

if os.name == 'nt':
    dir_slash = "\\"
else:
    dir_slash = "/"
try:
    fnku_VERSION_ = str(fnku.__VERSION__)
    current_fnku=LooseVersion(fnku_VERSION_)
except:
    fnku.__VERSION__ = "?"
    current_fnku=LooseVersion('0')




class VersionParser(HTMLParser):
    fnku_data_set=[]
    gui_data_set=[]
    
    def handle_starttag(self, tag, attrs):
        fnku_data_set=[]
        gui_data_set=[]
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if value.startswith("/llakssz") and value.endswith(".zip"):
                        self.fnku_data_set.append(value)
                    elif value.startswith("/dojafoja") and value.endswith(".zip"):
                        self.gui_data_set.append(value)

                
class RootWindow(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self)
        self.versions={'gui_new':'','gui_all':'','gui_url':'https://github.com/dojafoja/FunKii-UI/releases','fnku_new':'','fnku_all':'',
                       'fnku_url':'https://github.com/llakssz/FunKiiU/releases'}

        self.download_list=[]
        self.selection_list=[]
        self.title_data=[]
        self.nb = ttk.Notebook(self)
        tab1 = ttk.Frame(self.nb)
        self.tab2 = ttk.Frame(self.nb)
        tab3 = ttk.Frame(self.nb)
        tab4 = ttk.Frame(self.nb)
        self.nb.add(tab1,text="Welcome")
        self.nb.add(self.tab2,text="Download")
        self.nb.add(tab3,text="Options")
        self.nb.add(tab4,text="Updates")
        self.nb.pack(fill="both", expand=True)
        self.output_dir=tk.StringVar()
        self.retry_count=tk.IntVar(value=3)
        self.patch_demo=tk.BooleanVar(value=True)
        self.patch_dlc=tk.BooleanVar(value=True)
        self.tickets_only=tk.BooleanVar(value=False)
        self.simulate_mode=tk.BooleanVar(value=False)
        self.region_usa=tk.BooleanVar(value=False)
        self.region_eur=tk.BooleanVar(value=False)
        self.region_jpn=tk.BooleanVar(value=False)
        self.filter_usa=tk.BooleanVar(value=True)
        self.filter_eur=tk.BooleanVar(value=True)
        self.filter_jpn=tk.BooleanVar(value=True)
        self.filter_game=tk.BooleanVar(value=True)
        self.filter_dlc=tk.BooleanVar(value=True)
        self.filter_update=tk.BooleanVar(value=True)
        self.filter_hasticket=tk.BooleanVar(value=False)
        self.total_dl_size=tk.StringVar()
        self.total_dl_size_warning=tk.StringVar()
        self.dl_warning_msg = "     ! You have one or more items in the list with an unknown size. This probably means\n        the tmd can not be downloaded and the title will be skipped by FunKiiU."
        self.idvar=tk.StringVar()
        self.idvar.trace('w',self.id_changed)
        self.usa_selections={'game':[],'dlc':[],'update':[]}
        self.eur_selections={'game':[],'dlc':[],'update':[]}
        self.jpn_selections={'game':[],'dlc':[],'update':[]}
        self.title_sizes_raw={}
        self.title_sizes={}
        self.reverse_title_names={}
        self.title_dict={}
        self.has_ticket=[]
        self.errors=0
        

        # Tab 1
        t1_frm1=ttk.Frame(tab1)   
        t1_frm2=ttk.Frame(tab1)
        t1_frm3=ttk.Frame(tab1)
        t1_frm4=ttk.Frame(tab1)
        t1_frm5=ttk.Frame(tab1)
        t1_frm6=ttk.Frame(tab1)
        
        self.img = PhotoImage(file='logo.gif')
        logo=ttk.Label(t1_frm1,image=self.img).pack()
        lbl=ttk.Label(t1_frm2,justify='center',text='This is a simple GUI by dojafoja that was written for FunKiiU.\nCredits to cearp for writing FunKiiU and cerea1killer for rewriting\n it in way that made writing a GUI much easier.').pack()
        lbl=ttk.Label(t1_frm3,justify='center',text='If you plan on using an online methond to obtain keys or tickets\n then FunKiiU will need to know the name of *that key site*. If you\nhaven\'t already provided the address to the key site, you MUST do so\nbelow before proceeding. You only need to provide this information once!').pack(pady=15)
        self.enterkeysite_lbl=ttk.Label(t1_frm4,text='Enter the name of *that key site*. Something like wiiu.thatkeysite.com')
        self.enterkeysite_lbl.pack(pady=15,side='left')
        self.http_lbl=ttk.Label(t1_frm5,text='http://')
        self.http_lbl.pack(pady=15,side='left')
        self.keysite_box=ttk.Entry(t1_frm5,width=40)
        self.keysite_box.pack(pady=15,side='left')
        self.submitkeysite_btn=ttk.Button(t1_frm6,text='submit',command=self.submit_key_site)
        self.submitkeysite_btn.pack()
        self.updatelabel=ttk.Label(t1_frm6,text='')
        self.updatelabel.pack(pady=15)
        
        t1_frm1.pack()
        t1_frm2.pack()
        t1_frm3.pack()
        t1_frm4.pack()
        t1_frm5.pack()
        t1_frm6.pack()

        self.load_program_revisions()
        self.check_config_keysite()
        
        # Tab2
        t2_frm0=ttk.Frame(self.tab2)
        t2_frm1=ttk.Frame(self.tab2)
        t2_frm2=ttk.Frame(self.tab2)   
        t2_frm3=ttk.Frame(self.tab2)
        t2_frm4=ttk.Frame(self.tab2)
        t2_frm5=ttk.Frame(self.tab2)
        t2_frm6=ttk.Frame(self.tab2)
        t2_frm7=ttk.Frame(self.tab2)
        t2_frm8=ttk.Frame(self.tab2)
        t2_frm9=ttk.Frame(self.tab2)
        t2_frm10=ttk.Frame(self.tab2)
        t2_frm11=ttk.Frame(self.tab2)
        
        lbl=ttk.Label(t2_frm0,text='Enter as many Title ID\'s as you would like to the list. If you are going to use the key method to download then be sure a key is provided for every title\nyou add to the list or it will fail. Use the selection box to make life easier, it has auto-complete. You can always enter a title Id and key manually.').pack(padx=5,pady=7)
        lbl=ttk.Label(t2_frm1,text='Choose regions to display:').pack(padx=5,pady=5,side='left')
        filter_box_usa=ttk.Checkbutton(t2_frm1,text='USA',variable=self.filter_usa,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_eur=ttk.Checkbutton(t2_frm1,text='EUR',variable=self.filter_eur,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_jpn=ttk.Checkbutton(t2_frm1,text='JPN',variable=self.filter_jpn,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm2,text='Choose content to display:').pack(padx=5,pady=5,side='left')
        filter_box_usa=ttk.Checkbutton(t2_frm2,text='Game',variable=self.filter_game,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_eur=ttk.Checkbutton(t2_frm2,text='Update',variable=self.filter_update,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_jpn=ttk.Checkbutton(t2_frm2,text='DLC',variable=self.filter_dlc,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        filter_box_ticket=ttk.Checkbutton(t2_frm2,text='Only show items with an online ticket',variable=self.filter_hasticket,command=lambda:self.populate_selection_box(download_data=False)).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm3,text='Selection:').pack(padx=5,pady=7,side='left')
        self.selection_box=AutocompleteCombobox(t2_frm3,values=(self.selection_list),width=73)
        self.selection_box.bind('<<ComboboxSelected>>', self.selection_box_changed)
        self.selection_box.bind('<Return>', self.selection_box_changed)

        ## Change the selection box behavior slightly to clear title id and key boxes on any
        ## non-hits while auto completing. Not sure which is more preferred. 
        #self.selection_box.bind('<<NoHits>>', self.clear_id_key_boxes)
        
        self.selection_box.pack(padx=5,pady=7,side='left')
        btn=ttk.Button(t2_frm3,text='refresh',width=8,command=self.populate_selection_box).pack(side='left')
        lbl=ttk.Label(t2_frm4,text='Title ID:').pack(padx=5,pady=7,side='left')
        self.id_box=ttk.Entry(t2_frm4,width=40,textvariable=self.idvar)
        self.id_box.pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t2_frm4,text='Add to list',command=self.add_to_list).pack(padx=5,pady=5,side='left')
        self.dl_size_lbl=ttk.Label(t2_frm4,text='Size:,',font='Helvetica 10 bold')
        self.dl_size_lbl.pack(side='left')
        lbl=ttk.Label(t2_frm4,text='Online ticket:',font='Helvetica 10 bold').pack(side='left',padx=5)
        self.has_ticket_lbl=ttk.Label(t2_frm4,text='',font='Helvetica 10 bold')
        self.has_ticket_lbl.pack(side='left')
        lbl=ttk.Label(t2_frm5,text='Key:').pack(padx=5,pady=7,side='left')
        self.key_box=ttk.Entry(t2_frm5,width=40)
        self.key_box.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t2_frm6,text='Download list:').pack()
        #lbl=ttk.Label(t2_frm6,text='Items marked with * have a key provided. Items marked with ! have an unknown size.').pack()
        dl_scroller=ttk.Scrollbar(t2_frm6,orient='vertical')
        dl_scroller.pack(side='right',fill='y')
        self.dl_listbox=tk.Listbox(t2_frm6,width=78,height=12)
        self.dl_listbox.pack(fill='y',pady=3)
        self.dl_listbox.config(yscrollcommand=dl_scroller.set)
        dl_scroller.config(command=self.dl_listbox.yview)
        btn=ttk.Button(t2_frm7,text='Remove selected',command=self.remove_from_list).pack(padx=3,pady=2,side='left',anchor='w')
        btn=ttk.Button(t2_frm7,text='Clear list',command=self.clear_list).pack(padx=3,pady=2,side='left')
        lbl=ttk.Label(t2_frm8,text='',textvariable=self.total_dl_size,font='Helvetica 10 bold').pack(side='left')
        lbl=ttk.Label(t2_frm10,text='',textvariable=self.total_dl_size_warning,foreground='red').pack(side='left')
        lbl=ttk.Label(t2_frm9,justify='center',text='Add an entry to the download list one at a time.\nWhen you are done, click on a download button\nbelow based on your preferred method. Items marked\nwith * have a key provided and items marked with ! have\nan unknown size. Don\'t forget to visit the options tab\nbefore you download.').pack(padx=20,pady=10)
        btn=ttk.Button(t2_frm11,text='Download using online tickets',width=30,command=lambda:self.download_clicked(1)).pack(padx=5,pady=10,side='left')
        btn=ttk.Button(t2_frm11,text='Download using keys method',width=30,command=lambda:self.download_clicked(2)).pack(padx=5,pady=10,side='left')

        self.load_title_sizes()
        self.populate_selection_box()
        self.total_dl_size.set('Total Size:')
        
        
        t2_frm0.grid(row=0,column=1,columnspan=3,sticky='w')
        t2_frm1.grid(row=1,column=1,sticky='w')
        t2_frm2.grid(row=2,column=1,columnspan=2,sticky='w')
        t2_frm3.grid(row=3,column=1,columnspan=2,sticky='w')
        t2_frm4.grid(row=4,column=1,columnspan=3,sticky='w')
        t2_frm5.grid(row=5,column=1,sticky='w')
        t2_frm6.grid(row=6,column=2,rowspan=3,columnspan=3,sticky='e')
        t2_frm7.grid(row=9,column=3,sticky='e')
        t2_frm8.grid(row=9,column=2,padx=20,sticky='w')
        t2_frm9.grid(row=6,column=1,sticky='w')
        t2_frm10.grid(row=10,column=2,padx=5,columnspan=2,sticky='nw')
        t2_frm11.grid(row=11,column=2,columnspan=3)
        
        
        # Tab3
        t3_frm1=ttk.Frame(tab3)
        t3_frm2=ttk.Frame(tab3)
        t3_frm3=ttk.Frame(tab3)
        t3_frm4=ttk.Frame(tab3)
        t3_frm5=ttk.Frame(tab3)
        t3_frm6=ttk.Frame(tab3)
        t3_frm7=ttk.Frame(tab3)
        t3_frm8=ttk.Frame(tab3)
        
        lbl=ttk.Label(t3_frm1,text='To use the default output directory, leave the entry blank').pack(padx=5,pady=10,side='left')
        lbl=ttk.Label(t3_frm2,text='Output directory').pack(padx=5,pady=5,side='left')
        self.out_dir_box=ttk.Entry(t3_frm2,width=35,textvariable=self.output_dir)
        self.out_dir_box.pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t3_frm2,text='Browse',command=self.get_output_directory).pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm3,text='Retry count:').pack(padx=5,pady=5,side='left')
        self.retry_count_box=ttk.Combobox(t3_frm3,state='readonly',width=5,values=range(10),textvariable=self.retry_count)
        self.retry_count_box.set(3)
        self.retry_count_box.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm4,text='Patch demo play limit:').pack(padx=5,pady=5,side='left')
        self.patch_demo_true=ttk.Radiobutton(t3_frm4,text='Yes',variable=self.patch_demo,value=True)
        self.patch_demo_false=ttk.Radiobutton(t3_frm4,text='No',variable=self.patch_demo,value=False)
        self.patch_demo_true.pack(padx=5,pady=5,side='left')
        self.patch_demo_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm5,text='Patch DLC:').pack(padx=5,pady=5,side='left')
        self.patch_dlc_true=ttk.Radiobutton(t3_frm5,text='Yes',variable=self.patch_dlc,value=True)
        self.patch_dlc_false=ttk.Radiobutton(t3_frm5,text='No',variable=self.patch_dlc,value=False)
        self.patch_dlc_true.pack(padx=5,pady=5,side='left')
        self.patch_dlc_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm6,text='Tickets only mode:').pack(padx=5,pady=5,side='left')
        self.tickets_only_true=ttk.Radiobutton(t3_frm6,text='On',variable=self.tickets_only,value=True)
        self.tickets_only_false=ttk.Radiobutton(t3_frm6,text='Off',variable=self.tickets_only,value=False)
        self.tickets_only_true.pack(padx=5,pady=5,side='left')
        self.tickets_only_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm7,text='Simulation mode:').pack(padx=5,pady=5,side='left')
        self.simulate_mode_true=ttk.Radiobutton(t3_frm7,text='On',variable=self.simulate_mode,value=True)
        self.simulate_mode_false=ttk.Radiobutton(t3_frm7,text='Off',variable=self.simulate_mode,value=False)
        self.simulate_mode_true.pack(padx=5,pady=5,side='left')
        self.simulate_mode_false.pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t3_frm8,text='Download ALL titles on NUS except system\ntitles. Choose the regions you would like:').pack(padx=5,pady=5,side='left')
        self.region_box_usa=ttk.Checkbutton(t3_frm8,text='USA',variable=self.region_usa).pack(padx=5,pady=5,side='left')
        self.region_box_eur=ttk.Checkbutton(t3_frm8,text='EUR',variable=self.region_eur).pack(padx=5,pady=5,side='left')
        self.region_box_jpn=ttk.Checkbutton(t3_frm8,text='JPN',variable=self.region_jpn).pack(padx=5,pady=5,side='left')
        btn=ttk.Button(t3_frm8,text='Go',width=4,command=lambda:self.download_clicked(3)).pack(pady=20,side='left')
                
        t3_frm1.grid(row=1,column=1,sticky='w')
        t3_frm2.grid(row=2,column=1,sticky='w')
        t3_frm3.grid(row=3,column=1,sticky='w')
        t3_frm4.grid(row=4,column=1,sticky='w')
        t3_frm5.grid(row=5,column=1,sticky='w')
        t3_frm6.grid(row=6,column=1,sticky='w')
        t3_frm7.grid(row=7,column=1,sticky='w')
        t3_frm8.grid(row=8,column=1,padx=10,pady=70,sticky='w')

        # Tab 4
        t4_frm0=ttk.Frame(tab4)
        t4_frm1=ttk.Frame(tab4)
        t4_frm2=ttk.Frame(tab4)
        t4_frm3=ttk.Frame(tab4)
        t4_frm4=ttk.Frame(tab4)
        t4_frm5=ttk.Frame(tab4)
        t4_frm6=ttk.Frame(tab4)
        t4_frm7=ttk.Frame(tab4)
        t4_frm8=ttk.Frame(tab4)
        t4_frm9=ttk.Frame(tab4)
        t4_frm10=ttk.Frame(tab4)
        t4_frm11=ttk.Frame(tab4)

        lbl=ttk.Label(t4_frm0,text='Version Information:\n\nSince the FunKii-UI GUI and FunKiiU are two seperate applications developed by different authors,\nswitching versions can break compatibility and shouldn\'t be done if you don\'t know what you are\ndoing. I will try to implement a compatibility list in a future release').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm1,text='GUI application:',font="Helvetica 13 bold").pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm2,text='Running version:\nTargeted for:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm2,text=__VERSION__+'\n'+targetversion).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm3,text='Latest release:').pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm3,text=self.versions['gui_new']).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm4,text='Update to latest release:').pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm4,text='Update',command=lambda:self.update_application('gui',self.versions['gui_new'])).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm5,text='Switch to different version:').pack(padx=5,pady=1,side='left')
        self.gui_switchv_box=ttk.Combobox(t4_frm5,width=7,values=[x for x in self.versions['gui_all']],state='readonly')
        self.gui_switchv_box.pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm5,text='Switch',command=lambda:self.update_application('gui',self.gui_switchv_box.get())).pack(padx=5,pady=1,side='left')        
        lbl=ttk.Label(t4_frm6,text='').pack(pady=15,side='left')
        lbl=ttk.Label(t4_frm7,text='FunKiiU core application:',font="Helvetica 13 bold").pack(padx=5,pady=5,side='left')
        lbl=ttk.Label(t4_frm8,text='running version:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm8,text=fnku.__VERSION__).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm9,text='latest release:').pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm9,text=self.versions['fnku_new']).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm10,text='Update to latest release:').pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm10,text='Update',command=lambda:self.update_application('fnku',self.versions['fnku_new'])).pack(padx=5,pady=1,side='left')
        lbl=ttk.Label(t4_frm11,text='Switch to different version:').pack(padx=5,pady=1,side='left')
        self.fnku_switchv_box=ttk.Combobox(t4_frm11,width=7,values=[x for x in self.versions['fnku_all']],state='readonly')
        self.fnku_switchv_box.pack(padx=5,pady=1,side='left')
        btn=ttk.Button(t4_frm11,text='Switch',command=lambda:self.update_application('fnku',self.fnku_switchv_box.get())).pack(padx=5,pady=1,side='left')
        
        t4_frm0.grid(row=0,column=1,padx=5,pady=5,sticky='w')
        t4_frm1.grid(row=1,column=1,padx=5,sticky='w')
        t4_frm2.grid(row=2,column=1,padx=25,sticky='w')
        t4_frm3.grid(row=3,column=1,padx=25,sticky='w')
        t4_frm4.grid(row=4,column=1,padx=25,sticky='w')
        t4_frm5.grid(row=5,column=1,padx=25,sticky='w')
        t4_frm6.grid(row=6,column=1,padx=5,sticky='w')
        t4_frm7.grid(row=7,column=1,padx=5,sticky='w')
        t4_frm8.grid(row=8,column=1,padx=25,sticky='w')
        t4_frm9.grid(row=9,column=1,padx=25,sticky='w')
        t4_frm10.grid(row=10,column=1,padx=25,sticky='w')
        t4_frm11.grid(row=11,column=1,padx=25,sticky='w')
        

        ## Build an sqlite database of all the data in the titlekeys json as well as size information
        ## for the title. Raw size in bytes as well as human readable size is recorded.
        ## The database that ships with the releases are minimal, containing ONLY size information.
        ## A full db build is mostly for redundancy and can be built by deleting the old data.db file,
        ## setting sizeonly=False, uncomment self.build_database() below and run the program.
        ## Be sure to re-comment out self.build_database() before running the program again.
        ## This will take a short while to fetch all the download size information.
        
        #self.build_database()

        if len(self.title_sizes) != len(self.title_data):
            print('\n\nSize informataion database is out of sync with titlekeys.json.')
            self.build_database()
            
    def build_database(self,sizeonly=True):
        print('\nUpdating size information database now.....\n')
        dataset=[]
        compare_ids=[]
        TK = fnku.TK
        
        if not os.path.isfile('data.db'):
            db=sqlite3.connect('data.db')
            cursor=db.cursor()
            cursor.execute(""" CREATE TABLE titles(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, title_id TEXT, title_key TEXT, name TEXT, region TEXT, content_type TEXT, size TEXT, ticket INT, raw_size INT) """)
        else:
            db=sqlite3.connect('data.db')
            cursor=db.cursor()
        cursor.execute("""SELECT title_id FROM titles""")
        
        for i in cursor:
            compare_ids.append(str(i[0]))
          
        for i in self.title_data:
            if not str(i[2]) in compare_ids:
                name=i[0]
                region=i[1]
                tid=i[2]
                tkey=i[3]
                cont=i[4]
                if tid in self.has_ticket:
                    tick=1
                else:
                    tick=0
                
                sz=0
                total_size=0
                    
                baseurl = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/{}'.format(tid)

                if not fnku.download_file(baseurl + '/tmd', 'title.tmd', 1):
                    print('ERROR: Could not download TMD...')
                else:
                    with open('title.tmd', 'rb') as f:
                        tmd = f.read()
                    content_count = int(binascii.hexlify(tmd[TK + 0x9E:TK + 0xA0]), 16)
    
                    total_size = 0
                    for i in range(content_count):
                        c_offs = 0xB04 + (0x30 * i)
                        c_id = binascii.hexlify(tmd[c_offs:c_offs + 0x04]).decode()
                        total_size += int(binascii.hexlify(tmd[c_offs + 0x08:c_offs + 0x10]), 16)
                    sz = fnku.bytes2human(total_size)
                    os.remove('title.tmd')
                
                dataset.append((tid,tkey,name,region,cont,sz,total_size,tick))
        if len(dataset) > 0:   
            for i in dataset:
                tid=i[0]
                tkey=i[1]
                name=i[2]
                region=i[3]
                cont=i[4]
                sz=i[5]
                raw=i[6]
                tick=i[7]
                if sizeonly:
                    cursor.execute("""INSERT INTO titles (title_id, size, raw_size) VALUES (?, ?, ?)""", (tid,sz,raw))
                else:
                    cursor.execute("""INSERT INTO titles (title_id, title_key, name, region, content_type, size, ticket, raw_size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (tid,tkey,name,region,cont,sz,tick,raw))
        db.commit()
        db.close()
        print('done bulding database. Restart for changes to take effect.')
        
    def load_title_sizes(self):
        if os.path.isfile('data.db'):
            db = sqlite3.connect('data.db')
            cursor = db.cursor()
            cursor.execute("""SELECT title_id, size, raw_size FROM titles""")
            for i in cursor:
                    self.title_sizes[str(i[0])] = str(i[1])
                    self.title_sizes_raw[str(i[0])] = str(i[2])
            db.close()
        else:
            print('No data.db file found. No size information will be available')

    def id_changed(self,*args):
        self.key_box.delete('0',tk.END)
        t_id=self.id_box.get()
        if len(t_id) == 16:
            try:
                self.selection_box.set(self.title_dict[t_id].get('longname',''))                
                if t_id in self.has_ticket:
                    self.has_ticket_lbl.configure(text='YES',foreground='green')
                else:
                    self.has_ticket_lbl.configure(text='NO',foreground='red')                
                if self.title_dict[t_id].get('key',None):
                    self.key_box.insert('end',self.title_dict[t_id]['key'])
                if self.title_sizes[t_id] != '0':
                    self.dl_size_lbl.configure(text='Size: '+self.title_sizes[t_id]+',')
                else:
                    self.dl_size_lbl.configure(text='Size: ?,')
                    
            except Exception as e:
                #print(e)
                self.selection_box.set('')
                self.dl_size_lbl.configure(text='Size: ?,')
        
        else:
            #self.selection_box.set('')
            if self.dl_size_lbl.cget('text') != 'Size:,':
                self.dl_size_lbl.configure(text='Size:,')
            if self.has_ticket_lbl.cget('text') != '':
                self.has_ticket_lbl.configure(text='')


    def update_keysite_widgets(self):
        txt='Correct keysite is already loaded'
        self.enterkeysite_lbl.configure(text=txt,background='black',foreground='green',font="Helvetica 13 bold")
        self.http_lbl.pack_forget()
        self.keysite_box.pack_forget()
        self.submitkeysite_btn.pack_forget()
        
    def check_config_keysite(self):
        try:
            with open('config.json') as cfg:
                config=json.load(cfg)                
                site=config['keysite']
                if fnku.hashlib.md5(site.encode('utf-8')).hexdigest() == fnku.KEYSITE_MD5:
                    self.update_keysite_widgets()
                    
        except IOError:
            pass
        
    def notify_of_update(self,update=True):
        txt='Updates are available in the updates tab'
        fg='red'
        if not update:
            txt='No updates are currently available'
            fg='green'
        self.updatelabel.configure(text=txt,background='black',foreground=fg,font="Helvetica 13 bold")
        
    def update_application(self,app,zip_file):
        if app == 'fnku':
            self.download_zip(self.versions['fnku_url'].split('releases')[0]+'archive'+'/v'+zip_file+'.zip')
        else:
            self.download_zip(self.versions['gui_url'].split('releases')[0]+'archive'+'/v'+zip_file+'.zip')
            
        if self.unpack_zip('update.zip'):
            print('Update completed succesfully! Restart application\nfor changes to take effect.')
            os.remove('update.zip')
            
    def unpack_zip(self,zip_name):
        try:
            print('unzipping update')
            cwd=os.getcwd()
            dest=cwd+dir_slash+zip_name
            zfile=zipfile.ZipFile(dest,'r')
            for i in zfile.namelist():
                data=zfile.read(i,None)
                x=i.split("/")[1]
                if x!='':
                    with open(x,'wb') as p_file:
                        p_file.write(data)                      
            zfile.close()           
            return True
        
        except Exception as e:
            print('Error:',e)
            return False
        
    def download_zip(self,url):
        try:
            z = urlopen(url)
            print('Downloading ', url)      
            with open('update.zip', "wb") as f:
                f.write(z.read())
            print('\nDone.')
            
        except HTTPError as e:
            print("Error:", e.code, url)
        except URLError as e:
            print ("Error:", e.reason, url)
                   
    def populate_selection_box(self,download_data=True):
        if download_data:
            keysite = fnku.get_keysite()
            print(u'Downloading/updating data from {0}'.format(keysite))

            if not fnku.download_file('https://{0}/json'.format(keysite), 'titlekeys.json', 3):
                print('ERROR: Could not download data file...\n')
            else:
                print('DONE....Downloaded titlekeys.json succesfully')
        try:
            self.clear_id_key_boxes()
            self.selection_list=[]    
            self.load_title_data()
            
            if self.filter_usa.get():
                if self.filter_game.get():
                    for i in self.usa_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.usa_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)   
                if self.filter_update.get():
                    for i in self.usa_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                    
            if self.filter_eur.get():
                if self.filter_game.get():
                    for i in self.eur_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.eur_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)       
                if self.filter_update.get():
                    for i in self.eur_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                        
            if self.filter_jpn.get():
                if self.filter_game.get():
                    for i in self.jpn_selections['game']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_dlc.get():
                    for i in self.jpn_selections['dlc']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                if self.filter_update.get():
                    for i in self.jpn_selections['update']:
                        if self.filter_hasticket.get():
                            if self.reverse_title_names.get(i) in self.has_ticket:
                                self.selection_list.append(i)
                        else:
                            self.selection_list.append(i)
                            
            self.selection_list.sort()
            self.selection_box.set('')
            self.selection_box.configure(values=(self.selection_list))
            self.selection_box.set_completion_list(self.selection_list)
            print('Succesfully populated the selection box..')
        except Exception as e:
            print('Something happened while trying to populate the selection box...')
            print('ERROR:' ,e)

    def clear_id_key_boxes(self,*args):
        self.id_box.delete('0',tk.END)
        self.key_box.delete('0',tk.END)
        
    def selection_box_changed(self,*args):
        user_selected_raw=self.selection_box.get()
        self.clear_id_key_boxes()
        titleid = self.reverse_title_names[user_selected_raw]
        self.id_box.insert('end',titleid)                
    
    def load_title_data(self):       
        self.title_data=[]
        try:
            with open('titlekeys.json') as td:
                title_data=json.load(td)
            self.errors=0
            print('Now parsing titlekeys.json')
            for i in title_data:
                try:
                    if i['name']:
                        titleid=i['titleID']
                        name=i['name']
                        name=name.lower().capitalize().strip()
                        titlekey=i['titleKey']
                        region=i['region']
                        tick=i['ticket']
                        if titleid[4:8] == '0000':
                            content_type='GAME'
                        elif titleid[4:8] == '000c':
                            content_type='DLC'
                        elif titleid[4:8] == '000e':
                            content_type='UPDATE'
                        if tick == '1':
                            self.has_ticket.append(titleid)
                        
                        longname=name+'  --'+region+'  -'+content_type
                        entry=(name,region,titleid,titlekey,content_type,longname)
                        entry2=(longname)
                        self.reverse_title_names[longname]=titleid 
                        self.title_dict[titleid]={'name':name, 'region':region, 'key':titlekey, 'type':content_type, 'longname':longname, 'ticket':tick}
                        
                        if not entry in self.title_data:
                            self.title_data.append(entry)
                            if region == 'USA':
                                if content_type == 'GAME':
                                    if not entry2 in self.usa_selections['game']:
                                        self.usa_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.usa_selections['dlc']:
                                        self.usa_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.usa_selections['update']:
                                        self.usa_selections['update'].append(entry2)
                            elif region == 'EUR':
                                if content_type == 'GAME':
                                    if not entry2 in self.eur_selections['game']:
                                        self.eur_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.eur_selections['dlc']:
                                        self.eur_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.eur_selections['update']:
                                        self.eur_selections['update'].append(entry2)
                            elif region == 'JPN':
                                if content_type == 'GAME':
                                    if not entry2 in self.jpn_selections['game']:
                                        self.jpn_selections['game'].append(entry2)
                                elif content_type == 'DLC':
                                    if not entry2 in self.jpn_selections['dlc']:
                                        self.jpn_selections['dlc'].append(entry2)
                                elif content_type == 'UPDATE':
                                    if not entry2 in self.jpn_selections['update']:
                                        self.jpn_selections['update'].append(entry2)                
                except Exception as e:
                    if DEBUG:
                        print('Error on title: ' + titleid)
                        print('ERROR LOADING ',e)
                        self.errors+=1
        except IOError:
            print('No titlekeys.json file was found. The selection box will be empty')
        if DEBUG: print(str(self.errors)+' Titles did not load correctly.')
         
    def sanity_check_input(self,val,chktype):
        try:
            if chktype == 'title':
                if len(val) == 16:
                    val=int(val,16)
                    return True
            elif chktype =='key':
                if len(val) == 32:
                    val=int(val,16)
                    return True
            else:
                return False
        except ValueError:
            return False
        
    def add_to_list(self):
        titleid = self.id_box.get().strip()
        if len(titleid) == 16:
            key=None        
            name = self.title_dict[titleid].get('longname',titleid)
            name='  '+name
            if self.sanity_check_input(titleid,'title'):
                pass
            else:
                print('Bad Title ID. Must be a 16 digit hexadecimal.')
                return
            key=self.title_dict[titleid].get('key',self.key_box.get().strip())
            if key == '':
                key=None
            if not key or self.sanity_check_input(key,'key'):
                pass
            else:
                print('Bad Key. Must be a 32 digit hexadecimal.')
                return
            if key: name=' *'+name
            size=int(self.title_sizes_raw.get(titleid,0))
            if size == 0:
                name =' !'+name
            entry=(name,titleid,key,size)
            if not entry in self.download_list:
                self.download_list.append(entry)
            self.populate_dl_listbox()
        else:
            print('There is no title id entered')

    def remove_from_list(self):
        try:
            index=self.dl_listbox.curselection()
            item=self.dl_listbox.get('anchor')
            for i in self.download_list:
                if i[0] == item:
                    self.download_list.remove(i)
            self.populate_dl_listbox()
        except IndexError as e:
            print('Download list is already empty')
            print(e)

    def clear_list(self):
        self.download_list=[]
        self.populate_dl_listbox()
        
    def populate_dl_listbox(self):
        total_size=[]
        trigger_warning=False
        self.dl_listbox.delete('0',tk.END)
        for i in self.download_list:
            name=i[0]
            if i[3] == 0:
                if not trigger_warning:
                    trigger_warning=True
            self.dl_listbox.insert('end',name)
            total_size.append(int(i[3]))
        total_size=sum(total_size)
        total_size=fnku.bytes2human(total_size)
        self.total_dl_size.set('Total size: '+total_size)
        if trigger_warning:
            self.total_dl_size_warning.set(self.dl_warning_msg)
        else:
            self.total_dl_size_warning.set('')
        return

    def submit_key_site(self):
        site=self.keysite_box.get().strip()
        if fnku.hashlib.md5(site.encode('utf-8')).hexdigest() == fnku.KEYSITE_MD5:
            print('Correct key site, now saving...')
            config=fnku.load_config()
            config['keysite'] = site
            fnku.save_config(config)
            print('done saving, you are good to go!')
            self.update_keysite_widgets()
            self.nb.select(self.tab2)
        else:
            print('Wrong key site provided. Try again')

    def get_output_directory(self):
        out_dir=filedialog.askdirectory()
        self.out_dir_box.delete('0',tk.END)
        self.out_dir_box.insert('end',out_dir)

    def load_program_revisions(self):
        print('Checking for program updates, this might take a few seconds.......\n')
        url1=self.versions['fnku_url']
        url2=self.versions['gui_url']    
        response = urlopen(url1)
        rslts=response.read()
        rslts=str(rslts)
        x=''
        for i in rslts:
            x=x+i
        parser = VersionParser()
        parser.feed(x)
        response = urlopen(url2)
        rslts=response.read()
        rslts=str(rslts)
        x=''
        for i in rslts:
            x=x+i
        parser = VersionParser()
        parser.feed(x)

        fnku_data_set = parser.fnku_data_set
        gui_data_set = parser.gui_data_set
        
        fnku_all=[]
        fnku_newest=''
        gui_all=[]
        gui_newest=''
        
        for i in fnku_data_set:
            ver=LooseVersion(i.split('/')[4][1:-4])
            fnku_all.append(str(ver))
        fnku_newest=max(fnku_all)
        
        for i in gui_data_set:
            ver=LooseVersion(i.split('/')[4][1:-4])
            if ver > LooseVersion('2.0.5'):
                gui_all.append(ver)
                
        gui_newest=max(gui_all)
        if gui_newest > current_gui or fnku_newest > current_fnku:
            self.notify_of_update()
        else:
            self.notify_of_update(update=False)
            

        self.versions['fnku_all']=fnku_all
        self.versions['fnku_new']=fnku_newest
        self.versions['gui_all']=[str(i) for i in gui_all]
        self.versions['gui_new']=str(gui_newest)
        
    def download_clicked(self,dl_method):
        title_list=[]
        key_list=[]
        out_dir=self.output_dir.get().strip()
        if len(out_dir)==0:
            out_dir=None
        rtry_count=self.retry_count.get()
        ptch_demo=self.patch_demo.get()
        ptch_dlc=self.patch_dlc.get()
        tick_only=self.tickets_only.get()
        sim=self.simulate_mode.get()
        for i in self.download_list:
            title_list.append(i[1])
            key_list.append(i[2])
            
        if dl_method == 1:
            for i in title_list:
                if not i in self.has_ticket:
                    print('You chose online ticket method but have items in the download list that do not have\nan online ticket.')
                    return
            for i in self.download_list[:]:
                t=i[1]
                k=None
                n=self.title_dict[t].get('name', '').strip()
                n=n+'_'+self.title_dict[t].get('type','').strip()
                r=self.title_dict[t].get('region','').strip()
                
                fnku.process_title_id(t, k, name=n, region=r, output_dir=out_dir, retry_count=rtry_count, onlinetickets=True, patch_demo=ptch_demo,
                                      patch_dlc=ptch_demo, simulate=sim, tickets_only=tick_only)
               
                self.download_list.remove(i)
                self.populate_dl_listbox()
                root.update()

        elif dl_method == 2:
            for i in key_list:
                if not i:
                    print('You chose a key method without providing a key for one or more titles')
                    return
                
            for i in self.download_list[:]:
                t=i[1]
                k=i[2]
                n=self.title_dict[t].get('name', '').strip()
                n=n+'_'+self.title_dict[t].get('type','').strip()
                r=self.title_dict[t].get('region','').strip()
                
                fnku.process_title_id(t, k, name=n, region=r, output_dir=out_dir, retry_count=rtry_count, patch_demo=ptch_demo,
                                      patch_dlc=ptch_demo, simulate=sim, tickets_only=tick_only)
               
                self.download_list.remove(i)
                self.populate_dl_listbox()
                root.update()
                
                    
        # I need to add bulk selection to the download list instead of using the -regions option of FunKiiU
        # There is also no default behavior, ie: Download legit tickets if they exist and create a fake
        # ticket if not, or ignore titles without online ticket etc.. I need to give behavior options 
        elif dl_method == 3:
            regions=[]
            if self.region_usa.get():
                regions.append('USA')
            if self.region_eur.get():
                regions.append('EUR')
            if self.region_jpn.get():
                regions.append('JPN')
            if len(regions)>0:
                fnku.main(download_regions=regions,output_dir=output_dir,retry_count=retry_count,
                          patch_demo=patch_demo,patch_dlc=patch_dlc,tickets_only=tickets_only,simulate=simulate,download=False)
            else:
                print('No regions selected. Try again.')
            
                
    
        
if __name__ == '__main__':
    root=RootWindow()
    root.title('FunKii-UI')
    root.resizable(width=False,height=False)
    root.mainloop()
