# Song Class
from time import sleep
import tkinter as tk
from tkinter import filedialog
import json 
from youtube_search import YoutubeSearch # pip install youtube-search!

# global variables key

class Song:
    def __init__(self,*,artist="",name="",singer="",):
        self.name = name
        self.singer = singer
        self.artist = artist
    def get(self):
        return [self.artist,self.name,self.singer]
    def matches(self,song):
        return song.artist==self.artist and song.name==self.name
    def getJSON(self):
        return {"name":self.name,"artist":self.artist,"singer":self.singer}
    def change(self,*,artist="",name="",singer=""):
        if artist:
            self.artist = artist
        if name:
            self.name = name
        if singer:
            self.singer = singer

class AppFunctions():
    # Google, help me out here to get this...
    def get_youtube_results(self,url,results=1): 
        results = YoutubeSearch(url,results)
        print(results)
        return results
    

# All keys inside save.json will be lowercase!
# at least i hope

# Frontend
class Song_UI():
    def __init__(self,root,parent,song=Song(),*,column=-1,row=-1):
        self.song = song
        pos = len(root.grid_slaves())
        self.pos = pos
        self.parent = parent
        
        # Title
        title = tk.Label(root,text=song.name)
        title.grid(column = 0,row = pos,sticky="w")
        self.title = title
        
        # Artist
        artist = tk.Label(root,text=f"by {song.artist}")
        artist.grid(column=1,row=pos)
        self.artist = artist
        self.song = song
        
        # Remove Button
        removeButton = tk.Button(root,text="X",command=self.remove)
        removeButton.grid(column=1,row=pos,sticky="e")
        
        
        
        self.self = [removeButton,title,artist]
    
    # Remove this song
    def remove(self):
        for i in self.self:
            i.destroy()
        print(len(self.parent.songlist))
        print(len(self.parent.song_UI_list))
        for i in self.parent.songlist:
            if i.matches(self.song):
                self.parent.songlist.remove(i)
                self.parent.song_UI_list.remove(self)
                break
        print(len(self.parent.songlist))
        print(len(self.parent.song_UI_list))
        
class App():
    def __init__(self,*,
                 title="Favorite Song Playlist Thing",
                 geometry="600x350",
                 root_bg="Black",
                 frame_bg="WHITE",
                 txt_bg="Grey",
                 ):
        self.functions = AppFunctions()
        self.songlist = []
        split = geometry.split("x")
        # Column is x, Row is y...

        # Window
        root = tk.Tk()
        root.configure(background=root_bg)
        root.title(title)
        self.root = root
        
        # scroll
        tk.Scrollbar(root)
        
        
        
        # Frame thing
        frame = tk.Frame(root)
        frame.configure(background=frame_bg,height=split[0],width=split[1])
        frame.grid(column=0,row=0,columnspan=3,rowspan=3)
        self.frame = frame

        # the Bottom that stays at the bottom
        bottom = tk.Frame(root)
        bottom.grid(column=1,row=0)
        
        # Box Display for stuffs
        display = tk.Canvas(frame,background=txt_bg,borderwidth=2,width=30,height=180)
        display.grid(row=0,column=0,columnspan=5,rowspan=15)
        display.columnconfigure(0,weight=40)
        self.display = display
        
        span = display.grid_info().get("rowspan")+1

        # song input label
        display_label = tk.Label(display,text="favorite songs",state="normal",background="grey")
        display_label.configure(width=50,height=1,anchor="center")
        display_label.grid(row=0,column=1,sticky="n")
        display_label.columnconfigure(1,weight=20)
        self.display_label = display_label

        # faster and convenient
        new_entry = lambda: tk.Entry(frame,foreground="white")
        
        # Input Box For Song Title
        inputBox = new_entry()
        inputBox.grid(column=1,row=span,sticky="w")
        inputBox.columnconfigure(2,weight=12)
        self.inputBox = inputBox
        
        # Input box for artist
        artistInputBox = new_entry()
        artistInputBox.grid(column=1,row=span+1,sticky="w")
        artistInputBox.columnconfigure(2,weight=12)
        self.artistInputBox = artistInputBox
        
        # Input Box for URL
        saveInputBox = new_entry()
        saveInputBox.grid(column=1,row=span+2,sticky="w")
        self.saveInputBox = saveInputBox
        
        new_label = lambda x: tk.Label(frame, text=x)
        # Label for song title input
        inputBoxLabel = new_label("Song Title: ")
        inputBoxLabel.grid(column=0,row=span)
        inputBoxLabel.columnconfigure(1,weight=12)
        self.inputBoxLabel = inputBoxLabel
        
        # Label for song Artist input
        songInputLabel = new_label("Artist: ")
        songInputLabel.grid(column=0,row=span+1)
        songInputLabel.columnconfigure(1,weight=12)
        self.songInputLabel = songInputLabel
        
        # Label for URL input
        saveInputLabel = new_label("Save Name: ")
        saveInputLabel.grid(column=0,row=span+2)
        saveInputLabel.columnconfigure(1,weight=12,minsize=12)
        self.saveInputLabel = saveInputLabel
        self.inputs = [saveInputBox,inputBox,artistInputBox]
        
        # The Add Song Button
        button = tk.Button(frame,command=self.add,text="add")
        button.grid(column=4,row=span,sticky="e")
        self.button = button
        
        # clear ALL songs button
        clear_button = tk.Button(frame, command=self.clearAllSongs,text="clear")
        clear_button.grid(column=3,row=span)
        self.clear_button = clear_button
        
        # Save slot Button
        save_button = tk.Button(frame, command=self.save,text="Save")
        save_button.grid(column=3,row=span+2,sticky="nesw")
        self.save_button = save_button
        
        # Load slot Button
        load_button = tk.Button(frame, command=self.load,text="Load")
        load_button.grid(column=4,row=span+2,sticky="nesw")
        self.load_button = load_button
        
        self.song_UI_list = []
        
    def clearOthers(self):
        self.inputs[1].delete("0","end")
        self.inputs[2].delete("0","end")
        
    # Clear all inputs
    def clear(self):
        for i in self.inputs:
            i.delete("0","end")
        
    # Clear entire song playlist
    def clearAllSongs(self):
        self.clear()
        print(len(self.song_UI_list))
        for i in self.song_UI_list:
            for item in i.self:
                item.destroy()
        self.song_UI_list = []
        self.songlist = []
        
    def save(self):
        x = self.saveInputBox.get()
        if not x:
            x = "SDA_save"
        with open(f"{x}.json","w+") as file:
            save = []
            for i in self.songlist:
                get = i.getJSON()
                save.append(get)
                # print(f"{type(get)}\n{get}\n\n") # Debug
            file.write(json.dumps(save))

    def load(self):
        print("\n\n\nLOADING FILE\n\n\n")
        loadFile = filedialog.askopenfile(mode="r+",filetypes=[('JSON File', '*.json')])
        if loadFile:
            self.clearAllSongs()
            for i in json.load(loadFile):
                self.add(name=i['name'],artist=i['artist'],singer=i['singer'])
        
    # Add a new song to the display
    def add(self,*args,artist=None,name=None,singer=None):
        print(f"new song \nArtist:{artist}\nName:{name}\nSinger:{singer}")
        span = self.display.grid_info().get("rowspan")+1
        newSong = Song()
        if singer:
            newSong.singer = singer
        if not(artist or name):
            newSong.change(artist=self.artistInputBox.get(),name=self.inputBox.get())
            self.song_UI_list.append(Song_UI(self.display,self,song=newSong,column=span,row=0))
            self.songlist.append(newSong)
            self.clear()
        else:
            newSong.change(artist=artist,name=name)
            self.song_UI_list.append(Song_UI(self.display,self,song=newSong,column=span,row=0))
            self.songlist.append(newSong)
    
    def mainloop(self):
        self.root.mainloop()
App().mainloop()