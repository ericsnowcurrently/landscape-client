import os

from gettext import gettext as _

from gi.repository import GObject, Gtk

from landscape.ui.constants import (
    CANONICAL_MANAGED, LOCAL_MANAGED, NOT_MANAGED)


class ClientSettingsDialog(Gtk.Dialog):
    """
    L{ClientSettingsDialog} is a subclass of Gtk.Dialog that loads the UI
    components from the associated Glade XML file and wires everything up to
    the controller.
    """

    GLADE_FILE = "landscape-client-settings.glade"
    NO_SERVICE_TEXT = _("None")
    HOSTED_SERVICE_TEXT = _("Landscape - hosted by Canonical")
    LOCAL_SERVICE_TEXT = _("Landscape - dedicated server")
    REGISTER_BUTTON_TEXT = _("Register")
    DISABLE_BUTTON_TEXT = _("Disable")

    def __init__(self, controller):
        super(ClientSettingsDialog, self).__init__(
            title=_("Management Service"),
            flags=Gtk.DialogFlags.MODAL)
        self.set_default_icon_name("preferences-management-service")
        self.set_resizable(False)
        self._initialised = False
        self.controller = controller
        self.setup_ui()
        self.load_data()
        # One extra revert to reset after loading data
        self.controller.revert()

    def _set_use_type_combobox_from_controller(self):
        """
        Load the persisted L{management_type} from the controller and set the
        combobox appropriately.

        Note that Gtk makes us jump through some hoops by having it's own model
        level to deal with here.  The conversion between paths and iters makes
        more sense if you understand that treeviews use the same model.
        """
        list_iter = self.liststore.get_iter_first()
        while (self.liststore.get(list_iter, 0)[0] !=
               self.controller.management_type):
            list_iter = self.liststore.iter_next(list_iter)
        path = self.liststore.get_path(list_iter)
        [index] = path.get_indices()
        self.use_type_combobox.set_active(index)

    def _set_hosted_values_from_controller(self):
        self.hosted_account_name_entry.set_text(
            self.controller.hosted_account_name)
        self.hosted_password_entry.set_text(self.controller.hosted_password)

    def _set_local_values_from_controller(self):
        self.local_landscape_host_entry.set_text(
            self.controller.local_landscape_host)
        self.local_password_entry.set_text(self.controller.local_password)

    def load_data(self):
        self._initialised = False
        self.controller.load()
        self._set_hosted_values_from_controller()
        self._set_local_values_from_controller()
        self._set_use_type_combobox_from_controller()
        self._initialised = True

    def make_liststore(self):
        """
        Construct the correct L{Gtk.ListStore} to drive the L{Gtk.ComboBox} for
        use-type.  This a table of:

           * Management type (key)
           * Text to display in the combobox
           * L{Gtk.Frame} to load when this item is selected.
        """
        liststore = Gtk.ListStore(GObject.TYPE_PYOBJECT,
                                  GObject.TYPE_STRING,
                                  GObject.TYPE_PYOBJECT)
        self.active_widget = None
        liststore.append([NOT_MANAGED, self.NO_SERVICE_TEXT,
                          self._builder.get_object("no-service-frame")])
        liststore.append([CANONICAL_MANAGED, self.HOSTED_SERVICE_TEXT,
                          self._builder.get_object("hosted-service-frame")])
        liststore.append([LOCAL_MANAGED, self.LOCAL_SERVICE_TEXT,
                          self._builder.get_object("local-service-frame")])
        return liststore

    def link_hosted_service_widgets(self):
        self.hosted_account_name_entry = self._builder.get_object(
            "hosted-account-name-entry")
        self.hosted_account_name_entry.connect(
            "changed", self.on_changed_event, "hosted_account_name")

        self.hosted_password_entry = self._builder.get_object(
            "hosted-password-entry")
        self.hosted_password_entry.connect(
            "changed", self.on_changed_event, "hosted_password")

    def link_local_service_widgets(self):
        self.local_landscape_host_entry = self._builder.get_object(
            "local-landscape-host-entry")
        self.local_landscape_host_entry.connect(
            "changed", self.on_changed_event, "local_landscape_host")

        self.local_password_entry = self._builder.get_object(
            "local-password-entry")
        self.local_password_entry.connect(
            "changed", self.on_changed_event, "local_password")

    def link_use_type_combobox(self, liststore):
        self.use_type_combobox = self._builder.get_object("use-type-combobox")
        self.use_type_combobox.connect("changed", self.on_combo_changed)
        self.use_type_combobox.set_model(liststore)
        cell = Gtk.CellRendererText()
        self.use_type_combobox.pack_start(cell, True)
        self.use_type_combobox.add_attribute(cell, 'text', 1)

    def cancel_response(self, widget):
        self.response(Gtk.ResponseType.CANCEL)

    def register_response(self, widget):
        self.response(Gtk.ResponseType.OK)

    def set_button_text(self, management_type):
        [alignment] = self.register_button.get_children()
        [hbox] = alignment.get_children()
        [image, label] = hbox.get_children()
        if management_type == NOT_MANAGED:
            label.set_text(self.DISABLE_BUTTON_TEXT)
        else:
            label.set_text(self.REGISTER_BUTTON_TEXT)

    def setup_buttons(self):
        self.revert_button = Gtk.Button(stock=Gtk.STOCK_REVERT_TO_SAVED)
        self.action_area.pack_start(self.revert_button, True, True, 0)
        self.revert_button.connect("clicked", self.revert)
        self.revert_button.show()
        self.cancel_button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        self.action_area.pack_start(self.cancel_button, True, True, 0)
        self.cancel_button.show()
        self.cancel_button.connect("clicked", self.cancel_response)
        self.register_button = Gtk.Button(stock=Gtk.STOCK_OK)
        self.action_area.pack_start(self.register_button, True, True, 0)
        self.register_button.show()
        self.register_button.connect("clicked", self.register_response)

    def setup_ui(self):
        self._builder = Gtk.Builder()
        self._builder.add_from_file(
            os.path.join(
                os.path.dirname(__file__), "ui", self.GLADE_FILE))
        content_area = self.get_content_area()
        content_area.set_spacing(12)
        self.set_border_width(12)
        self._vbox = self._builder.get_object("toplevel-vbox")
        self._vbox.unparent()
        content_area.pack_start(self._vbox, expand=True, fill=True, padding=12)
        self.liststore = self.make_liststore()
        self.link_use_type_combobox(self.liststore)
        self.link_hosted_service_widgets()
        self.link_local_service_widgets()
        self.setup_buttons()

    def on_combo_changed(self, combobox):
        list_iter = self.liststore.get_iter(combobox.get_active())
        if not self.active_widget is None:
            self._vbox.remove(self.active_widget)
        [management_type] = self.liststore.get(list_iter, 0)
        self.set_button_text(management_type)
        if self._initialised:
            self.controller.management_type = management_type
            self.controller.modify()
        [self.active_widget] = self.liststore.get(list_iter, 2)
        self.active_widget.unparent()
        self._vbox.add(self.active_widget)

    def on_changed_event(self, widget, attribute):
        setattr(self.controller, attribute, widget.get_text())
        self.controller.modify()

    def quit(self, *args):
        self.destroy()

    def revert(self, button):
        self.controller.revert()
        self.load_data()
        # One extra revert to reset after loading data
        self.controller.revert()
