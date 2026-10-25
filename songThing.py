# Song Class
from tkinter import Tk, Label, Frame, Button, Canvas, filedialog, Entry
from tkinter.simpledialog import askstring
from tkinter.colorchooser import askcolor
from abc import ABC, abstractmethod
from json import dumps, load 
from os import path

# Sound effects

# Backend Classes
# Class For storing songs
class Song:
    
    
    def __init__(self,*,artist="",name="",comment="",):
        self.name = name
        self.comment = comment
        self.artist = artist
    
    # Access the keys of the song using indexes, meant to be paired with get().
    def getKeys(self):
        return ["name","artist","comment"]
    
    # Access the values of the song.
    def get(self): 
        return [self.name,self.artist,self.comment]
    
    # Access the song as a dictionary, meant to be returned to the JSON package.
    def getJSON(self): 
        return {"name":self.name,"artist":self.artist,"comment":self.comment}
    
    # Check if this Song object matches another Song object. do not check comments.
    def matches(self,song):
        return song.artist.lower()==self.artist.lower() and song.name.lower()==self.name.lower()
    
    # Change an aspect of this object. more easy to work with that directly modifying the values yourself.
    def change(self,*,artist="",name="",comment="",TYPE=0,passed=""):
        if artist:
            self.artist = artist
        if name:
            self.name = name
        if comment:
            self.comment = comment
        if TYPE:
            if TYPE==1:
                self.name = passed
            elif TYPE==2:
                self.artist = passed
            elif TYPE==3:
                self.comment = passed
            else:
                print(f"{self.name} UI: Huh?")

# Class for storing undo/redos
class Action:
    def __init__(self):
        pass
        
    
# Frontend Classes

# Parent Superclass for basically all the other Classes.
class BaseWidgetExtension(ABC):
    # Constructor
    def __init__(self,root,parent):
        self.root = root
        self.parent = parent
    
    # Update a widget, and it's children, colors (taken from ColorSetting but dont tell them that I got lazy)
    def updateChildrenColors(self,parent,color):
        parent.configure(background=color)
        parent.configure(highlightbackground=color)
        for i in parent.grid_slaves():
            i.configure(highlightbackground=color)
            i.configure(background=color)
    
    # Method to remove the widget, made abstract so widgets have some flexibility with it.
    @abstractmethod
    def remove(self):
        pass

class ColorSetting(BaseWidgetExtension):
    # Constructor
    def __init__(self,parent,name,*,modify=[],TYPE=0):
        # Superclass constructor
        super().__init__(parent.parent.display,parent)
        
        # Type of Color Settings.
        # Type 0 Color Settings Will update all descendants aswell, 
        # Any other type will only update this specific modify element.
        # Meant to be used for updateColors.
        self.type = TYPE 
        
        # The widget(s) to modify.
        self.modify=modify 
        
        # Lambda for convenience
        new_text_label = lambda x: Label(frame, text=x)
        new_button = lambda cmd: Button(frame,command=cmd)
        new_text_button = lambda cmd,x: Button(frame,command=cmd,text=x,state="active")
        
        # Frame holding the Colorsetting's Widgets
        frame = Frame(parent.frame)
        frame.grid(row=len(parent.frame.grid_slaves()))
        self.frame = frame
        
        # Labeling the name of the Color Setting.
        label = new_text_label(name)
        label.grid(row=0,column=0,sticky="n")
        self.label = label

        # Button that opens to a color picker.
        color_picker = new_button(self.getUserColor)
        color_picker.grid(row=1,column=0,sticky="w")
        self.color_picker = color_picker
        
        # Button that applies colors to the widgets to modify
        apply_button = new_text_button(self.applyCurrentColor,"Apply\nColor")
        apply_button.grid(row=1,column=1,sticky="e")
        self.apply_button = apply_button
        
    # applyColor makes sure that there actually is a color to modify before modifying the widget.
    def applyColor(self,color):
        if color:
            try:
                self.updateColors(self.modify,color)
            except Exception as x:
                print(f"got exception:\n{x}")
        else:
            print("didnt put in a color!")

    # Use the user input (from self.color_picker) and color given that.
    def applyCurrentColor(self):
        try:
            self.applyColor(self.color)
        except AttributeError:
            print("No picked color!")

    # Process if the "frame" is a list to judge how to color the widget and it's descendents.
    def updateColors(self,frame,color):
        if type(frame)==list:
            for i in frame:
                for v in i.frame:
                    v.configure(highlightbackground=color)
                    v.configure(background=color)
        else:
            frame.configure(background=color)
            if self.type==0:
                for i in frame.grid_slaves():
                    i.configure(highlightbackground=color)
                    i.configure(background=color)
                    try:
                        super().updateChildrenColors(i,color)
                    except Exception:
                        pass
        
    # Ask for a color using the askcolor() prompt.
    def getUserColor(self):
        color = list(askcolor())[1]
        super().updateChildrenColors(self.frame,color)
        self.color = color
        print(self.color)
        return self.color
    
    # Removal (Abstract method)
    def remove(self):
        self.frame.destroy()
        

class Settings(BaseWidgetExtension):
    # Constructor
    def __init__(self,root,parent):
        # Superclass Constructor
        BaseWidgetExtension.__init__(BaseWidgetExtension,root,parent)
        # Settings Button
        button = Button(parent.display,command=self.update,text="S")
        button.grid(row=0,column=1,sticky="w")
        self.button = button
        
        # Framework
        frame = Frame(root,padx=25)
        frame.grid(column=0,row=0,sticky="n")
        frame.grid_remove()
        self.frame = frame
        self.shown = False
        
        # The Settings
        sideColor = ColorSetting(self,"Sideframe Color",modify=parent.sideframe)
        settingsColor = ColorSetting(self,"Settings Color",modify=self.frame,TYPE=1)
        backgroundColor = ColorSetting(self,"Background Color",modify=parent.root,TYPE=1)
        displayColor = ColorSetting(self,"Display Color",modify=parent.display)

        
    
    # Hide/Show Settings Side Tab
    def update(self):
        if self.shown:
            print("Hid Settings")
            self.frame.grid_remove()
            self.shown = False
        else:
            print("Showed Settings")
            self.frame.grid()
            self.shown = True
    
    # Remove the widget (Abstract method)
    def remove(self):
        self.frame.destroy()
        self.button.destroy()
        
        
class Song_UI(BaseWidgetExtension):
    
    # Constructor
    def __init__(self,root,parent,song=Song(),*,column=-1,row=-1):
        # Superclass Constructor
        BaseWidgetExtension.__init__(BaseWidgetExtension,root,parent)
        
        
        self.song = song
        self.pos = len(self.root.grid_slaves())
        self.parent = self.parent
        
        frame = Canvas(self.root,width=50)
        frame.grid(column=2,row=(self.pos+1),sticky="nesw")
        self.frame = frame
        # Title
        title = Label(frame,text=song.name)
        title.grid(column = 0,row = 0,sticky="w")
        self.title = title
        
        # Artist
        artist = Label(frame,text=f"by {song.artist}")
        artist.grid(column=3,row=0)
        self.artist = artist
        self.song = song
        
        # info Button
        infoButton = Button(frame,text="i",command=self.comment)
        infoButton.grid(column=4,row=0,sticky="e")
        self.infoButton = infoButton
        
        # Remove Button
        removeButton = Button(parent.display,text="X",command=self.remove)
        removeButton.grid(column=3,row=(self.pos+1),sticky="nesw")
        self.removeButton = removeButton
        
        # Configure Button
        configButton = Button(parent.display,text="S",command=self.configure)
        configButton.grid(column=4,row=(self.pos+1),sticky="nesw")
        self.configButton = configButton

            
    # Prompt
    def configure(self):
        prompt = "Enter 1 for Name Configuration\nEnter 2 for Artist Configuration\nEnter 3 for comment configuration\nEnter 4 for Special Color Configuration"
        x = int(askstring(title = "CONFIGURATION", prompt=prompt))
        if x>0 and x<4:
            y = askstring(title = "CONFIGURATION", prompt=f"modifying:{self.song.getKeys()[x-1]} \noriginal text:{self.song.get()[x-1]} \nenter the string: ")
            self.song.change(TYPE=x,passed=y)
            self.updateInfo()
        if x==4:
            y = askcolor()
            self.updateColor(y,type=1)
            
    # Show the song's comment
    def comment(self):
        newScreen = Tk()
        newScreen.title(f"{self.song.name} by {self.song.artist}")
        frame = Canvas(newScreen)
        frame.pack()
        label = Label(frame,text=f"Comment:\n {self.song.comment}",width=10,height=5)   
        label.pack()
        
    def updateInfo(self):
        self.artist.configure(text=f"by {self.song.artist}")
        self.title.configure(text=self.song.name)
    
    def updateColor(self,color,*,type=0):
        def update():
            self.frame.configure(background=color)
            for i in self.frame.grid_slaves():
                i.configure(background=color)
                i.configure(highlightbackground=color)
        if type==0:
            if not self.specialColor:
                update()
        elif type==1:
            update()
            
    
    # Remove this and it's index
    def remove(self):
        self.frame.destroy()
        self.removeButton.destroy()
        self.configButton.destroy()
        for i in range(len(self.parent.song_UI_list)):
            if self.pos==self.parent.song_UI_list[i].pos:
                self.parent.song_UI_list.pop(i)
                break

        
        
class App():
    def __init__(self,*,
                 title="Favorite Song Playlist Thing",
                 geometry="600x350",
                 root_bg="Black",
                 frame_bg="WHITE",
                 txt_bg="Grey",
                 ):
        self.song_UI_list = []
        self.title = "favorite songs" # Song List Title
        split = geometry.split("x")
        # Column is x, Row is y...

        # Window
        root = Tk()
        root.configure(background=root_bg)
        root.title(title)
        self.root = root
        
        # Lambda functions for laziness
        new_entry = lambda: Entry(sideFrame,foreground="white")
        new_label = lambda x: Label(sideFrame, text=x)
        newButton = lambda cmd,text: Button(sideFrame,command=cmd,text=text)
        newOtherButton = lambda root,cmd,text: Button(root,command=cmd,text=text)

        # Frame thing
        frame = Frame(root)
        frame.configure(background=frame_bg,height=split[0],width=split[1])
        frame.grid(column=1,row=0,sticky="n")
        self.frame = frame
        
        # Box Display for stuffs
        display = Canvas(frame,background=txt_bg,borderwidth=2,width=300,height=300)
        display.grid(column=1,row=1,sticky="n")
        self.display = display
        
        # Side Frame
        sideFrame = Frame(root)
        sideFrame.configure(background=frame_bg,height=100,width=300)
        sideFrame.grid(column=2,row=0,sticky="n")
        self.sideframe = sideFrame
        
        # Title Label
        display_label = Label(display,text=self.title,state="normal",background="grey")
        display_label.configure(width=50,height=1,anchor="n")
        display_label.grid(row=0,column=2,sticky="n")
        display_label.columnconfigure(1,weight=20)
        self.display_label = display_label
        
        # Input Box For Song Title
        inputBox = new_entry()
        inputBox.grid(column=1,row=0,sticky="w")
        inputBox.columnconfigure(2,weight=12)
        self.inputBox = inputBox
        
        # Input box for artist
        artistInputBox = new_entry()
        artistInputBox.grid(column=1,row=1,sticky="w")
        artistInputBox.columnconfigure(2,weight=12)
        self.artistInputBox = artistInputBox
        
        # Input Box for URL
        commentInputBox = new_entry()
        commentInputBox.grid(column=1,row=2,sticky="w")
        self.commentInputBox = commentInputBox
        
        # Label for song title input
        inputBoxLabel = new_label("Title: ")
        inputBoxLabel.grid(column=0,row=0,sticky="nesw")
        inputBoxLabel.columnconfigure(1,weight=12)
        self.inputBoxLabel = inputBoxLabel
        
        # Label for song Artist input
        songInputLabel = new_label("Artist: ")
        songInputLabel.grid(column=0,row=1,sticky="nesw")
        songInputLabel.columnconfigure(1,weight=12)
        self.songInputLabel = songInputLabel
        
        # Label for URL input
        commentInputLabel = new_label("Comment: ")
        commentInputLabel.grid(column=0,row=2,sticky="nesw")
        commentInputLabel.columnconfigure(1,weight=12,minsize=12)
        self.commentInputLabel = commentInputLabel
        self.inputs = [commentInputBox,inputBox,artistInputBox]
        
        # clear ALL songs button
        clear_button = newButton(self.clearAllSongs,"clear")
        clear_button.grid(column=3,row=0)
        self.clear_button = clear_button
        
        # Save slot Button
        save_button = newButton(self.save,"Save")
        save_button.grid(column=3,row=1,sticky="nesw")
        self.save_button = save_button
        
        # The Add Song Button
        button = newButton(self.add,"add")
        button.grid(column=4,row=0,sticky="nesw")
        self.button = button
        
        # Load slot Button
        load_button = newButton(self.load,"Load")
        load_button.grid(column=4,row=1,sticky="nesw")
        self.load_button = load_button
        
        # New Title Button
        new_title_button = newOtherButton(display,self.newTitle,"N")
        new_title_button.grid(column=4,row=0,sticky="e")
        self.new_title_button = new_title_button
        
        # Settings Button
        self.settings = Settings(root,self)
        
        # Undo/Redo Button
        self.changes = [] # List for changes to remember
        self.version = 0
        undoButton = Button(sideFrame,text="U",command=self.undo)
        undoButton.grid(column=3,row=2,sticky="nesw")
        self.undoButton = undoButton
        redoButton = Button(sideFrame,text="R",command=self.redo)
        redoButton.grid(column=4,row=2,sticky="nesw")
        self.redoButton = redoButton
        
        
    # Save to Version Logs
        
    # Load Version
    def loadVersion(self,version):
        try:
            self.changes[version].mainloop()
            self.root.quit()
        except Exception:
            askstring(prompt="VERSION LOAD FAILED")
            
    # Undo, loading last version
    def undo(self):
        if self.version>0:
            self.version-=1
        self.loadVersion(self.version)
        
        
    # Redo loading next version
    def redo(self):
        if self.version<len(self.changes):
            self.version+=1
        self.loadVersion(self.version)
        
        
    # Make a new title
    def newTitle(self):
        self.title = askstring("New Title Label","Input a new Title:",initialvalue=self.display_label.cget("text"))
        self.display_label.configure(text=self.title)
        
    # Clear entire song playlist
    def clearAllSongs(self):
        for i in self.inputs:
            i.delete("0","end")
        while len(self.song_UI_list):
            self.song_UI_list[0].remove()
    
    # Save as JSON File
    def save(self):
        # name = askstring("Please input a Name.","Save File Name: ",initialvalue="SDA_save") (prompt)
        
        # Use the title of the Playlist as the filename.
        name = self.display_label.cget("text") 
        # Save to Documents
        fileDirectory = path.join(path.expanduser('~'),'Documents',name)
        with open(f"{fileDirectory}.json","w+") as file:
            save = []
            for i in self.song_UI_list:
                get = i.song.getJSON()
                save.append(get)
            file.write(dumps(save))
        print(f"SAVED FILE as {name}")

    # Load a JSON File, also update it if it's an old JSON.
    def load(self):
        print("\n\n\nLOADING FILE\n\n\n")
        loadFile = filedialog.askopenfile(mode="r+",filetypes=[('JSON File', '*.json')])
        if loadFile:
            self.display_label.configure(text=path.basename(loadFile.name)[0:len(path.basename(loadFile.name))-5])
            self.clearAllSongs()
            for i in load(loadFile):
                if i.get('singer'): # For older versions
                    i["comment"] = i.get('singer')
                self.add(name=i.get('name'),artist=i.get('artist'),comment=i.get("comment"))
    
    # Add a new song to the display
    def add(self,*args,artist=None,name=None,comment=None):
        # To Append widget at the bottom of the display
        span = self.display.grid_info().get("rowspan")+1 
        newSong = Song() # Song Variable initialized
        
        # Check if any variables have been passed, if not, just add the inputs
        if not(artist or name or comment):
            # print(f"inputted artist:{self.artistInputBox.get()}\nName:{self.inputBox.get()}\nComment:{self.commentInputBox.get()}") debug
            newSong = Song(artist=self.artistInputBox.get(),name=self.inputBox.get(),comment=self.commentInputBox.get())
        else:
            newSong = Song(artist=artist,name=name,comment=comment)
        
        print(f"new song \nArtist:{newSong.artist}\nName:{newSong.name}\nComment:{newSong.comment}") #Debug
        self.song_UI_list.append(Song_UI(self.display,self,song=newSong,column=1,row=span)) 
        
        # Clear Song Name input and Comment input
        self.inputs[1].delete("0","end")
        self.inputs[0].delete("0","end")
        
    # Run forever
    def mainloop(self):
        self.root.mainloop()


app = App()
app.mainloop()
