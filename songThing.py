# Song Class
from tkinter import Tk, Label, Frame, Button, Canvas, filedialog,Entry
from tkinter.simpledialog import askstring
from json import dumps, load 
from os import path

class Song:
    def __init__(self,*,artist="",name="",comment="",):
        self.name = name
        self.comment = comment
        self.artist = artist
    def get(self):
        return [self.artist,self.name,self.comment]
    def matches(self,song):
        return song.artist==self.artist and song.name==self.name
    def getJSON(self):
        return {"name":self.name,"artist":self.artist,"comment":self.comment}
    def change(self,*,artist="",name="",comment=""):
        if artist:
            self.artist = artist
        if name:
            self.name = name
        if comment:
            self.comment = comment
    

# All keys inside save.json will be lowercase!
# at least i hope

# Frontend
class Song_UI():
    def __init__(self,root,parent,song=Song(),*,column=-1,row=-1):
        self.song = song
        self.pos = len(root.grid_slaves())
        self.parent = parent
        
        # Title
        title = Label(root,text=song.name)
        title.grid(column = 0,row = self.pos,sticky="w")
        self.title = title
        
        # Artist
        artist = Label(root,text=f"by {song.artist}")
        artist.grid(column=1,row=self.pos)
        self.artist = artist
        self.song = song
        
        # Remove Button
        removeButton = Button(root,text="X",command=self.remove)
        removeButton.grid(column=1,row=self.pos,sticky="e")
        
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
        self.songlist = []
        split = geometry.split("x")
        # Column is x, Row is y...

        # Window
        root = Tk()
        root.configure(background=root_bg)
        root.title(title)
        self.root = root
        
        # Lambda functions that make it faster, and more easily editable
        new_entry = lambda: Entry(sideFrame,foreground="white")
        new_label = lambda x: Label(sideFrame, text=x)
        newButton = lambda cmd,text: Button(sideFrame,command=cmd,text=text)

        # Frame thing
        frame = Frame(root)
        frame.configure(background=frame_bg,height=split[0],width=split[1])
        frame.grid(column=0,row=0)
        self.frame = frame
        # Side Frame
        sideFrame = Frame(root)
        sideFrame.configure(background=frame_bg,height=100,width=300)
        sideFrame.grid(column=1,row=0,sticky="n")
        
        # Box Display for stuffs
        display = Canvas(frame,background=txt_bg,borderwidth=2,width=300,height=300)
        display.grid(row=1,column=0,sticky="n")
        self.display = display
        
        span = display.grid_info().get("rowspan")+1
        
        # song input label
        display_label = Label(display,text="favorite songs",state="normal",background="grey")
        display_label.configure(width=50,height=1,anchor="n")
        display_label.grid(row=0,column=1,sticky="n")
        display_label.columnconfigure(1,weight=20)
        self.display_label = display_label
        
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
        saveInputLabel = new_label("Comment: ")
        saveInputLabel.grid(column=0,row=span+2)
        saveInputLabel.columnconfigure(1,weight=12,minsize=12)
        self.saveInputLabel = saveInputLabel
        self.inputs = [saveInputBox,inputBox,artistInputBox]
        
        
        # clear ALL songs button
        clear_button = newButton(self.clearAllSongs,"clear")
        clear_button.grid(column=3,row=span)
        self.clear_button = clear_button
        
        # Save slot Button
        save_button = newButton(self.save,"Save")
        save_button.grid(column=3,row=span+1,sticky="nesw")
        self.save_button = save_button
        
        # The Add Song Button
        button = newButton(self.add,"add")
        button.grid(column=4,row=span,sticky="nesw")
        self.button = button
        
        # Load slot Button
        load_button = newButton(self.load,"Load")
        load_button.grid(column=4,row=span+1,sticky="nesw")
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
        name = askstring("Please input a Name.","Save File Name: ",initialvalue="SDA_save")
        fileDirectory = path.join(path.expanduser('~'),'Documents',name)
        with open(f"{fileDirectory}.json","w+") as file:
            save = []
            for i in self.songlist:
                get = i.getJSON()
                save.append(get)
                # print(f"{type(get)}\n{get}\n\n") # Debug
            file.write(dumps(save))

    # Load a JSON File, also update it if it's an old JSON.
    def load(self):
        print("\n\n\nLOADING FILE\n\n\n")
        loadFile = filedialog.askopenfile(mode="r+",filetypes=[('JSON File', '*.json')])
        if loadFile:
            self.clearAllSongs()
            for i in load(loadFile):
                if i.get('singer'): # For older versions
                    i["comment"] = i.get('singer')
                self.add(name=i.get('name'),artist=i.get('artist'),comment=i.get("comment"))
    # Add a new song to the display
    def add(self,*args,artist=None,name=None,comment=None):
        print(f"new song \nArtist:{artist}\nName:{name}\nComment:{comment}")
        span = self.display.grid_info().get("rowspan")+1
        newSong = Song()
        if comment:
            newSong.singer = comment
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