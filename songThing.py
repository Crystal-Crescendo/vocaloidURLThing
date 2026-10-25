# Song Class
from tkinter import Tk, Label, Frame, Button, Canvas, filedialog, Entry, Scrollbar
from tkinter.simpledialog import askstring
from tkinter.colorchooser import askcolor
from abc import ABC, abstractmethod
from json import dumps, load, JSONDecodeError
from os import path

# Sound effects
# Backend Classes
# Class For storing songs
VERSION = "0.5"

# Superclass for Saved Data
class Saved:
    # Check if the type of data is the same as another.
    def checkSameType(self,check):
        return type(check)==type(self)
    # Abstract method, return as dictionary containing key and value pairs of all variables
    @abstractmethod
    def getJSON():
        pass

# Song Saves! For Song_UI
class SaveSong(Saved):
    
    # Constructor
    def __init__(self,*,artist="",name="",comment="",same=None,dic=None):
        if Saved.checkSameType(self=self,check=same):
            self.name = same.name
            self.artist = same.artist
            self.comment = same.comment
        elif dic:
            self.name = dic["name"]
            self.artist = dic["artist"]
            self.comment = dic["comment"]
        else:
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

class SaveColor(Saved):
    
    def __init__(self,*,side=None,back=None,settings=None,display=None,same=None,dic=None):
        
        # Match App Colors with another SaveColor Object
        if Saved.checkSameType(self=self,check=same):
            self.side = same.side
            self.back = same.back
            self.settings = same.settings
            self.display = same.display
            
        # Match App Colors with a dictionary that contains same variables.
        elif dic:
            self.side = dic.get("side")
            self.back = dic.get("back")
            self.settings = dic.get("settings")
            self.display = dic.get("display")
            
        # Match Colors with passed colors in constructor
        else:
            self.side = side
            self.back = back
            self.settings = settings
            self.display = display
        
    # Abstract method
    def getJSON(self):
        return {"side":self.side,"back":self.back,"settings":self.settings,"display":self.display}
    
# Class for redo/undo Saving, and file saving...

class SaveApp(Saved):
    
    # Constructor
    def __init__(self,*,song_UI_list=[],title="",savedColor=SaveColor(),version=VERSION,same=None,dic=None):
        # Match with same object
        if Saved.checkSameType(self=self,check=same):
            self.title = same.title
            self.song_UI_list = same.song_UI_list
            self.savedColor = same.savedColor
            self.version = same.version
        elif dic:
            self.title = dic.get("title")
            self.song_UI_list = dic.get("song_UI_list")
            self.savedColor = dic.get("savedColor")
            self.version = dic.get("version")
        else:
            self.title = title
            self.song_UI_list = song_UI_list
            self.savedColor = savedColor
            self.version = version
    def getJSON(self):
        return {"title":self.title,"version":self.version,"song_UI_list":self.song_UI_list,"savedColor":self.savedColor}

    
# Frontend Classes

# Parent Superclass for basically all the other Classes.
class BaseWidgetExtension(ABC):
    # Constructor
    def __init__(self,root,parent):
        self.root = root
        self.parent = parent

    # Update a widget, and it's children, colors
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

# Color Setting Widget, placed inside Settings

class SaveColorSetting(BaseWidgetExtension,Saved):
    # Constructor
    def __init__(self,parent,name,*,modify=[],TYPE=0,color=None):
        # Superclass constructor
        super().__init__(parent.parent.display,parent)
        
        # Type of Color Settings.
        # Type 0 Color Settings Will update all descendants aswell, 
        # Any other type will only update this specific modify element.
        # Meant to be used for updateColors.
        self.type = TYPE 
        self.color = color
        
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
                if type(i)==SaveSongUI:
                    i.updateColor(color)
                else:
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
    def getJSON(self):
        return {"color":self.color}
    # Removal (Abstract method)
    def remove(self):
        self.frame.destroy()
        
# Settings Widget

class Settings(BaseWidgetExtension):
    # Constructor
    def __init__(self,root,parent,row=0,column=0,brow=0,bcol=1):
        # Superclass Constructor
        BaseWidgetExtension.__init__(BaseWidgetExtension,root,parent)
        # Settings Button
        button = Button(parent.display,command=self.update,text="S")
        button.grid(row=brow,column=bcol,sticky="nw")
        self.button = button
        
        # Framework
        frame = Frame(root,padx=25)
        frame.grid(column=column,row=row,sticky="n")
        frame.grid_remove()
        self.frame = frame
        self.shown = False
        
        # The Settings
        self.sideColor = SaveColorSetting(self,"Sideframe Color",modify=parent.hostFrame)
        self.settingsColor = SaveColorSetting(self,"Settings Color",modify=self.frame,TYPE=1)
        self.backgroundColor = SaveColorSetting(self,"Background Color",modify=parent.root,TYPE=1)
        self.displayColor = SaveColorSetting(self,"Display Color",modify=parent.display)

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
    
    # Get Color settings
    def getColors(self):
        dic = {"side":self.sideColor.getJSON(),"settings":self.settingsColor.getJSON(),"back":self.backgroundColor.getJSON(),"display":self.displayColor.getJSON()}
        return SaveColor(dic=dic)
    # Remove the widget (Abstract method)
    def remove(self):
        self.frame.destroy()
        self.button.destroy()
        
# Song UI Widget
class SaveSongUI(Saved,BaseWidgetExtension):
    
    # Constructor
    def __init__(self,root,parent,song=SaveSong()):
        # Superclass Constructor
        BaseWidgetExtension.__init__(BaseWidgetExtension,root,parent)
        
        # Initalize Variables
        self.specialColor = None
        self.song = song
        self.pos = len(root.grid_slaves())
        self.parent = self.parent
        
        frame = Canvas(root,width=50)
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
        
        # Comment
        commentFrame = Canvas(frame)
        commentFrame.grid(column=0,row=1)
        commentLabel = Label(commentFrame,text=f"Comment:")   
        commentLabel.grid(column=0,row=0,sticky="nw")
        commentComment = Label(commentFrame,text=str(self.song.comment)) 
        commentComment.grid(column=1,row=0)
        commentFrame.grid_remove()
        self.show_comment = False
        self.commentComment = commentComment
        self.commentFrame = commentFrame
        self.commentLabel = commentLabel
        
        # comment Button
        infoButton = Button(frame,text="i",command=self.comment)
        infoButton.grid(column=4,row=0,sticky="e")
        self.infoButton = infoButton
        
        # Remove Button
        removeButton = Button(frame,text="X",command=self.remove)
        removeButton.grid(column=5,row=0,sticky="e")
        self.removeButton = removeButton
        
        # Configure Button
        configButton = Button(frame,text="*",command=self.configure)
        configButton.grid(column=6,row=0,sticky="e")
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
            color = askcolor()
            substr = str(color).split("), '")[1]
            print(color)
            print(str(color))
            print(substr)
            y = substr[0:len(substr)-2]
            self.updateColor(y,type=1)
            
    # Get as a Dictionary, meant for JSON files
    def getJSON(self):
        return {"song":self.song,"color":self.color}
    
    # Show the song's comment
    def comment(self):
        self.commentComment.config(text=self.song.comment) # Update in case
        if self.show_comment:
            self.commentFrame.grid_remove()
            self.show_comment=False
        else:
            self.commentFrame.grid()
            self.show_comment=True
    def updateInfo(self):
        self.artist.configure(text=f"by {self.song.artist}")
        self.title.configure(text=self.song.name)
    
    def updateColor(self,color,*,type=0):
        def update():
            self.frame.configure(background=color)
            for i in self.frame.grid_slaves():
                i.configure(background=color)
                i.configure(highlightbackground=color)
        # Type 0 will modify the color if it doesn't have a special color already.
        if type==0:
            if not self.specialColor:
                update()
        #Type 1 will make this the special Color for the UI widget.
        elif type==1:
            self.specialColor = color
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

        
        
class App:
    def __init__(self,*,
                 title="Favorite Song Playlist Thing",
                 geometry="600x350",
                 root_bg="Black",
                 frame_bg="WHITE",
                 txt_bg="Grey",
                 ):
        self.changes = [] # List for changes to remember
        self.version = 0
        self.song_UI_list = []
        self.title = "favorite songs" # Song List Title
        split = geometry.split("x")
        # Column is x, Row is y...

        # Window
        root = Tk()
        root.configure(background=root_bg)
        root.title(title)
        self.root = root
        
        # Frame thing
        frame = Frame(root)
        frame.configure(background=frame_bg,height=split[0],width=split[1])
        frame.grid(column=1,row=1,sticky="n")
        self.frame = frame
        
        # Box Display for stuffs
        display = Canvas(frame,background=txt_bg,borderwidth=2)
        display.grid(column=1,row=4,sticky="n")
        self.display = display
        
        # Host Frame
        hostFrame = Frame(root)
        hostFrame.configure(background=frame_bg)
        hostFrame.grid(column=1,row=0,sticky="w")
        self.hostFrame = hostFrame
        
        # Side Frame
        sideFrame = Frame(hostFrame)
        sideFrame.configure(background=frame_bg)
        sideFrame.grid(column=0,row=1,sticky="n")
        self.sideFrame = sideFrame
        
        # Lambda functions for convenience
        new_entry = lambda root=self.sideFrame: Entry(root,foreground="white")
        new_label = lambda x,root=self.sideFrame: Label(root, text=x)
        newButton = lambda cmd,text,root=self.sideFrame: Button(root,command=cmd,text=text)
        
        # Song Display
        songDisplay = Canvas(display,background=txt_bg,borderwidth=2,border=2)
        songDisplay.grid(row=1,column=2,columnspan=2,sticky="n")
        self.songDisplay = songDisplay
        
        # Scrollbar for the songs display
        scroll = Scrollbar(songDisplay,orient="vertical",command=songDisplay.yview)
        songDisplay.config(yscrollcommand=scroll.set)
        scroll.grid(column=3,sticky="e")
        self.scroll = scroll
        
        # Hide/Show Button for Adding Songs
        sideVisibilityButton = newButton(self.sideVisibility,"-",root=root)
        sideVisibilityButton.grid(column=1,row=1,sticky="nw")
        self.sideVisibilityButton = sideVisibilityButton
        self.visible = True
        
        # Title Label
        display_label = Label(display,width=40,text=self.title,state="normal",background="grey",padx=30)
        display_label.grid(row=0,column=2,sticky="n")
        self.display_label = display_label
        
        # Input Box For Song Title
        inputBox = new_entry()
        inputBox.grid(column=1,row=0,sticky="w")
        self.inputBox = inputBox
        
        # Input box for artist
        artistInputBox = new_entry()
        artistInputBox.grid(column=1,row=1,sticky="w")
        self.artistInputBox = artistInputBox
        
        # Input Box for URL
        commentInputBox = new_entry()
        commentInputBox.grid(column=1,row=2,sticky="w")
        self.commentInputBox = commentInputBox
        
        # Label for song title input
        inputBoxLabel = new_label("Title: ")
        inputBoxLabel.grid(column=0,row=0,sticky="nesw")
        self.inputBoxLabel = inputBoxLabel
        
        # Label for song Artist input
        songInputLabel = new_label("Artist: ")
        songInputLabel.grid(column=0,row=1,sticky="nesw")
        self.songInputLabel = songInputLabel
        
        # Label for URL input
        commentInputLabel = new_label("Comment: ")
        commentInputLabel.grid(column=0,row=2,sticky="nesw")
        self.commentInputLabel = commentInputLabel
        self.inputs = [commentInputBox,inputBox,artistInputBox]
        
        # clear ALL songs button
        clear_button = newButton(self.clearAllSongs,"C")
        clear_button.grid(column=3,row=0)
        self.clear_button = clear_button
        
        # Save slot Button
        save_button = newButton(self.save,"S")
        save_button.grid(column=3,row=1,sticky="nesw")
        self.save_button = save_button
        
        # The Add Song Button
        button = newButton(self.add,"A")
        button.grid(column=4,row=0,sticky="nesw")
        self.button = button
        
        # Load slot Button
        load_button = newButton(self.load,"L")
        load_button.grid(column=4,row=1,sticky="nesw")
        self.load_button = load_button
        
        # New Title Button
        new_title_button = newButton(self.newTitle,"N",root=display)
        new_title_button.grid(column=5,row=0,sticky="e")
        self.new_title_button = new_title_button
        
        # Settings Button
        self.settings = Settings(root,self,row=1,column=0,brow=1,bcol=0)
        
        # Undo/Redo Buttons
        
        undoButton = newButton(text="U",cmd=self.undo)
        undoButton.grid(column=3,row=2,sticky="nesw")
        self.undoButton = undoButton
        
        redoButton = newButton(text="R",cmd=self.redo)
        redoButton.grid(column=4,row=2,sticky="nesw")
        self.redoButton = redoButton
    def sideVisibility(self):
        if self.visible:
            self.sideVisibilityButton.config(text="+")
            self.hostFrame.grid_remove()
            self.visible = False
        else:
            self.sideVisibilityButton.config(text="-")
            self.hostFrame.grid()
            self.visible = True
    
    # Save to Version Logs
    def saveVersion(self):
        print("Saved this change!")
        self.changes.append(SaveApp(song_UI_list=self.song_UI_list,title=self.title,savedColor=SaveColor(same=self.settings.getColors())))
        self.version+=1
    
    # Throw a popup message
    def throw(self,title="",text="",ExceptionX=""):
        askstring(title=title,prompt=f"{text}{ExceptionX}")
        
    # Load Version From Undo/Redo History
    def loadVersion(self,change):
        prevVersion = self.version
        resultVersion = int(self.version+change)
        if resultVersion<len(self.changes) and resultVersion>0:
            save = SaveApp(song_UI_list=self.song_UI_list,title=self.title,savedColor=SaveColor(same=self.settings.getColors()))
            self.clearAllSongs()
            self.version+=change
            try:
                for i in self.changes[resultVersion].song_UI_list:
                    self.add(artist=i.song.artist,name=i.song.name,comment=i.song.comment)
            except Exception as x:
                self.throw(title="FAILED TO LOAD VERSION",text="ERROR:\n",ExceptionX=x)
        else:
            self.throw(title="oops",text="Cant keep going!")
            
    # Undo, loading last version
    def undo(self):
        self.loadVersion(-1)
        
        
    # Redo loading next version
    def redo(self):
        self.loadVersion(1)
        
        
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
        
        name = self.display_label.cget("text") # Use the title of the Playlist as the filename.
        
        # Save to Documents
        filename = path.join(path.expanduser('~'),'Documents',name)
        
        with open(f"{filename}.json","w+") as file:
            save = {}
            getList = []
            for i in self.song_UI_list:
                getList.append(i.getJSON())
            
            
            save["song_UI_list"]=getList
            save["title"]=self.title
            save["savedColor"]=self.settings.getColors().getJSON()
            print(save)
            file.write(dumps(save))
        print(f"SAVED FILE as {name}")

    # Load a JSON File, also update it if it's an old JSON.
    def load(self):
        print("\n\n\nLOADING FILE\n\n\n")
        file = filedialog.askopenfile(mode="r+",filetypes=[('JSON File', '*.json')])
        try:
            loadFile = load(file)
            if loadFile:
                self.display_label.configure(text=path.basename(file.name)[0:len(path.basename(file.name))-5])
                self.clearAllSongs()
                print(f"File type: {type(loadFile)}")
                print(f"Compare To: {list}")
                if type(loadFile)==list:
                    # For older versions
                    for i in loadFile:
                        if i.get('singer'): 
                            i["comment"] = i.get('singer')
                        self.add(name=i.get('name'),artist=i.get('artist'),comment=i.get("comment"))
                else:
                    version = loadFile.get("version")
                    title = loadFile.get("title")
                    colors = loadFile.get("savedColor")
                    songs = loadFile.get("song_UI_list")
        except JSONDecodeError as x:
            print("Couldnt read that!")
            askstring(title="EXCEPTION!",prompt=f"{x}")
        

    # Add a new song to the UI
    def add(self,*args,artist=None,name=None,comment=None):
        # To Append widget at the bottom of the display
        span = self.display.grid_info().get("rowspan")+1 
        newSong = SaveSong() # Song Variable initialized
        
        # Check if any variables have been passed, if not, just add what's in the input boxes
        if not(artist or name or comment):
            # print(f"inputted artist:{self.artistInputBox.get()}\nName:{self.inputBox.get()}\nComment:{self.commentInputBox.get()}") debug
            newSong = SaveSong(artist=self.artistInputBox.get(),name=self.inputBox.get(),comment=self.commentInputBox.get())
        else:
            newSong = SaveSong(artist=artist,name=name,comment=comment)
        
        # print(f"new song \nArtist:{newSong.artist}\nName:{newSong.name}\nComment:{newSong.comment}") # Debug
        self.song_UI_list.append(SaveSongUI(self.songDisplay,self,song=newSong)) 
        
        # Clear Song Name input and Comment input
        self.inputs[1].delete("0","end")
        self.inputs[0].delete("0","end")
        self.saveVersion()
        
    def mainloop(self):
        self.root.mainloop()


app = App()
app.mainloop()
