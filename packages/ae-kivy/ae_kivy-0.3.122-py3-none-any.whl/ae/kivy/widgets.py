"""
ae.kivy.widgets module
----------------------

this module provides constants and widgets for your multi-platform apps.

the generic constants for animations and vibration patterns (mostly used on mobile platforms).

most of the widgets provided by this module are based on the widgets of the `Kivy framework <https://kivy.org>`__,
extended to work with :ref:`app-state-variables`, e.g. to support app styles and theming (dark or light) and
user definable font sizes. some of them also change the :ref:`application flow`.

by importing this module the following generic widgets will be registered in the kivy widget class factory maps,
to be available in the kv language for your app (some of them implemented exclusively in pure kv lang within
the `widgets.kv` file of this portion):

* :class:`~ae.kivy.widgets.AppStateSlider`: extended version of :class:`~kivy.uix.slider.Slider`, changing the value of
  :ref:`app-state-variables`.
* :class:`~ae.kivy.widgets.FlowButton`: button to change the application flow.
* :class:`~ae.kivy.widgets.FlowDropDown`: attachable menu-like popup, based on :class:`~kivy.uix.dropdown.DropDown`.
* :class:`~ae.kivy.widgets.FlowInput`: text input widget based on :class:`~kivy.uix.textinput.TextInput` with
  application flow support.
* :class:`~ae.kivy.widgets.FlowPopup`: auto-content-sizing popup to query user input or to show messages.
* :class:`~ae.kivy.widgets.FlowSelector`: attachable popup used for dynamic elliptic auto-spreading menus and toolbars.
* :class:`~ae.kivy.widgets.FlowToggler`: toggle button based on :class:`~ae.kivy.widgets.ImageLabel` and
  :class:`~kivy.uix.behaviors.ToggleButtonBehavior` to change the application flow or any flag or application state.
* :class:`~ae.kivy.widgets.HelpToggler` is a toggle button widget that switches the app's help and tour mode on and off.
* IconButton: extended :class:`~ae.kivy.widgets.FlowButton` with an icon image, which can be placed relatively to the
  button screen coordinates.
* :class:`~ae.kivy.widgets.ImageLabel`: label widget extending the Kivy :class:`~kivy.uix.label.Label` widget
  with an image.
* :class:`~ae.kivy.widgets.MessageShowPopup`: simple message box widget based on :class:`~ae.kivy.widgets.FlowPopup`.
* OptionalButton: dynamically hideable button widget based on :class:`~ae.kivy.widgets.FlowButton`.
* PopupTitleBar: a :class:`~ae.kivy.widgets.FlowButton` automatically displaying long button texts with a horizontal
  auto-scroll (with the help of the :class:`~ae.kivy_auto_width.SimpleAutoTickerBehavior`).
* :class:`~ae.kivy.widgets.PopupQueryBox`: a :class:`~kivy.uix.stacklayout.StackLayout` supporting the dynamic creation
  of child widgets (with the help of :class:`~ae.kivy_dyn_chi.DynamicChildrenBehavior`).
* ReliefBox: a :class:`kivy.uix.boxlayout.BoxLayout` providing relief decorations (with the help of the
  :class:`ae.kivy_relief_canvas.ReliefCanvas` mixin class).
* ShortenedButton: button widget based on :class:`~ae.kivy.widgets.FlowButton`, which is automatically
  shortening a long button text.
* StopTourButton: a simple image button with relief canvas (with the help of the
  :class:`ae.kivy_relief_canvas.ReliefCanvas` mixin class).
* :class:`~ae.kivy.widgets.Tooltip` displays text blocks that are automatically positioned next to any
  widget to providing e.g. i18n context help texts or app tour/onboarding info.
* SwitchPageButton:  simple button with relief canvas (provided by the
  :class:`ae.kivy_relief_canvas.ReliefCanvas` mixin class) and OpenGL shader (via :class:`~ae.kivy_glsl.ShadersMixin`).
* TourPageTexts: a :class:`kivy.uix.boxlayout.BoxLayout` providing relief decorations (with the help of the
  :class:`ae.kivy_relief_canvas.ReliefCanvas` mixin class) and OpenGL shader (via :class:`~ae.kivy_glsl.ShadersMixin`).
* UserNameEditorPopup: :class:`~ae.kivy.widgets.FlowPopup` widget used to enter a username, to be registered in the
  :ref:`app config files <config-files>`.


tooltip popup to display context-sensitive help and app tour texts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

the tooltip popup widget class :class:`~ae.kivy.widgets.Tooltip` allows you to target any widget by pointing with an
arrow to it. the position and size of this widget gets automatically calculated from the targeted widget position and
size and the tooltip text size. and if the screen/window size is not big enough then the tooltip texts get scrollable.

.. hint::
    use cases of the class :class:`~ae.kivy.widgets.Tooltip` are e.g. the help texts prepared and displayed by the
    method :meth:`~ae.gui_help.HelpAppBase.help_display` as well as the "explaining widget" tooltips in an app tour.


help activation and de-activation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

use the widget class :class:`~ae.kivy.widgets.HelpToggler` provided by this module to toggle
the active state of the help mode.

.. hint::
    the :class:`~ae.kivy.widgets.HelpToggler` class is using the low-level touch events to prevent the dispatch of the
    Kivy events `on_press`, `on_release` and `on_dismiss`, to allow to show help texts for opened dropdowns and popups,
    without closing/dismissing them.

to attach help texts to your widget instances add the behavior class :class:`~ae.kivy.behaviors.HelpBehavior`.
"""
import os

from math import atan, cos, pi, sin, tau
from typing import Any, Callable, Dict, List, Optional, Tuple

import kivy                                                                                             # type: ignore
from kivy.animation import Animation                                                                    # type: ignore
from kivy.app import App                                                                                # type: ignore
from kivy.core.window import Window                                                                     # type: ignore
from kivy.graphics import Color, Ellipse, Line                                                          # type: ignore
from kivy.input import MotionEvent                                                                      # type: ignore
from kivy.lang import Builder                                                                           # type: ignore
from kivy.metrics import sp                                                                             # type: ignore
# pylint: disable=no-name-in-module
from kivy.properties import (                                                                           # type: ignore
    BooleanProperty, ColorProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty)
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior                                     # type: ignore
from kivy.uix.boxlayout import BoxLayout                                                                # type: ignore
from kivy.uix.bubble import BubbleButton                                                                # type: ignore
from kivy.uix.dropdown import DropDown                                                                  # type: ignore
from kivy.uix.image import Image                                                                        # type: ignore
from kivy.uix.label import Label                                                                        # type: ignore
from kivy.uix.relativelayout import RelativeLayout                                                      # type: ignore
from kivy.uix.scrollview import ScrollView                                                              # type: ignore
from kivy.uix.slider import Slider                                                                      # type: ignore
from kivy.uix.stacklayout import StackLayout                                                            # type: ignore
import kivy.uix.textinput                                                                               # type: ignore
# noinspection PyProtectedMember
from kivy.uix.textinput import TextInput, TextInputCutCopyPaste as OriTextInputCutCopyPaste
from kivy.uix.widget import Widget                                                                      # type: ignore

from ae.gui_app import (                                                                                # type: ignore
    ColorOrInk, ellipse_polar_radius, ensure_tap_kwargs_refs, id_of_flow, replace_flow_action, update_tap_kwargs)
from ae.gui_help import (                                                                               # type: ignore
    anchor_layout_x, anchor_layout_y, anchor_points, anchor_spec, help_id_tour_class)
from ae.kivy_auto_width import ContainerChildrenAutoWidthBehavior                                       # type: ignore
from ae.kivy_dyn_chi import DynamicChildrenBehavior                                                     # type: ignore
from ae.kivy_glsl import ShadersMixin                                                                   # type: ignore
from ae.kivy_relief_canvas import ReliefCanvas, relief_colors                                           # type: ignore

from .behaviors import HelpBehavior, ModalBehavior, SlideSelectBehavior, TouchableBehavior
from .i18n import get_txt


PosSizeCallable = Callable[[Widget, List[float]], Any]
BoundWidgetPropertyId = Tuple[Widget, str, int]
PropagatedAttributes = Tuple[Any, str, Optional[PosSizeCallable]]


ANI_SINE_DEEPER_REPEAT3 = \
    Animation(ani_value=0.99, t='in_out_sine', d=0.9) + Animation(ani_value=0.87, t='in_out_sine', d=1.2) + \
    Animation(ani_value=0.96, t='in_out_sine', d=1.5) + Animation(ani_value=0.75, t='in_out_sine', d=1.2) + \
    Animation(ani_value=0.90, t='in_out_sine', d=0.9) + Animation(ani_value=0.45, t='in_out_sine', d=0.6)
""" sine 3 x deeper repeating animation, used e.g. to animate help layout (see :class:`Tooltip` widget) """
ANI_SINE_DEEPER_REPEAT3.repeat = True

CRITICAL_VIBRATE_PATTERN = (0.00, 0.12, 0.12, 0.12, 0.12, 0.12,
                            0.12, 0.24, 0.12, 0.24, 0.12, 0.24,
                            0.12, 0.12, 0.12, 0.12, 0.12, 0.12)
""" very long/~2.4s vibrate pattern for critical error notification (sending SOS to the mobile world;) """

ERROR_VIBRATE_PATTERN = (0.0, 0.09, 0.09, 0.18, 0.18, 0.27, 0.18, 0.36, 0.27, 0.45)
""" long/~2s vibrate pattern for error notification. """

LOVE_VIBRATE_PATTERN = (0.0, 0.12, 0.12, 0.21, 0.03, 0.12, 0.12, 0.12)
""" short/~1.2s vibrate pattern for fun/love notification. """

MAIN_KV_FILE_NAME = 'main.kv'  #: default file name of the main kv file of your app


# load/declare base widgets with integrated app flow and observers ensuring change of app states (e.g. theme and size)
Builder.load_file(os.path.join(os.path.dirname(__file__), "widgets.kv"))


class AbsolutePosSizeBinder:                                                                        # pragma: no cover
    """ propagate changes of `pos`/`size` properties of one or more widgets plus their parents to attributes/callbacks.

    create an instance of this class passing the widget(s) to observe on change of their pos/size. then call the methods
    :meth:`pos_to_attribute`, :meth:`pos_to_callback`, :meth:`size_to_attribute` and :meth:`size_to_callback` to specify
    the propagation of the changed `pos` and/or `size`. to remove the change propagation call the method :meth:`unbind`.

    .. note:: the `pos` attribute/callback propagations are providing absolute window coordinates.
    """
    def __init__(self, *widgets: Widget, bind_window_size: bool = False):
        """ instantiate binder specifying the monitored widget(s).

        :param widgets:         widget(s) to observe changes of their `pos` and `size` properties. if specified more
                                than one widget then the pos/size coordinates of the rectangle that is enclosing all
                                specified widgets are propagated.
        :param bind_window_size: pass True to propagate pos and size changes if window size changes.
        """
        self.widgets = widgets
        self.relatives: List[Widget] = []
        self.main_app = App.get_running_app().main_app

        self._pos_attributes: List[PropagatedAttributes] = []
        self._size_attributes: List[PropagatedAttributes] = []
        self._pos_callbacks: List[PosSizeCallable] = []
        self._size_callbacks: List[PosSizeCallable] = []
        self._bound_wid_properties: List[BoundWidgetPropertyId] = []
        self._bound_rel_properties: List[BoundWidgetPropertyId] = []

        self._bind()
        if bind_window_size:
            uid = Window.fbind('size', self._rel_size_changed)
            self._bound_rel_properties.append((Window, 'size', uid))

    def _bind(self):
        for wid in self.widgets:
            uid = wid.fbind('pos', self._wid_pos_changed)
            self._bound_wid_properties.append((wid, 'pos', uid))

            uid = wid.fbind('size', self._wid_size_changed)
            self._bound_wid_properties.append((wid, 'size', uid))

            parent = wid
            while parent != (parent := parent.parent) and parent:
                if isinstance(parent, (ScrollView, RelativeLayout)) and parent not in self.relatives:
                    uid = parent.fbind('pos', self._rel_pos_changed)
                    self._bound_rel_properties.append((parent, 'pos', uid))

                    uid = parent.fbind('size', self._rel_size_changed)
                    self._bound_rel_properties.append((parent, 'size', uid))

                    self.relatives.append(parent)

    def _propagate(self, wid, value, attributes, callbacks):
        self.main_app.vpo(f"AbsolutePosSizeBinder._propagate({wid=}, {value=}, {attributes=}, {callbacks=})")

        for (target, attribute, converter) in attributes:
            setattr(target, attribute, converter(wid, value) if converter else value)

        for callback in callbacks:
            callback(wid, value)

    def _wid_pos_changed(self, wid: Widget, new_pos: List[float]):
        """ propagate `pos` property change to target attributes and subscribed observers.

        :param wid:             bound widget or a ScrollView that is embedding the bound widget, which pos changed.
        :param new_pos:         new position of the bound widget/ScrollView (unused).
        """
        wgs = self.widgets
        new_pos = self.main_app.widgets_enclosing_rectangle(wgs)[:2] if len(wgs) > 1 else wid.to_window(*new_pos)
        self._propagate(wid, new_pos, self._pos_attributes, self._pos_callbacks)

    def _wid_size_changed(self, wid: Widget, new_size: List[float]):
        """ propagate `size` property change to target attributes and subscribed observers.

        :param wid:             bound widget or a ScrollView that is embedding the bound widget, which pos changed.
        :param new_size:        new position of the bound widget/ScrollView (unused).
        """
        wgs = self.widgets
        if len(wgs) > 1:
            new_size = self.main_app.widgets_enclosing_rectangle(wgs)[2:]
        self._propagate(wid, new_size, self._size_attributes, self._size_callbacks)

    def _rel_pos_changed(self, _rel: Widget, _new_pos: list):
        """ propagate `pos` property change of relative/scrollable layout/container.

        :param _rel:            relative layout or a scroll view, embedding bound widget(s), which pos changed.
        :param _new_pos:        new position of the RelativeLayout/ScrollView (unused).
        """
        wid = self.widgets[0]
        self._wid_pos_changed(wid, wid.pos)

    def _rel_size_changed(self, _rel: Widget, _new_size: list):
        """ propagate size change of relative/scrollable layout/container.

        :param _rel:            relative layout or a scroll view, embedding bound widget(s), which size changed.
        :param _new_size:       new size of the RelativeLayout/ScrollView (unused).
        """
        wid = self.widgets[0]
        self._wid_size_changed(wid, wid.size)
        self._wid_pos_changed(wid, wid.pos)     # layout size change mostly does change also the absolute widget pos

    def pos_to_attribute(self, target: Any, attribute: str, converter: Optional[PosSizeCallable] = None):
        """ request the propagation of the changed (absolute) widget(s) position to an object attribute.

        :param target:          the object which attribute will be changed on change of `pos`.
        :param attribute:       the name of the attribute to assign the new/changed absolute position.
        :param converter:       optional pos value converter, returning the final value assigned to the attribute.
        """
        self._pos_attributes.append((target, attribute, converter))

    def pos_to_callback(self, callback: PosSizeCallable):
        """ bind callable to `pos` change event.

        :param callback:        callable to be called when pos changed with the changed widget and pos as arguments.
        """
        self._pos_callbacks.append(callback)

    def size_to_attribute(self, target: Any, attribute: str, converter: Optional[PosSizeCallable] = None):
        """ request the propagation of the changed widget(s) size to an object attribute.

        :param target:          the object which attribute will be changed on change of `size`.
        :param attribute:       the name of the attribute to assign the new/changed size.
        :param converter:       optional pos value converter, returning the final value assigned to the attribute.
        """
        self._size_attributes.append((target, attribute, converter))

    def size_to_callback(self, callback: PosSizeCallable):
        """ bind callable to `size` change event.

        :param callback:        callable to be called when size changed with the changed widget and size as arguments.
        """
        self._size_callbacks.append(callback)

    def unbind(self):
        """ unbind the widget(s) of this binder instance.

        .. note:: this instance can be destroyed after the call of this method. for new bindings create a new instance.
        """
        for (wid, prop, uid) in reversed(self._bound_rel_properties):
            wid.unbind_uid(prop, uid)
        self._bound_rel_properties.clear()

        for (wid, prop, uid) in reversed(self._bound_wid_properties):
            wid.unbind_uid(prop, uid)
        self._bound_wid_properties.clear()

        self.relatives = self._pos_attributes = self._size_attributes = self._pos_callbacks = self._size_callbacks = []
        self.widgets = ()


class AppStateSlider(HelpBehavior, ShadersMixin, Slider):                                           # pragma: no cover
    """ slider widget with help text to change app state value. """
    app_state_name = StringProperty()  #: name of the app state to be changed by this slider value

    def __str__(self):
        """ added for easier debugging. """
        return f"{self.__class__.__name__}({hex(id(self))} {self.app_state_name=} {self.value=})"

    def on_value(self, *args):
        """ value changed event handler.

        :param args:            tuple of instance and new value.
        """
        App.get_running_app().main_app.change_app_state(self.app_state_name, args[1])


class HelpToggler(ReliefCanvas, Image):                                                               # pragma: no cover
    """ widget to activate and deactivate the help mode.

    To prevent dismiss of opened popups and dropdowns at help mode activation, this singleton instance has to:

    * be registered in its __init__ to the :attr:`~ae.gui_help.HelpAppBase.help_activator` attribute and
    * have a :meth:`~HelpToggler.on_touch_down` method that is eating the activation touch event (returning True) and
    * a :meth:`~HelpToggler.on_touch_down` method not passing an activation touch in all DropDown/Popup widgets.

    """
    ani_value = NumericProperty(0.999)      #: float value (range: 0.0 - 1.0) to animate this button in help/tour mode

    def __init__(self, **kwargs):
        """ initialize an instance of this class and also :attr:`~ae.gui_help.HelpAppBase.help_activator`. """
        self.main_app = App.get_running_app().main_app
        self.main_app.help_activator = self
        super().__init__(**kwargs)

    def ani_start(self):
        """ start animation of this button. """
        ANI_SINE_DEEPER_REPEAT3.start(self)

    def ani_stop(self):
        """ stop animation of this button. """
        ANI_SINE_DEEPER_REPEAT3.stop(self)
        self.ani_value = 0.999

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ touch down event handler to toggle help mode while preventing dismiss of open dropdowns/popups.

        :param touch:           touch event.
        :return:                True if touch happened on this button (and will get no further processed => eaten).
        """
        if self.collide_point(*touch.pos):
            self.main_app.help_activation_toggle()
            return True
        return False


class ImageLabel(ReliefCanvas, ShadersMixin, Label):                                                # pragma: no cover
    """ base label used for all labels and buttons - declared in widgets.kv and also in this module to inherit from.

    .. note::
        hide-able label needs extra handling, because even setting width/height to zero the text can still be visible,
        especially in dark mode and even with having the text-color-alpha==0. to fully hide the texture in all cases,
        set either the text to an empty string or the opacity to zero.
    """
    def __repr__(self):
        """ added for easier debugging of :class:`FlowButton` and :class:`FlowToggler` widgets. """
        flo = f" {self.tap_flow_id=}" if hasattr(self, 'tap_flow_id') else ""
        return f"{self.__class__.__name__}({hex(id(self))}{flo} {self.text=})"


class FlowButton(HelpBehavior, SlideSelectBehavior, TouchableBehavior, ButtonBehavior, ImageLabel):  # pragma: no cover
    """ button to change the application flow. """
    long_tap_flow_id = StringProperty()     #: flow id that will be set when this button gets long tap event
    tap_flow_id = StringProperty()          #: the new flow id that will be set when this button get tapped
    tap_kwargs = ObjectProperty()           #: kwargs dict passed to event handler (change_flow) when button get tapped

    def __init__(self, **kwargs):
        ensure_tap_kwargs_refs(kwargs, self)
        super().__init__(**kwargs)

    def on_long_tap(self, touch: MotionEvent):
        """ long tap/click default handler.

        :param touch:           motion/touch event data with the touched widget in `touch.grab_current`.
        """
        super().on_long_tap(touch)
        if flow_id := self.long_tap_flow_id:
            self.main_app.change_flow(flow_id, **update_tap_kwargs(self, popup_kwargs={'touch_event': touch}))

    def on_release(self):
        """ overridable touch release event handler. """
        self.main_app.change_flow(self.tap_flow_id, **self.tap_kwargs)


class FlowDropDown(ContainerChildrenAutoWidthBehavior, DynamicChildrenBehavior, SlideSelectBehavior, ReliefCanvas,
                   DropDown):  # pragma: no cover
    """ flow based widget class to implement dynamic menu-like user selections and toolbars. """
    close_kwargs = DictProperty()
    """ kwargs passed to all close action flow change event handlers.

    :attr:`close_kwargs` is a :class:`~kivy.properties.DictProperty`. the default depends the action of the penultimate
    flow id in the :attr:`ae.gui_app.flow_path`: is empty or 'enter' dict then it defaults to an empty flow, else to an
    empty dict.
    """

    content = ObjectProperty()
    """ popup main content layout container, displayed as a child of the scrollable layout :attr:`container`.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty` and has to be specified either in the kv language
    as children or via the `content` kwarg.
    """

    menu_items = ObjectProperty()
    """ sequence of the container/content widgets, like buttons, text inputs, sliders or the close button.

    :attr:`menu_items` is an :class:`~kivy.properties.ObjectProperty` and includes by default the content widgets
    as well as the close button of this popup.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fw_app = App.get_running_app()

    def __repr__(self):
        """ added for easier debugging. """
        return f"{self.__class__.__name__}({hex(id(self))} {self.close_kwargs=})"

    def _real_dismiss(self, *_args):
        """ overridden to ensure that return value of on_dismiss-dispatch get recognized. """
        if self.dispatch('on_dismiss'):
            return      # dismiss/close cancelled
        if self.parent:
            self.parent.remove_widget(self)
        if self.attach_to:
            self.attach_to.unbind(pos=self._reposition, size=self._reposition)
            self.attach_to = None
        self._layout_finished = True

    def dismiss(self, *args):
        """ override DropDown method to prevent dismiss of any dropdown/popup while clicking on activator widget.

        :param args:            args to be passed to DropDown.dismiss().
        """
        if self.attach_to:
            help_layout = self.fw_app.help_layout
            if help_layout is None or not isinstance(help_layout.targeted_widget, HelpToggler):
                self._layout_finished = False
                super().dismiss(*args)

    close = dismiss

    def on_container(self, instance: Widget, value: Widget):
        """ sync :attr:`content` widget and :attr:`menu_items` list with container widget.

        :param instance:        self.
        :param value:           new/changed :attr:`~kivy.uix.dropdown.DropDown.container` widget.
        """
        super().on_container(instance, value)
        self.content = value     # value==self.container
        self.menu_items = self.content.children

    def on_dismiss(self) -> Optional[bool]:
        """ default dismiss/close default event handler.

        :return:                True to prevent/cancel the dismiss/close.
        """
        return not self.attach_to \
            or not self.main_app.change_flow(id_of_flow('close', 'flow_popup'), **self.close_kwargs)

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ prevent the processing of a touch on the help activator widget by this dropdown.

        :param touch:           motion/touch event data.
        :return:                True if event got processed/used.
        """
        if self.main_app.help_activator.collide_point(*touch.pos):
            return False  # allow help activator button to process this touch down event
        return super().on_touch_down(touch)

    def _reposition(self, *args):
        """ ensure animated small x coordinate displacement after reposition of the attach_to-widget/popup/dropdown. """
        super()._reposition(*args)
        if self._win and self.attach_to and self.attach_to.get_parent_window():
            Animation(x=min(self.x + sp(12), Window.width - self.width), t='in_out_sine', d=0.69).start(self)


class ExtTextInputCutCopyPaste(OriTextInputCutCopyPaste):  # pragma: no cover
    """ overwrite/extend :class:`kivy.uix.textinput.TextInputCutCopyPaste` w/ translatable and autocomplete options. """
    def __init__(self, **kwargs):
        """ create :class:`~kivy.uix.Bubble` instance to display the cut/copy/paste options.

        the monkey patch of :class:`~kivy.uix.textinput.TextInputCutCopyPaste` which was done in
        :meth:`FlowInput._show_cut_copy_paste` has to be temporarily reset before the super() call below, to prevent
        endless recursion because else the other super(cls, instance) call (in python2 style within
        :meth:`TextInputCutCopyPaste.__init__`) results in the same instance (instead of the overwritten instance).
        """
        kivy.uix.textinput.TextInputCutCopyPaste = OriTextInputCutCopyPaste
        self.fw_app = app = App.get_running_app()

        kwargs['arrow_image'] = app.main_app.img_file('bubble_arrow')
        super().__init__(**kwargs)

    def on_parent(self, instance: Widget, value: Widget):
        """ overwritten to translate BubbleButton texts and to add extra menus to add/delete ac texts.

        :param instance:        self.
        :param value:           kivy main window.
        """
        textinput = self.textinput
        self.fw_app.main_app.vpo(f"{self.__class__.__name__}.on_parent {instance=} {value=} {textinput=}")
        if not textinput:
            return                              # shortcut: not calling super().on_parent() because does only return too
        super().on_parent(instance, value)      # reset self.content.children

        font_size = self.fw_app.main_app.font_size
        cont = self.content

        for child in cont.children:
            child.font_size = font_size
            child.text = get_txt(child.text)

        if not textinput.readonly:
            # memorize/forget complete text to/from autocomplete because dropdown is not visible if this bubble is
            cont.add_widget(BubbleButton(text=get_txt("Memorize"), font_size=font_size,
                                         on_release=textinput.extend_ac_with_text))
            cont.add_widget(BubbleButton(text=get_txt("Forget"), font_size=font_size,
                                         on_release=textinput.delete_text_from_ac))

        # estimate container size (exact calc not possible because bubble button width/texture_size[0] is still 100/0)
        bub_w = bub_h = 0.0
        text_size_guess = self.fw_app.main_app.text_size_guess
        bub_padding = cont.padding[0] + cont.padding[2], cont.padding[1] + cont.padding[3]
        for bub in cont.children:
            width, height = text_size_guess(bub.text, padding=bub_padding)
            if width > bub_w:
                bub_w = width
            if height > bub_h:
                bub_h = height

        bub_w, bub_h = 2.1 * cont.spacing + bub_w, 2.1 * cont.spacing + 1.5 * bub_h
        if self.fw_app.landscape:
            width = cont.padding[0] + cont.padding[2] + len(cont.children) * bub_w
            height = cont.padding[1] + cont.padding[3] + bub_h
        else:
            width = cont.padding[0] + cont.padding[2] + bub_w
            height = cont.padding[1] + cont.padding[3] + len(cont.children) * bub_h
        self.size = width, height   # pylint: disable=attribute-defined-outside-init # false positive


class FlowInput(HelpBehavior, ShadersMixin, ReliefCanvas, TextInput):  # pragma: no cover
    """ text input/edit widget with optional autocompletion.

    until version 0.1.43 of this portion the background and text color of :class:`FlowInput` did automatically
    get switched by a change of the light_theme app state. now all colors left unchanged (before only the ones
    with <unchanged>)::

    * background_color: Window.clearcolor            # default: 1, 1, 1, 1
    * cursor_color: app.font_color                   # default: 1, 0, 0, 1
    * disabled_foreground_color: <unchanged>         # default: 0, 0, 0, .5
    * foreground_color: app.font_color               # default: 0, 0, 0, 1
    * hint_text_color: <unchanged>                   # default: 0.5, 0.5, 0.5, 1.0
    * selection_color: <unchanged>                   # default: 0.1843, 0.6549, 0.8313, .5

   to implement a dark background for the dark theme we would need also to change the images in the properties:
    background_active, background_disabled_normal and self.background_normal.

    the images/colors of the bubble that is showing e.g. on long press of the TextInput widget (cut/copy/paste/...)
    kept unchanged - only the font_size get adapted and the bubble button texts get translated. for that the class
    :class:`ExtTextInputCutCopyPaste` provided by this portion inherits from the original bubble class
    :class:`~kivy.uix.textinput.TextInputCutCopyPaste`.

    the original bubble class is getting monkey patched shortly/temporarily in the moment of the instantiation to
    translate the bubble menu options, change the font sizes and add additional menu options to memorize/forget
    auto-completion texts.
    """
    focus_flow_id = StringProperty()        #: flow id that will be set when this widget get focus
    unfocus_flow_id = StringProperty()      #: flow id that will be set when this widget lost focus

    auto_complete_texts: List[str] = ListProperty()  #: list of autocompletion texts
    auto_complete_selector_index_ink: ColorOrInk = ListProperty([0.69, 0.69, 0.69, 1])
    """ color and alpha used to highlight the currently selected text of all matching autocompletion texts """

    _ac_dropdown: Any = None                #: singleton FlowDropDown instance for all TextInput instances
    _matching_ac_texts: List[str] = []      #: one list instance for all TextInput instances is enough
    _matching_ac_index: int = 0             #: index of selected text in the dropdown matching texts list

    def __init__(self, **kwargs):
        # changed to kivy properties so no need to pop them from kwargs:
        # self.auto_complete_texts = kwargs.pop('auto_complete_texts', [])
        # self.auto_complete_selector_index_ink = kwargs.pop('auto_complete_selector_index_ink', [0.69, 0.69, 0.69, 1.])

        self.main_app = App.get_running_app().main_app

        super().__init__(**kwargs)

        if not FlowInput._ac_dropdown:
            FlowInput._ac_dropdown = FlowDropDown()  # widget instances cannot be created in class var declaration

    def __repr__(self):
        """ added for easier debugging. """
        return f"{self.__class__.__name__}({hex(id(self))} {self.focus_flow_id=} {self.unfocus_flow_id=} {self.text=})"

    def _change_selector_index(self, delta: int):
        """ change/update/set the index of the matching texts in the opened autocompletion dropdown.

        :param delta:           index delta value between old and new index (e.g. pass +1 to increment index).
                                set index to zero if the old/last index was on the last item in the matching list.
        """
        cnt = len(self._matching_ac_texts)
        if cnt:
            chi = self._ac_dropdown.container.children[::-1]
            idx = self._matching_ac_index
            chi[idx].square_fill_ink = Window.clearcolor
            self._matching_ac_index = (idx + delta + cnt) % cnt
            chi[self._matching_ac_index].square_fill_ink = self.auto_complete_selector_index_ink

    def _delete_ac_text(self, ac_text: str = ""):
        if not ac_text and self._matching_ac_texts:
            ac_text = self._matching_ac_texts[self._matching_ac_index]
        if ac_text in self.auto_complete_texts:
            self.auto_complete_texts.remove(ac_text)
            self.on_text(self, self.text)   # redraw autocompletion dropdown

    def delete_text_from_ac(self, *_args):
        """ check if current text is in autocompletion list and if yes then remove it.

        called by FlowInput kbd event handler and from menu button added by ExtTextInputCutCopyPaste.on_parent().

        :param _args:           unused event args.
        """
        self._delete_ac_text(self.text)

    def extend_ac_with_text(self, *_args):
        """ add non-empty text to autocompletion texts.

        :param _args:           unused event args.
        """
        if self.text:
            self.auto_complete_texts.insert(0, self.text)

    def keyboard_on_key_down(self, window: Any, keycode: Tuple[int, str], text: str, modifiers: List[str]) -> bool:
        """ overwritten TextInput/FocusBehavior kbd event handler.

        :param window:          keyboard window.
        :param keycode:         pressed key as tuple of (numeric key code, key name string).
        :param text:            pressed key value string.
        :param modifiers:       list of modifier keys (pressed or locked like numlock and capslock).
        :return:                True if key event get processed/used by this method.
        """
        self.main_app.vpo(f"{self}.keyboard_on_key_down {modifiers=} {keycode=} {text=}")
        key_name = keycode[1]

        if self._ac_dropdown.attach_to:
            if key_name in ('enter', 'right') and len(self._matching_ac_texts) > self._matching_ac_index:
                # suggestion_text will be removed in Kivy 2.1.0 - see PR #7437
                # self.suggestion_text = ""
                self.text = self._matching_ac_texts[self._matching_ac_index]    # pylint: disable=W0201
                self._ac_dropdown.close()
                return True

            if key_name == 'down':
                self._change_selector_index(1)
            elif key_name == 'up':
                self._change_selector_index(-1)
            elif key_name == 'delete' and 'ctrl' in modifiers:
                self._delete_ac_text()

        if key_name == 'insert' and 'ctrl' in modifiers:
            self.extend_ac_with_text()
        elif key_name == 'enter':                                           # and isinstance(self, FlowInput):
            parent = self           # check if self.parent,parent.parent.parent is InputShowPopup
            while parent != (parent := parent.parent) and parent:
                if getattr(parent, 'enter_confirms', False):                # and isinstance(parent, InputShowPopup):
                    btn_map = parent.query_data_maps[0]['kwargs']
                    tap_flow_id, tap_kwargs = btn_map['tap_flow_id'], btn_map['tap_kwargs']
                    self.main_app.change_flow(tap_flow_id, **tap_kwargs)
                    return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)

    def keyboard_on_textinput(self, window: Window, text: str):
        """ overridden to suppress any user input if tour is running/active. """
        if not self.main_app.tour_layout:
            super().keyboard_on_textinput(window, text)

    def on_focus(self, _self: Widget, focus: bool):
        """ change flow on text input change of focus.

        :param _self:           unused dup ref to self.
        :param focus:           True if this text input got focus, False on unfocus.
        """
        flow_id = self.focus_flow_id if focus else self.unfocus_flow_id
        self.main_app.vpo(f"{self}.on_focus {focus=} --> {flow_id=}")
        if flow_id:
            self.main_app.change_flow(flow_id)

    def on_text(self, _self: Widget, text: str):
        """ TextInput.text change event handler.

        :param _self:           unneeded duplicate reference to TextInput/self.
        :param text:            new/current text property value.
        """
        if text:
            matching = [txt for txt in self.auto_complete_texts if txt[:-1].startswith(text)]
        else:
            matching = []
        self._matching_ac_texts[:] = matching
        self._matching_ac_index = 0

        if matching:
            cdm = []
            for txt in matching:
                cdm.append({'cls': 'FlowButton', 'kwargs': {'text': txt, 'on_release': self._select_ac_text}})
            self._ac_dropdown.child_data_maps[:] = cdm
            if not self._ac_dropdown.attach_to:
                self.main_app.change_flow(replace_flow_action(self.focus_flow_id, 'suggest'))
                self._ac_dropdown.open(self)
            self._change_selector_index(0)
        elif self._ac_dropdown.attach_to:
            self._ac_dropdown.close()

    def _select_ac_text(self, selector: Widget):
        """ put selected autocompletion text into text input and close _ac_dropdown """
        self.text = selector.text                                           # pylint: disable=W0201
        self._ac_dropdown.close()

    def _show_cut_copy_paste(self, *args, **kwargs):    # pylint: disable=signature-differs
        self.main_app.vpo(f"FlowInput._show_cut_copy_paste {args=} {kwargs=}")
        # monkey-patch kivy's built-in cut/copy/paste popup, will be reset also in ExtTextInputCutCopyPaste.__init_
        kivy.uix.textinput.TextInputCutCopyPaste = ExtTextInputCutCopyPaste

        if 'pos_in_window' not in kwargs and kwargs.get('mode') == 'paste':
            kwargs['pos_in_window'] = True              # ensure correct pos in long_touch/paste mode
        super()._show_cut_copy_paste(*args, **kwargs)

        kivy.uix.textinput.TextInputCutCopyPaste = OriTextInputCutCopyPaste


class PopupQueryBox(DynamicChildrenBehavior, StackLayout):                                          # pragma: no cover
    """ container used by :class:`~ae.kivy.widgets.FlowPopup` to display dynamically created button/input widgets. """
    def close(self, *args, **kwargs):
        """ forward close/dismiss to parent FlowPopup instance for popups_to_close-'replace_with_data_map_popup' refs

        :param args:            forwarded arguments (providing compatible signature for DropDown/Popup/ModalView/...).
        :param kwargs:          forwarded keyword arguments (compatible signature for DropDown/Popup/ModalView/...).
        """
        parent = self           # check if self.parent,parent.parent.parent is FlowPopup
        while parent != (parent := parent.parent) and parent:
            if isinstance(parent, FlowPopup):
                parent.close(*args, **kwargs)

    dismiss = close     #: alias method of :meth:`~PopupQueryBox.close`


class FlowPopup(ModalBehavior, DynamicChildrenBehavior, SlideSelectBehavior, ReliefCanvas,
                BoxLayout):  # pragma: no cover
    """ popup for dynamic and auto-sizing dialogs and other top-most or modal windows.

    the scrollable :attr:`container` (a :class:`~kivy.uix.scrollview.ScrollView` instance) can only have one child,
    referenced by the :attr:`content` attribute, which can be any widget (e.g. a label). use a layout for
    :attr:`content` to display multiple widgets. set :attr:`optimal_content_width` and/or
    :attr:`optimal_content_height` to make the popup size as small as possible, using e.g. `minimum_width`
    respectively `minimum_height` if :attr:`content` is a layout that is providing and updating this property, or
    :meth:`~KivyMainApp.text_size_guess` if it is a label or button widget.

    .. hint::
        :attr:`~kivy.uix.label.Label.texture_size` could provide a more accurate size than
        :meth:`~~ae.kivy.apps.KivyMainApp.text_size_guess`, but should be used with care to prevent recursive
        property change loops.

    this class is very simular to :class:`~kivy.uix.popup.Popup` and can be used as replacement, incompatible are
    the following attributes of :class:`~kivy.uix.popup.Popup` and :class:`~kivy.uix.modalview.ModalView`:

        * :attr:`~kivy.uix.modalview.ModalView.background`: FlowPopup has no :class:`BorderImage`.
        * :attr:`~kivy.uix.modalview.ModalView.border`: FlowPopup is using a :class:`RoundedRectangle`.
        * :attr:`~kivy.uix.popup.Popup.title_align`: is 'center' and could be changed via the `title_bar` id.
        * :attr:`~kivy.uix.popup.Popup.title_color` is the `app.font_color`.
        * :attr:`~kivy.uix.popup.Popup.title_font` is the default font.
        * :attr:`~kivy.uix.popup.Popup.title_size` is the default button height
          (:attr:`~ae.kivy.apps.FrameworkApp.button_height`).

    :Events:
        `on_pre_open`:
            fired before the FlowPopup is opened and got added to the main window.
        `on_open`:
            fired when the FlowPopup is opened.
        `on_pre_dismiss`:
            fired before the FlowPopup is closed.
        `on_dismiss`:
            fired when the FlowPopup is closed. if the callback returns True, the popup will stay opened.

    """

    background_color = ColorProperty()
    """ background ink tuple in the format (red, green, blue, alpha).

    the :attr:`background_color` is a :class:`~kivy.properties.ColorProperty` and defaults to
    :attr:`~kivy.core.window.Window.clearcolor`.
    """

    close_kwargs = DictProperty()
    """ kwargs passed to all close action flow change event handlers.

    :attr:`close_kwargs` is a :class:`~kivy.properties.DictProperty`. the default depends the action of the penultimate
    flow id in the :attr:`ae.gui_app.flow_path`: is empty or 'enter' dict then it defaults to an empty flow, else to an
    empty dict.
    """

    container = ObjectProperty()
    """ popup scrollable layout underneath the title bar and the parent of the :attr:`content` container.

    :attr:`container` is an :class:`~kivy.properties.ObjectProperty` and is read-only.
    """

    content = ObjectProperty()
    """ popup main content container, displayed as a child of the scrollable layout :attr:`container`.

    :attr:`content` is an :class:`~kivy.properties.ObjectProperty` and has to be specified either in the kv language
    as children or via the `content` kwarg.
    """

    menu_items = ObjectProperty()
    """ sequence of the content widgets and close button.

    :attr:`menu_items` is an :class:`~kivy.properties.ObjectProperty` and includes by default the content widgets
    as well as the close button of this popup.
    """

    optimal_content_width = NumericProperty()
    """ width of the content to be fully displayed/visible.

    :attr:`optimal_content_width` is a :class:`~kivy.properties.NumericProperty`. if `0` or `None` or not explicitly
    set then it defaults to the main window width and - in landscape orientation - minus the :attr:`side_spacing` and
    the width needed by the :attr:`query_data_maps` widgets.
    """

    optimal_content_height = NumericProperty()
    """ height of the content to be fully displayed/visible.

    :attr:`optimal_content_height` is a :class:`~kivy.properties.NumericProperty`. if `0` or `None` or not explicitly
    set then it defaults to the main window height minus the height of :attr:`title` and - in portrait orientation -
    minus the :attr:`side_spacing` and the height needed by the :attr:`query_data_maps` widgets.
    """

    overlay_color = ColorProperty()
    """ ink (color + alpha) tuple in the format (red, green, blue, alpha) used for dimming of the main window.

    :attr:`overlay_color` is a :class:`~kivy.properties.ColorProperty` and defaults to the current color value
    :attr:`~kivy.core.window.Window.clearcolor` with an alpha of 0.6 (set in :meth:`.__init__`).
    """

    query_data_maps: List[Dict[str, Any]] = ListProperty()
    """ list of child data dicts to instantiate the query widgets (most likely :class:`FlowButton`) of this popup.

    :attr:`query_data_maps` is a :class:`~kivy.properties.ListProperty` and defaults to an empty list.
    """

    separator_color = ColorProperty()
    """ color used by the separator between title and the content-/container-layout.

    :attr:`separator_color` is a :class:`~kivy.properties.ColorProperty` and defaults to the current value of the
    :attr:`~FrameworkApp.font_color` property.
    """

    separator_height = NumericProperty('3sp')
    """ height of the separator.

    :attr:`separator_height` is a :class:`~kivy.properties.NumericProperty` and defaults to 3sp.
    """

    side_spacing = NumericProperty('192sp')
    """ padding in pixels from Window.width in landscape-orientation, and from Window.height in portrait-orientation.

    :attr:`side_spacing` is a :class:`~kivy.properties.NumericProperty` and defaults to 192sp.
    """

    title = StringProperty("")
    """ title string of the popup.

    :attr:`title` is a :class:`~kivy.properties.StringProperty` and defaults to an empty string.
    """

    _anim_alpha = NumericProperty()                         #: internal opacity/alpha for fade-in/-out animations
    _anim_duration = NumericProperty(.3)                    #: internal time in seconds for fade-in/-out animations
    _max_height = NumericProperty()                         #: popup max height (calculated from Window/side_spacing)
    _max_width = NumericProperty()                          #: popup max width (calculated from Window/side_spacing)

    __events__ = ('on_pre_open', 'on_open', 'on_pre_dismiss', 'on_dismiss')

    def __init__(self, **kwargs):
        self.fw_app = app = App.get_running_app()
        clr_ink = Window.clearcolor
        self.background_color = clr_ink
        self.overlay_color = clr_ink[:3] + [0.69]
        self.relief_square_outer_colors = relief_colors(app.font_color)
        # noinspection PyTypeChecker
        self.relief_square_outer_lines = sp(9)
        self.separator_color = app.font_color
        self.close_with_cancel = False

        super().__init__(**kwargs)

    def __repr__(self):
        """ added for easier debugging. """
        return f"{self.__class__.__name__}({hex(id(self))} {self.close_kwargs=})"

    def add_widget(self, widget: Widget, index: int = 0, canvas: Optional[str] = None):
        """ add container and content widgets.

        first call set container from kv rule, 2nd the content, 3rd raise error.

        :param widget:          widget instance to be added.
        :param index:           index kwarg of :meth:`kivy.uix.widget.Widget`.
        :param canvas:          canvas kwarg of :meth:`kivy.uix.widget.Widget`.
        """
        if self.container:      # None until FlowPopup kv rule in widgets.kv is fully built (before user kv rule build)
            if self.content:
                raise ValueError("FlowPopup has already a children, set via this method, kv or the content property")
            self.main_app.vpo(f"FlowPopup: add content {widget=} to {self.container=}; {index=} {canvas=}")
            self.container.add_widget(widget, index=index)  # ScrollView.add_widget does not have canvas parameter
            self.content = widget
            self.menu_items = widget.children + [self.ids.title_bar]
        else:
            self.main_app.vpo(f"FlowPopup: add container {widget=} from internal kv rule {index=} {canvas=}")
            super().add_widget(widget, index=index, canvas=canvas)

    def close(self, *args, **kwargs):
        """ close/dismiss container/layout (ae.gui_app popup handling compatibility for all GUI frameworks).

        .. note:: prevents close/dismiss of any dropdown/popup while clicking on help activator widget.

        :param args:            arguments (providing compatible signature for DropDown/Popup/ModalView/ModalBehavior).
                                some like ModalBehavior passing the MotionEvent of the closing touch event.
        :param kwargs:          keyword arguments (compatible signature for DropDown/Popup/ModalView/ModalBehavior).
        """
        self.main_app.vpo(f"FlowPopup.close {args=} {kwargs=} {self.is_modal=}")
        if not self.is_modal:
            return

        help_layout = self.fw_app.help_layout
        if help_layout and isinstance(help_layout.targeted_widget, HelpToggler):
            return

        self.dispatch('on_pre_dismiss')

        if not self.dispatch('on_dismiss') or kwargs.get('force', False):
            if kwargs.get('animation', True):
                self._layout_finished = False
                Animation(_anim_alpha=0.0, d=self._anim_duration).start(self)
            else:
                self._anim_alpha = 0.0
                self.deactivate_esc_key_close()
                self.deactivate_modal()

    dismiss = close     #: alias method of :meth:`~FlowPopup.close`

    def on__anim_alpha(self, _instance: Widget, value: float):
        """ _anim_alpha changed event handler. """
        if value == 0.0 and self.is_modal:
            self.deactivate_esc_key_close()
            self.deactivate_modal()
            self._layout_finished = True

    def on_content(self, _instance: Widget, value: Widget):
        """ optional single widget (to be added to the container layout) set directly or via FlowPopup kwargs. """
        self.main_app.vpo(f"FlowPopup.on_content adding content {value=} to {self.container=}")
        self.container.clear_widgets()
        self.container.add_widget(value)

    def on_dismiss(self) -> Optional[bool]:
        """ default dismiss/close event handler.

        :return:                return True to prevent/cancel the dismiss/close.
        """
        return not self.is_modal \
            or not self.main_app.change_flow(id_of_flow('close', 'flow_popup'), **self.close_kwargs)

    def on_open(self):
        """ open default event handler. """

    def on_pre_dismiss(self):
        """ pre close/dismiss event handler. """

    def on_pre_open(self):
        """ pre open default event handler. """

    def on_touch_up(self, touch: MotionEvent) -> bool:
        """ touch up event handler. """
        xt, yt = self.to_local(*touch.pos)
        xw, yw = self.ids.title_bar.image_pos   # cancel 'button' widget (the Image within :class:`ImageLabel`) pos
        w, h = self.ids.title_bar.image_size
        self.close_with_cancel = xw <= xt <= xw + w and yw <= yt <= yw + h
        return super().on_touch_up(touch)

    def open(self, *_args, **kwargs):
        """ start optional open animation after calling open method if exists in inheriting container/layout widget.

        :param _args:           unused argument (to have compatible signature for Popup/ModalView and DropDown
                                widgets passing the parent widget).
        :param kwargs:          optional arguments:

                                * 'animation': `False` will disable the fade-in-animation (default=True).
        """
        app = self.fw_app
        if not self.optimal_content_width:
            self.optimal_content_width = self._max_width * (0.69 if self.query_data_maps and app.landscape else 1.0)
        if not self.optimal_content_height:
            self.optimal_content_height = self._max_height \
                - (app.button_height + self.ids.title_bar.padding[1] * 2 if self.title else 0.0) \
                - (len(self.query_data_maps) * app.button_height if not app.landscape else 0.0)
        self.center = Window.center

        self.dispatch('on_pre_open')
        self.activate_esc_key_close()
        self.activate_modal()
        if kwargs.get('animation', True):
            ani = Animation(_anim_alpha=1.0, d=self._anim_duration)
            ani.bind(on_complete=lambda *_args: self.dispatch('on_open'))
            ani.start(self)
        else:
            self._anim_alpha = 1.0
            self.dispatch('on_open')


class FlowSelector(ModalBehavior, DynamicChildrenBehavior, FlowButton):                   # pragma: no cover
    """ attachable popup used for dynamic elliptic auto-spreading menus and toolbars.

    this app flow based menu-like popup consists of a central button and animated elliptic-auto-spreading menu items.

    any widget class can be used for the menu items of this class, although the ShortenedButton widget
    instances are best-prepared to auto-shorten the `text` property.

    :Events:
        `on_pre_open`:
            fired before the FlowSelector is opened and got added to the main window.
        `on_open`:
            fired when the FlowSelector is opened.
        `on_pre_dismiss`:
            fired before the FlowSelector is closed.
        `on_dismiss`:
            fired when the FlowSelector is closed. if the callback returns True, the menu will stay opened.

    inspired by https://github.com/kivy-garden/garden.modernmenu
    """
    attached_widget = ObjectProperty(allownone=True)
    """ widget from which this instance got opened.

    The :meth:`open` method will automatically set this property whilst
    :meth:`close` will set it back to None.
    """

    close_kwargs = DictProperty()
    """ kwargs passed to all close action flow change event handlers.

    :attr:`close_kwargs` is a :class:`~kivy.properties.DictProperty`. the default depends the action of the penultimate
    flow id in the :attr:`ae.gui_app.flow_path`: is empty or 'enter' dict then it defaults to an empty flow, else to an
    empty dict.
    """

    container = ObjectProperty()
    """ parent widget of the menu items (for compatibility with other popups/dropdowns).

    :attr:`container` is an :class:`~kivy.properties.ObjectProperty` and is read-only.
    """

    is_open = BooleanProperty(defaultvalue=False)
    """ `True` if the :meth:`.open` method of this instance got called. :meth:`.close` sets this value to `False`.

    :attr:`is_open` is a :class:`~kivy.properties.BooleanProperty` and defaults to False.
    """

    menu_items = ListProperty()
    """ sequence of the menu items widgets (for compatibility with :class:`~ae.kivy.behaviors.SlideSelectBehavior`).

    :attr:`menu_items` is an :class:`~kivy.properties.ListProperty` and defaults to the items specified via
    the :attr:`~ae.kivy_dyn_chi.DynamicChildrenBehavior.child_data_maps` property and the kv language.
    """

    overlay_color = ColorProperty()
    """ ink (color + alpha) tuple in the format (red, green, blue, alpha) used for dimming of the main window.

    :attr:`overlay_color` is a :class:`~kivy.properties.ColorProperty` and defaults to the current color value
    :attr:`~kivy.core.window.Window.clearcolor` with an alpha of 0.6 (set in :meth:`.__init__`).
    """

    radian_offset = NumericProperty(tau * 9.0 / 360.0)
    """ start/end angle offset (in radians) for the elliptically positioned items of an elliptic menu.

    :attr:`radian_offset` is a :class:`~kivy.properties.NumericProperty` and defaults to 9 degrees (as radian,
    respectively ``tau * 9.0 / 360.0``).
    """

    separator_color = ColorProperty()
    """ color used to draw the border of the menu-back-button.

    :attr:`separator_color` is a :class:`~kivy.properties.ColorProperty` and defaults to the current value of the
    :attr:`~FrameworkApp.font_color` property.
    """

    separator_height = NumericProperty('1sp')
    """ line width of the border of the menu-back-button and of the connectors between the menu and its items.

    :attr:`separator_height` is a :class:`~kivy.properties.NumericProperty` and defaults to 1sp.
    """

    scale_x = NumericProperty(1.0)
    """ spread/widen factor of the menu item ellipse in x direction.

    :attr:`scale_x` is a :class:`~kivy.properties.NumericProperty` and defaults to 1.0.
    """

    scale_y = NumericProperty(1.0)
    """ spread/widen factor of the menu item ellipse in y direction.

    :attr:`scale_y` is a :class:`~kivy.properties.NumericProperty` and defaults to 1.0.
    """

    _anim_alpha = NumericProperty(0.0)                      #: internal opacity/alpha for fade-in/-out animations
    _anim_duration = NumericProperty(0.69)                  #: internal time in seconds for fade-in/-out animations

    _creation_direction = 1.0                               #: creation-ellipse-direction of the menu buttons/items
    _start_radian = 0.0                                     #: angle of the first menu item
    _item_radian = 0.0                                      #: angle of each menu item

    __events__ = ('on_pre_open', 'on_open', 'on_pre_dismiss', 'on_dismiss')

    def __init__(self, **kwargs):
        self._attached_wid_pos = ()     # x/y of attached widget in widget coordinates
        self._attached_binder = None

        if ini_touch := kwargs.pop('touch_event', None):
            ini_touch.grab(self)
            self._attached_touch_pos = ini_touch.pos    # x/y of initial touch in window coordinates
            self._ini_touch = ini_touch
            self._touch_started_inside = True  # for :meth:`ae.kivy.behaviors.ModalBehavior.on_touch_move` slide_select
        else:
            self._attached_touch_pos = []
            self._ini_touch = None

        # set default width and colors
        self.width = self.height * 2.1
        clr_ink = Window.clearcolor
        self.overlay_color = clr_ink[:3] + [0.69]
        self.fw_app = app = App.get_running_app()   # self.main_app get initialized in SlideSelectBehavior.__init__()
        self.separator_color = app.font_color

        self.container = self
        self.button_image = None
        self.menu_items = []

        super().__init__(**kwargs)

    def _attached_pos(self, widget: Widget, _pos: List[float]):     # assert widget.pos == _pos
        wid_x, wid_y = widget.to_window(*widget.pos)
        wid_r, wid_t = widget.to_window(widget.right, widget.top)
        delta_x, delta_y = widget.x - self._attached_wid_pos[0], widget.y - self._attached_wid_pos[1]
        mnu_center_x, mnu_center_y = self.center_x + delta_x, self.center_y + delta_y

        if self.x + delta_x < 0 or mnu_center_x < wid_x:
            mnu_center_x = max(self.width, wid_x + wid_r) / 2.0
        elif self.right + delta_x > Window.width or mnu_center_x > wid_r:
            mnu_center_x = min(Window.width - self.width / 2, wid_r)
        if self.y + delta_y < 0 or mnu_center_y < wid_y:
            mnu_center_y = max(self.height, wid_y + wid_t) / 2.0
        elif self.top + delta_y > Window.height or mnu_center_y > wid_t:
            mnu_center_y = min(Window.height - self.height / 2, wid_t)

        self.center = [mnu_center_x, mnu_center_y]
        self._attached_touch_pos = self.center
        self._attached_wid_pos = widget.pos

        self._layout_items()

    def _attached_size(self, widget: Widget, _size: List[float]):
        wid_x, wid_y = widget.to_window(*widget.pos)  # assert widget is self.attached_widget and widget.size == _size
        wid_r, wid_t = widget.to_window(widget.right, widget.top)
        self.center = [min(max(wid_x, self.center_x), wid_r), min(max(wid_y, self.center_y), wid_t)]
        self._layout_items()

    def _finalize_close(self, *_args):
        """ final real dismiss after animations are finished. """
        if self._ini_touch:
            self._ini_touch.ungrab(self)
            self._ini_touch = None

        if self._attached_binder:
            self.deactivate_modal()
            self._attached_binder.unbind()
            self._attached_binder = None
            if isinstance(self.attached_widget, ToggleButtonBehavior):
                self.attached_widget.state = 'normal'   # reset Toggler for option/toolbox dropdowns
            self.attached_widget = None

        self.unbind(menu_items=self._layout_items)

    def _item_moved(self, _anim: Animation, item: Widget, progress: float):
        """ draw line from menu-center to animated item-center. """
        center_x, center_y = self.center
        item_dis = item.menu_distance * 0.81 * progress
        item_radian = item.menu_radian * progress
        item_group = str(item.child_index)
        vis_val = abs((progress - 0.5) * 2)

        self.canvas.before.remove_group(item_group)
        with self.canvas.before:
            Color(rgba=self.separator_color[:3] + [self.separator_color[3] * vis_val],
                  group=item_group)
            dis = ellipse_polar_radius(self.width / 2, self.height / 2, item_radian)
            Line(points=(round(center_x + cos(item_radian) * dis),
                         round(center_y + sin(item_radian) * dis),
                         round(center_x + cos(item_radian) * item_dis),
                         round(center_y + sin(item_radian) * item_dis)),
                 # width=0.003 + vis_val * self.separator_height,
                 dash_length=3, dash_offset=3,     # only works if width == 1.0 (default and is faster)
                 group=item_group)

    def _layout_items(self, *_args):
        """ calculate the radians/angles and positions of the menu-items.

        given an offset angle of 9 degrees the (start-angle direction menu-item-angle) for the 9 block regions from
        top-left ... center/middle ... bottom-right would be:

        .. list-table:: possibly blocked window regions
            :widths: 12 9 9 9
            :header-rows: 1
            :stub-columns: 1
            :align: right

            * -
              - left
              - center
              - right
            * - top
              - 0  -72
              - 180+180
              - 180 +72
            * - middle
              - 81-162
              - 90+360
              - 99+162
            * - bottom
              - 72 -72
              - 180-180
              - 108 +72

        """
        self._layout_finished = False

        mnu_chi = self.menu_items  # assert set(self.container.children) == set(self.menu_items + [self.button_image])
        item_cnt = len(mnu_chi)
        if not item_cnt:
            return

        win_w, win_h = Window.width, Window.height
        mnu_w, mnu_h = self.width, self.height
        chi_w, chi_h = max(_.width for _ in mnu_chi), max(_.height for _ in mnu_chi)
        avl_r, avl_t, avl_l, avl_b = available = win_w - self.right, win_h - self.top, self.x, self.y
        sca_x, sca_y, shr_x, shr_y = self.scale_x, self.scale_y, 1.0, 1.0    # user scale and shrinking factors

        def _size_space(blk_cnt: int = 2):
            siz = (mnu_w + chi_w * sca_x * shr_x * item_cnt * 0.3,
                   mnu_h + chi_h * sca_y * shr_y * item_cnt / (2 ** (2 - min(blk_cnt, 2))))
            spa = [_space - siz[_idx % 2] for _idx, _space in enumerate(available)]
            blk = [_space < 0.0 for _space in spa]
            return siz, spa, blk, sum(blk)

        mnu_size, spaces, (blk_r, blk_t, blk_l, blk_b), block_cnt = _size_space()
        tries = 3
        while tries and ((shrink_x := blk_r and blk_l) + (shrink_y := blk_t and blk_b)):
            if shrink_x:
                shr_x = tries * 0.33
            if shrink_y:
                shr_y = tries * 0.33
            mnu_size, spaces, (blk_r, blk_t, blk_l, blk_b), block_cnt = _size_space(block_cnt)
            tries -= 1
        if blk_r and blk_l:
            if spaces[0] > spaces[2]:
                blk_r = False
            else:
                blk_l = False
            block_cnt -= 1
        if blk_t and blk_b:
            if spaces[1] > spaces[3]:
                blk_t = False
            else:
                blk_b = False
            block_cnt -= 1

        self._creation_direction = -1.0 if blk_l or blk_b and not blk_r else 1.0

        ell_x, ell_y = mnu_size
        if blk_l and blk_t:
            add_rad = max(0.0, atan(avl_t / ell_x))
            self._start_radian = add_rad                                        # 0º
            add_rad += max(0.0, atan((avl_l - ell_x / 2.0) * 2.0 / ell_y))
        elif blk_t or blk_b and not blk_r and not blk_l:
            add_rad = atan((avl_t if blk_t else avl_b) / ell_x)
            self._start_radian = pi + add_rad * (-1.0 if blk_t else 1.0)        # 180º
            add_rad *= 2.0 / block_cnt
        elif block_cnt == 2:
            add_rad = max(0.0, atan(((avl_r if blk_r else avl_l) - ell_x / 2.0) * 2.0 / ell_y))
            self._start_radian = pi / 2.0 + add_rad * (-1.0 if blk_r else 1.0)  # 90º (+90º)
            add_rad += max(0.0, atan((avl_t if blk_t else avl_b) / ell_x))
        elif block_cnt == 1:
            add_rad = max(0.0, atan(((avl_r if blk_r else avl_l) - ell_x / 2.0) * 2.0 / ell_y))
            self._start_radian = pi / 2.0 + add_rad * (-1.0 if blk_r else 1.0)  # 90º (+180º)
            add_rad = abs(add_rad) * 2.0
        else:
            self._start_radian = pi / 2.0                                       # 90º (+360º)
            add_rad = 0.0
        if not blk_t and (blk_l or blk_r) or not block_cnt:
            self._start_radian += (1 + blk_b) * self.radian_offset * self._creation_direction

        radian = add_rad + tau / (2 ** block_cnt)
        if blk_l or blk_r:
            radian -= self.radian_offset * 2.0
        self._item_radian = radian * self._creation_direction / max(1, item_cnt - (1 if block_cnt else 0))

        dur = self._anim_duration / 2
        center_x, center_y = self.center
        pre_coord = {}
        for idx, item in enumerate(mnu_chi):                                # assert idx == item.child_index
            radian = self._start_radian + self._item_radian * idx
            distance = ellipse_polar_radius(ell_x, ell_y, radian)
            width, height = item.size
            pos_x = round(center_x + cos(radian) * distance - width / 2)
            pos_y = round(center_y + sin(radian) * distance - height / 2)

            if pre_coord:   # detect and fix y-coordinate overlaps with previous child item
                pre_y, pre_h = pre_coord['y'], pre_coord['height']
                if pre_y > pos_y > pre_y - pre_h:       # if items are in 2nd or 3rd (left) quadrants
                    pos_y = pre_y - pre_h
                elif pos_y > pre_y > pos_y - height:    # items are in 1st or 4th (right) quadrants
                    pos_y = pre_y + height

            if pos_y < 0:
                distance = ellipse_polar_radius(ell_x, ell_y + pos_y, radian)
                pos_y = 0
            elif (dif := pos_y + height - win_h) > 0:
                distance = ellipse_polar_radius(ell_x, ell_y - dif, radian)
                pos_y = win_h - height
            if pos_x < 0:
                distance = ellipse_polar_radius(ell_x + pos_x, ell_y, radian)
                pos_x = 0
            elif (dif := pos_x + width - win_w) > 0:
                distance = ellipse_polar_radius(ell_x - dif, ell_y, radian)
                pos_x = win_w - width

            item.menu_distance = distance
            item.menu_radian = radian

            ani = Animation(x=pos_x, y=pos_y, width=item.width, height=item.height, d=dur)
            pre_coord = ani.animated_properties
            if item.x or item.y:
                # ani = Animation(center_x=center_x, center_y=center_y, width=99, height=99, d=dur / 3) + ani
                # commented out because on heavy resize of the app window, the second animation gets not finished
                pass
            else:
                item.center = center_x, center_y
                # item.size = 9, 9
                # commented out because on heave win resize the last item keeps size=9,9 (continuing resizing)
            ani.bind(on_progress=self._item_moved)
            ani.start(item)

        def _finished_layout(*_args):
            self._layout_finished = True
        ani = Animation(_anim_alpha=0.0, d=dur) + Animation(_anim_alpha=1.0, d=dur)
        ani.bind(on_complete=_finished_layout)
        ani.start(self)

    def add_widget(self, widget, index=0, canvas=None):
        """ manage children added via kv, python and :class:`ae.kivy_dyn_chi.DynamicChildrenBehavior`. """
        if self.button_image:
            self.menu_items.append(widget)
            widget.child_index = len(self.menu_items) - 1
        else:
            self.button_image = widget
        super().add_widget(widget, index, canvas)

    def close(self, *_args, **kwargs):
        """ close/dismiss menu (ae.gui_app popup handling compatibility for all GUI frameworks).

        .. note:: prevents close/dismiss of any dropdown/popup while clicking on help activator widget.

        :param _args:           arguments (to have compatible signature for DropDown/Popup/ModalView widgets).
        :param kwargs:          keyword arguments (compatible signature for DropDown/Popup/ModalView widgets):
                                `force`: pass `True` to force closing, ignoring return value of `dispatch('on_dismiss')`
                                `animation`: pass False to close this menu without fade-out animation
        """
        help_layout = self.fw_app.help_layout
        if help_layout and isinstance(help_layout.targeted_widget, HelpToggler):
            return

        self.dispatch('on_pre_dismiss')

        if not self.dispatch('on_dismiss') or kwargs.get('force', False):
            if not self.is_open:   # prevent multiple close from post-dispatches
                return
            self.is_open = False
            self.deactivate_esc_key_close()

            if kwargs.get('animation', True):
                ani = Animation(_anim_alpha=0.0, d=self._anim_duration)
                ani.bind(on_complete=self._finalize_close)
                ani.start(self)
            else:
                self._anim_alpha = 0.0
                self._finalize_close()

    dismiss = close     #: alias method of :meth:`~FlowSelector.close`

    def on_dismiss(self) -> Optional[bool]:
        """ dismiss/close default event handler.

        :return:                return True to prevent/cancel the dismiss/close.
        """
        return not self.is_open \
            or not self.main_app.change_flow(id_of_flow('close', 'flow_popup'), **self.close_kwargs)

    def on_open(self):
        """ open default event handler. """

    def on_pre_dismiss(self):
        """ pre close/dismiss event handler. """

    def on_pre_open(self):
        """ pre open default event handler. """

    def on_release(self):
        """ touch release default event handler. """
        self.close()

    def open(self, attach_to: Widget, **kwargs: Dict[str, Any]):
        """ display flow selector menu items, with animation and as a popup in modal mode.

        :param attach_to:       the widget to which this menu gets attached to (also called opener).
        :param kwargs:          optional arguments:

                                * 'animation': `False` will disable the fade-in-animation (default=True).
        """
        if self.is_open:
            return
        self.is_open = True
        self.activate_esc_key_close()

        self.attached_widget = attach_to
        self.activate_modal(align_center=False)

        self._attached_wid_pos = attach_to.pos
        self._attached_binder = abi = AbsolutePosSizeBinder(attach_to, bind_window_size=True)
        abi.size_to_callback(self._attached_size)
        abi.pos_to_callback(self._attached_pos)

        self.center = self._attached_touch_pos or attach_to.to_window(*attach_to.center)
        self._attached_pos(attach_to, attach_to.to_window(*self._attached_wid_pos))

        self.bind(menu_items=self._layout_items)

        self.dispatch('on_pre_open')

        if kwargs.get('animation', True):
            ani = Animation(_anim_alpha=1.0, d=self._anim_duration)
            ani.bind(on_complete=lambda *_args: self.dispatch('on_open'))
            ani.start(self)
        else:
            self._anim_alpha = 1.0
            self.dispatch('on_open')

    def remove_widget(self, widget):
        """ sync self.menu_items with self.children. """
        super().remove_widget(widget)
        self.menu_items.remove(widget)

    def touch_pos_is_inside(self, pos: List[float]) -> bool:
        """ is touch inside of this widget or a group of sub-widgets. overwritten to also include the menu items.

        :param pos:             touch position (x, y) in window coordinates.
        :return:                True if this menu and its items would process a touch event at the touch position
                                specified by the :paramref:`~touch_pos_is_inside.pos` argument.
        """
        # assert set(self.container.children) == set(self.menu_items + [self.button_image])
        return super().touch_pos_is_inside(pos) or any(_.collide_point(*pos) for _ in self.menu_items)


class FlowToggler(HelpBehavior, SlideSelectBehavior, TouchableBehavior, ToggleButtonBehavior,
                  ImageLabel):                                                                      # pragma: no cover
    """ toggle button changing flow id. """
    long_tap_flow_id = StringProperty()     #: flow id that will be set when this button gets long tap event
    tap_flow_id = StringProperty()          #: the new flow id that will be set when this toggle button get released
    tap_kwargs = DictProperty()             #: kwargs dict passed to event handler (change_flow) when button get tapped

    def __init__(self, **kwargs):
        ensure_tap_kwargs_refs(kwargs, self)
        super().__init__(**kwargs)
        self.down_shader = {'add_to': 'before', 'shader_code': '=circled_alpha', 'render_shape': Ellipse}

    def on_long_tap(self, touch: MotionEvent):
        """ long tap/click default handler.

        :param touch:           motion/touch event data with the touched widget in `touch.grab_current`.
        """
        super().on_long_tap(touch)
        if flow_id := self.long_tap_flow_id:
            self.main_app.change_flow(flow_id, **update_tap_kwargs(self, popup_kwargs={'touch_event': touch}))

    def on_release(self):
        """ overridable touch release event handler. """
        self.main_app.change_flow(self.tap_flow_id, **self.tap_kwargs)


class ConfirmationShowPopup(FlowPopup):
    """ flow popup to display info a messages to be confirmed by the user. """
    message = StringProperty()          #: popup window message text to display
    title = StringProperty()            #: popup window title text to display
    confirm_flow_id = StringProperty()  #: tap_flow_id of the confirm button
    confirm_kwargs = DictProperty()     #: tap_kwargs dict of the confirm button
    confirm_text = StringProperty()     #: confirm button text


class InputShowPopup(FlowPopup):
    """ flow popup to allow tht user to input a string. """
    message = StringProperty()          #: popup window message text to display
    title = StringProperty()            #: popup window title text to display
    input_default = StringProperty()    #: initial/default input string
    enter_confirms = BooleanProperty()  #: if enter key closes the popup confirming the input (default=True)
    confirm_flow_id = StringProperty()  #: tap_flow_id of the confirm button
    confirm_kwargs = DictProperty()     #: tap_kwargs dict of the confirm button
    confirm_text = StringProperty()     #: confirm button text


class MessageShowPopup(FlowPopup):
    """ flow popup to display info or error messages. """
    message = StringProperty()          #: popup window message text to display
    title = StringProperty()            #: popup window title text to display


class Tooltip(ScrollView):                                                           # pragma: no cover
    """ semi-transparent and optional click-through container to display help and tour page texts. """
    targeted_widget = ObjectProperty()
    """ target widget to display tooltip text for (mostly a button, but could any, e.g. a layout widget).

    :attr:`targeted_widget` is a :class:`~kivy.properties.ObjectProperty` and defaults to the main app help_activator.
    """

    tip_text = StringProperty()
    """ tooltip text string to display.

    :attr:`tip_text` is a :class:`~kivy.properties.StringProperty` and defaults to an empty string.
    """

    anchor_spe = ObjectProperty()       #: anchor pos and direction, see :data:`~ae.gui_help.AnchorSpecType` (read-only)
    has_tour = BooleanProperty(False)   #: True if a tour exists for the current app flow/help context (read-only)
    tap_thru = BooleanProperty(False)   #: True if user can tap widgets behind/covered by this tooltip win (read-only)
    tour_start_pos = ListProperty()     #: screen position of the optionally displayed tour start button (read-only)
    tour_start_size = ListProperty()    #: size of the optionally displayed tour start button (read-only)

    def __init__(self, **kwargs):
        self.main_app = App.get_running_app().main_app
        self.targeted_widget = self.main_app.help_activator     # set default-value before calling super()
        # init binder before super().__init__ because calls back on_targeted_widget if targeted_widget is in kwargs
        self._targeted_binder = AbsolutePosSizeBinder(self.targeted_widget)

        super().__init__(**kwargs)

    def _actual_pos(self, *_args) -> Tuple[float, float]:
        wid = self.targeted_widget
        win_w, win_h = Window.size
        self.anchor_spe = anc = anchor_spec(*wid.to_window(*wid.pos), *wid.size, win_w, win_h)
        return anchor_layout_x(anc, self.width, win_w), anchor_layout_y(anc, self.height, win_h)

    def collide_tap_thru_toggler(self, touch_x: float, touch_y: float) -> bool:
        """ check if touch is on the tap through toggler pseudo button.

        :param touch_x:         window x position of touch.
        :param touch_y:         window y position of touch.
        :return:                True if user touched the tap through toggler.
        """
        anchor_pts = anchor_points(self.main_app.font_size, self.anchor_spe)

        x_values = tuple(x for idx, x in enumerate(anchor_pts) if not idx % 2)
        min_x, max_x = min(x_values), max(x_values)
        y_values = tuple(x for idx, x in enumerate(anchor_pts) if idx % 2)
        min_y, max_y = min(y_values), max(y_values)

        return min_x <= touch_x < max_x and min_y <= touch_y < max_y

    def collide_tour_start_button(self, touch_x: float, touch_y: float) -> bool:
        """ check if touch is on the tap through toggler pseudo button.

        :param touch_x:         window x position of touch.
        :param touch_y:         window y position of touch.
        :return:                True if user touched the tap through toggler.
        """
        min_x, min_y = self.tour_start_pos
        width, height = self.tour_start_size
        max_x, max_y = min_x + width, min_y + height

        return min_x <= touch_x < max_x and min_y <= touch_y < max_y

    def on_size(self, *_args):
        """ (re-)position help_activator tooltip correctly after help text loading and layout resizing. """
        self.pos = self._actual_pos()                               # pylint: disable=W0201

    def on_targeted_widget(self, *_args):
        """ targeted widget changed event handler.

        :param _args:           change event args (unused).
        """
        self._targeted_binder.unbind()

        wid = self.targeted_widget
        self._targeted_binder = twb = AbsolutePosSizeBinder(wid, bind_window_size=True)
        twb.size_to_attribute(self, 'pos', self._actual_pos)    # ensure position update on wid.size and .pos changes
        twb.pos_to_attribute(self, 'pos', self._actual_pos)

        self.pos = self._actual_pos()  # pylint: disable=W0201  # initial reposition of tooltip window

    def on_touch_down(self, touch: MotionEvent) -> bool:
        """ check for additional events added by this class.

        :param touch:           motion/touch event data.
        :return:                True if event got processed/used.
        """
        if self.collide_tap_thru_toggler(*touch.pos):
            self.tap_thru = not self.tap_thru
            ret = True
        elif self.has_tour and self.collide_tour_start_button(*touch.pos):
            ret = self.main_app.start_app_tour(help_id_tour_class(self.targeted_widget.help_id))
        elif self.tap_thru or not self.collide_point(*touch.pos):
            ret = False     # if self.tap_thru then make this tooltip widget transparent and let user click through
        else:
            ret = super().on_touch_down(touch)
        return ret
