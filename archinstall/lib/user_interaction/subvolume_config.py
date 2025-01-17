from ..menu.list_manager import ListManager
from ..menu.selection_menu import Selector, GeneralMenu
from ..menu.text_input import TextInput
from ..menu import Menu
"""
UI classes
"""

class SubvolumeList(ListManager):
	def __init__(self,prompt,list):
		self.ObjectNullAction = None # str(_('Add'))
		self.ObjectDefaultAction = str(_('Add'))
		super().__init__(prompt,list,None,self.ObjectNullAction,self.ObjectDefaultAction)

	def reformat(self):
		def presentation(key,value):
			text = _(" Subvolume :{:16}").format(key)
			if isinstance(value,str):
				text += _(" mounted at {:16}").format(value)
			else:
				if value.get('mountpoint'):
					text += _(" mounted at {:16}").format(value['mountpoint'])
				else:
					text += (' ' * 28)
				if value.get('options',[]):
					text += _(" with option {}").format(', '.join(value['options']))
			return text

		return sorted(list(map(lambda x:presentation(x,self.data[x]),self.data)))

	def action_list(self):
		return super().action_list()

	def exec_action(self):
		if self.target:
			origkey,origval = list(self.target.items())[0]
		else:
			origkey = None

		if self.action == str(_('Delete')):
			del self.data[origkey]
			return True

		if self.action == str(_('Add')):
			self.target = {}
			print(_('\n Fill the desired values for a new subvolume \n'))
			with SubvolumeMenu(self.target,self.action) as add_menu:
				for data in ['name','mountpoint','options']:
					add_menu.exec_option(data)
		else:
			SubvolumeMenu(self.target,self.action).run()
		self.data.update(self.target)

		return True

class SubvolumeMenu(GeneralMenu):
	def __init__(self,parameters,action=None):
		self.data = parameters
		self.action = action
		self.ds = {}
		self.ds['name'] = None
		self.ds['mountpoint'] = None
		self.ds['options'] = None
		if self.data:
			origkey,origval = list(self.data.items())[0]
			self.ds['name'] = origkey
			if isinstance(origval,str):
				self.ds['mountpoint'] = origval
			else:
				self.ds['mountpoint'] = self.data[origkey].get('mountpoint')
				self.ds['options'] = self.data[origkey].get('options')

		super().__init__(data_store=self.ds)

	def _setup_selection_menu_options(self):
		# [str(_('Add')),str(_('Copy')),str(_('Edit')),str(_('Delete'))]
		self._menu_options['name'] = Selector(str(_('Subvolume name ')),
			self._select_subvolume_name if not self.action or self.action in (str(_('Add')),str(_('Copy'))) else None,
			mandatory=True,
			enabled=True)
		self._menu_options['mountpoint'] = Selector(str(_('Subvolume mountpoint')),
			self._select_subvolume_mount_point if not self.action or self.action in (str(_('Add')),str(_('Edit'))) else None,
			enabled=True)
		self._menu_options['options'] = Selector(str(_('Subvolume options')),
			self._select_subvolume_options if not self.action or self.action in (str(_('Add')),str(_('Edit'))) else None,
			enabled=True)
		self._menu_options['save'] = Selector(str(_('Save')),
													exec_func=lambda n,v:True,
													enabled=True)
		self._menu_options['cancel'] = Selector(str(_('Cancel')),
													# func = lambda pre:True,
													exec_func=lambda n,v:self.fast_exit(n),
													enabled=True)
		self.cancel_action = 'cancel'
		self.save_action = 'save'
		self.bottom_list = [self.save_action,self.cancel_action]

	def fast_exit(self,accion):
		if self.option(accion).get_selection():
			for item in self.list_options():
				if self.option(item).is_mandatory():
					self.option(item).set_mandatory(False)
		return True

	def exit_callback(self):
		# we exit without moving data
		if self.option(self.cancel_action).get_selection():
			return
		if not self.ds['name']:
			return
		else:
			key = self.ds['name']
			value = {}
			if self.ds['mountpoint']:
				value['mountpoint'] = self.ds['mountpoint']
			if self.ds['options']:
				value['options'] = self.ds['options']
			self.data.update({key : value})

	def _select_subvolume_name(self,value):
		return TextInput(str(_("Subvolume name :")),value).run()

	def _select_subvolume_mount_point(self,value):
		return TextInput(str(_("Select a mount point :")),value).run()

	def _select_subvolume_options(self,value):
		# def __init__(self, title, p_options, skip=True, multi=False, default_option=None, sort=True):
		return Menu(str(_("Select the desired subvolume options ")),['nodatacow','compress'],
			skip=True,preset_values=value,multi=True).run()
