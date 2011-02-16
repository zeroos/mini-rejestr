#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk,gobject, pickle, datetime

WINDOW_TITLE = "rejestr mini"
DB_FILE = "data.db"

class MiniRejestr:
	unsavedData = False
	saveTime = 2
	def saveTimeout(self):
		if(self.saveTime == 0):
			self.save()
		elif(self.saveTime < 0):
			self.saveTime = 0
		else:
			self.saveTime-=1
			gobject.timeout_add(1000, self.saveTimeout)


	def setDataUnsaved(self):
		self.window.set_title("* " + WINDOW_TITLE)
		self.saveTime = 2
		if not self.unsavedData: #new save
			self.saveTimeout()
			self.unsavedData = True
	def save(self, data=None):
		myStore = []
		for row in self.store:
			myRow = []
			for field in row:
				myRow += [field]
			myStore += [myRow]

		pickle.dump(myStore, open(DB_FILE, "w"))

		self.unsavedData = False
		self.window.set_title(WINDOW_TITLE)
	def add(self, data=None):
		self.store.append(["+ nowy pacjent", ""])
	def delete(self, data=None):
		selection=self.treeview.get_selection()
		result = selection.get_selected()
		model, iter = result
		if(not iter):
			dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Nie wybrano pacjenta do usunięcia.")
			def close(a=None, b=None):
				dialog.destroy()
			dialog.connect("response", close)
			dialog.show()
			return
		self.store.remove(iter)
	def insertDate(self, data=None):
		self.textBuffer.insert_at_cursor("\n" + datetime.date.today().strftime("%d.%m.%Yr.") + " - ")


	def nameEdited(self, cell, path, new_text, store):
		store[path][0] = new_text
		self.setDataUnsaved()
	def nameSelected(self, treeview):
		path, col = treeview.get_cursor()
		if(path!=None):
			self.textBuffer.set_text(self.store[path][1])
			self.textView.set_editable(True)
		else:
		 	self.textBuffer.set_text("Wybierz pacjenta z listy po lewej stronie.")
			self.textView.set_editable(False)

	def textChanged(self, data=None):
		selection=self.treeview.get_selection()
		result = selection.get_selected()
		model,iter = result
		if not iter: #nothing selected
			return
		start, end = self.textBuffer.get_bounds()
		path = self.store.get_path(iter)
		self.store[path][1] = self.textBuffer.get_text(start, end)
		self.setDataUnsaved()
	
	def delete_event(self,widget,event,data=None):
		return False #delete
	def destroy(self, widget, data=None):
		gtk.main_quit()

	def key_pressed(self, window, event):
		if(event.keyval == 115 and event.state == 4):#ctrl + s
			self.save() 


	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.connect("key-press-event", self.key_pressed)
		self.window.set_title(WINDOW_TITLE)

		self.store = gtk.ListStore(str, str)
		self.store.set_sort_column_id(0, gtk.SORT_ASCENDING)
	
		try:
			data = pickle.load(open(DB_FILE))
			for row in data:
				self.store.append(row)
		except:
			pass

		self.treeview = gtk.TreeView(model=self.store)
		self.treeview.connect('cursor-changed', self.nameSelected)
		cellRenderer = gtk.CellRendererText()
		cellRenderer.set_property('editable', True)
		cellRenderer.connect('edited', self.nameEdited, self.store)
		self.treeview.append_column(gtk.TreeViewColumn("Pacjenci", cellRenderer, text=0))

		self.textBuffer = gtk.TextBuffer()
		self.textBuffer.connect('changed', self.textChanged)
		self.textView = gtk.TextView(self.textBuffer)
		self.textView.set_wrap_mode(gtk.WRAP_WORD)

		rightPanel = gtk.ScrolledWindow()
		rightPanel.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		rightPanel.add(self.textView)
		leftPanel = gtk.ScrolledWindow()
		leftPanel.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		leftPanel.add(self.treeview)
		

		#buttons
		addButton, delButton, saveButton, dateButton = gtk.Button(), gtk.Button(), gtk.Button(), gtk.Button()
		addImage, delImage, saveImage, dateImage = gtk.Image(), gtk.Image(), gtk.Image(), gtk.Image()
		addImage.set_from_file("./img/add.png")
		delImage.set_from_file("./img/del.png")
		saveImage.set_from_file("./img/save.png")
		dateImage.set_from_file("./img/date.png")
		
		addButton.set_image(addImage)
		delButton.set_image(delImage)
		saveButton.set_image(saveImage)
		dateButton.set_image(dateImage)

		addButton.connect("clicked", self.add)
		delButton.connect("clicked", self.delete)
		saveButton.connect("clicked", self.save)
		dateButton.connect("clicked", self.insertDate)

		buttons = gtk.HBox()
		buttons.pack_start(addButton, False, False, 0)
		buttons.pack_start(delButton, False, False, 0)
		buttons.pack_start(saveButton, False, False, 0)
		buttons.pack_start(dateButton, False, False, 0)
		

		mainPanel=gtk.HPaned()
		mainPanel.set_position(150)
		mainPanel.pack1(leftPanel)
		mainPanel.pack2(rightPanel)

		everything = gtk.VBox()
		everything.pack_start(buttons, expand=False)
		everything.pack_start(mainPanel)

		self.nameSelected(self.treeview)#init right panel
		self.window.resize(500,300)
		self.window.add(everything)



		self.window.show_all()
	def main(self):
		gtk.main()

	


if __name__ == "__main__":
	base = MiniRejestr()
	base.main()
