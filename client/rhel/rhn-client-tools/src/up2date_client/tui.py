#
# TUI for RHN Registration
# Copyright (c) 2000--2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

from os import geteuid
import sys
import string

import gettext
_ = gettext.gettext
gettext.textdomain("rhn-client-tools")

import snack

import signal

import rhnreg, hardware
import up2dateErrors
import up2dateUtils
import rpmUtils
import up2dateLog
import config
import up2dateAuth
from rhn import rpclib

from rhnreg_constants import *

log = up2dateLog.initLog()
cfg = config.initUp2dateConfig()

def FatalErrorWindow(screen, errmsg):
    snack.ButtonChoiceWindow(screen, FATAL_ERROR, "%s" % errmsg,
                             [OK])
    screen.finish()
    sys.exit(1)
    
def ConfirmQuitWindow(screen):
    button = snack.ButtonChoiceWindow(screen, CONFIRM_QUIT,
                             CONFIRM_QUIT_SURE + "\n" + \
                             WHY_REGISTER_SEC  + "\n" + \
                             WHY_REGISTER_SEC_TXT + "\n\n" + \
                             WHY_REGISTER_DLD + "\n" + \
                             WHY_REGISTER_DLD_TXT + "\n\n" + \
                             WHY_REGISTER_SUPP + "\n" + \
                             WHY_REGISTER_SUPP_TXT + "\n\n" + \
                             WHY_REGISTER_COMP + "\n" + \
                             WHY_REGISTER_COMP_TXT + "\n\n" + \
                             CONFIRM_QUIT_WILLNOT + "\n" + \
                             WHY_REGISTER_TIP,
                             [CONTINUE_REGISTERING, REGISTER_LATER2],
                             width = 70)

    if button == string.lower(REGISTER_LATER2):
        screen.finish()
        return 1
    else:
        return 0
    
    
def tui_call_wrapper(screen, func, *params):

    try:
        results = func(*params)
    except up2dateErrors.CommunicationError, e:
        FatalErrorWindow(screen, HOSTED_CONNECTION_ERROR % cfg['serverURL'])
    except up2dateErrors.SSLCertificateVerifyFailedError, e:
        FatalErrorWindow(screen, e.errmsg)
    except up2dateErrors.NoBaseChannelError, e:
        FatalErrorWindow(screen, e.errmsg + '\n' + 
                         BASECHANNELERROR % (up2dateUtils.getArch(), 
                                             up2dateUtils.getOSRelease(),
                                             up2dateUtils.getVersion()))
    except up2dateErrors.SSLCertificateFileNotFound, e:
        FatalErrorWindow(screen, e.errmsg + '\n\n' +
                         SSL_CERT_FILE_NOT_FOUND_ERRER)
        
    return results

class WindowSkipException:

    def __init__(self):
        pass

class AlreadyRegisteredWindow:

    def __init__(self, screen, tui):

        if not rhnreg.registered() or tui.test:
            raise WindowSkipException()

        self.name = "AlreadyRegisteredWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        systemIdXml = rpclib.xmlrpclib.loads(up2dateAuth.getSystemId())
        oldUsername = systemIdXml[0][0]['username']
        oldsystemId = systemIdXml[0][0]['system_id']

        toplevel = snack.GridForm(self.screen, SYSTEM_ALREADY_SETUP, 1, 2)
        self.bb = snack.ButtonBar(self.screen,
                                  [(YES_CONT, "next"),
                                   (NO_CANCEL, "exit")])
        toplevel.add(self.bb, 0, 1, growx = 1)

        tb = snack.Textbox(size[0]-30, size[1]-20,
                            SYSTEM_ALREADY_REGISTERED + "\n\n"
                            + _("Red Hat Network Location:") + " " + self.tui.serverURL + "\n"
                            + _("Login:") + " " + oldUsername + "\n"
                            + _("System ID:") + " " + oldsystemId + "\n\n"
                            + SYSTEM_ALREADY_REGISTERED_CONT + "\n",
                            1, 1)
        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))

        self.g = toplevel

    def saveResults(self):
            pass

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)

        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"

        return button

class ConnectWindow:

    def __init__(self, screen, tui):
        self.name = "ConnectWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        self.server = self.tui.serverURL

        fixed_server_url = rhnreg.makeNiceServerUrl(self.server)

        #Save the config only if the url is different
        if fixed_server_url != self.server:
            self.server = fixed_server_url
            cfg.set('serverURL', self.server)

            cfg.save()
        
        self.proxy = cfg['httpProxy']

        toplevel = snack.GridForm(self.screen, CONNECT_WINDOW, 1, 1)

        text = CONNECT_WINDOW_TEXT % self.server + "\n\n"

        if self.proxy:
            text += CONNECT_WINDOW_TEXT2 % self.proxy

        tb = snack.Textbox(size[0]-30, size[1]-20, 
                           text,
                           1, 1)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))                           

        self.g = toplevel


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)

        # We draw and display the window.  The window gets displayed as
        # long as we are attempting to connect to the server.  Once we
        # connect the window is gone.
        result = self.g.draw()
        self.screen.refresh()
        tui_call_wrapper(self.screen, rhnreg.getCaps)
            
        self.screen.popWindow()

        # Just return next, although the user wouldn't have actually pressed
        # anything.
        return "next"

    def saveResults(self):
        pass
    
class StartWindow:
    
    def __init__(self, screen, tui):
        self.name = "StartWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(self.screen, START_REGISTER_WINDOW,
                                  1, 2)

        start_register_text = START_REGISTER_TEXT

        tb = snack.Textbox(size[0]-10, size[1]-14, start_register_text, 1, 1)
        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))

        self.bb = snack.ButtonBar(self.screen,
                                  [(WHY_REGISTER, "why_register"),
                                   (NEXT, "next"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, growx = 1)

        self.g = toplevel

    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        elif button == "why_register":
            why_reg_win = WhyRegisterWindow(self.screen, self.tui)
            why_reg_win.run()
            return button

        return button

class WhyRegisterWindow:

    def __init__(self, screen, tui):
        self.name = "WhyRegisterWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(self.screen, WHY_REGISTER_WINDOW,
                                  1, 2)


        why_register_text = WHY_REGISTER_TEXT + "\n\n" + \
                            WHY_REGISTER_SEC  + "\n" + \
                            WHY_REGISTER_SEC_TXT + "\n\n" + \
                            WHY_REGISTER_DLD + "\n" + \
                            WHY_REGISTER_DLD_TXT + "\n\n" + \
                            WHY_REGISTER_SUPP + "\n" + \
                            WHY_REGISTER_SUPP_TXT + "\n\n" + \
                            WHY_REGISTER_COMP + "\n" + \
                            WHY_REGISTER_COMP_TXT + "\n\n" + \
                            WHY_REGISTER_TIP

        tb = snack.Textbox(size[0]-10, size[1]-14, why_register_text, 1, 1)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))


        self.bb = snack.ButtonBar(self.screen,
                                  [(BACK_REGISTER, "back")])
        toplevel.add(self.bb, 0, 1, growx = 1)

        self.g = toplevel

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        return button
    

class InfoWindow:

    def __init__(self, screen, tui):
        self.name = "InfoWindow"
        self.screen = screen
        self.tui = tui
        self.tui.alreadyRegistered = 0

        self.server = self.tui.serverURL
        
        size = snack._snack.size()

        toplevel = snack.GridForm(screen, REGISTER_WINDOW, 1, 4)

        # Satellite
        if self.tui.serverType == 'satellite':
            login_prompt = LOGIN_PROMPT % self.server
            login_label = LOGIN
            login_tip = LOGIN_TIP

        # Hosted
        else:
            login_prompt = HOSTED_LOGIN_PROMPT
            login_label = HOSTED_LOGIN
            login_tip = HOSTED_LOGIN_TIP


        label = snack.Textbox(size[0]-10, 3,
                                  login_prompt,
                                  scroll = 0, wrap = 1)

        toplevel.add(label, 0, 0, anchorLeft = 1)

        grid = snack.Grid(2, 3)

        label = snack.Label(login_label)
        grid.setField(label, 0, 0, padding = (0, 0, 1, 0),
                          anchorRight = 1)

        self.userNameEntry = snack.Entry(20)
        self.userNameEntry.set(tui.userName)
        grid.setField(self.userNameEntry, 1, 0, anchorLeft = 1)

        label = snack.Label(PASSWORD)
        grid.setField(label, 0, 1, padding = (0, 0, 1, 0),
                          anchorRight = 1)

        try:
            self.passwordEntry = snack.Entry(20, password = 1)
        except TypeError:
            self.passwordEntry = snack.Entry(20, hidden = 1)
        self.passwordEntry.set(tui.password)
        grid.setField(self.passwordEntry, 1, 1, anchorLeft = 1)

        toplevel.add(grid, 0, 1)

        label = snack.TextboxReflowed(size[0]-10, login_tip)
        toplevel.add(label, 0, 2, anchorLeft=1)

        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                   [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])

        toplevel.add(self.bb, 0, 3, padding = (0, 1, 0, 0),
                 growx = 1)


        self.g = toplevel


    def validateFields(self):
        if self.userNameEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     USER_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.userNameEntry)
            return 0
        if self.passwordEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordEntry)
            return 0


        try:
            self.tui.alreadyRegistered = rhnreg.reserveUser(self.userNameEntry.value(), self.passwordEntry.value())
        except up2dateErrors.ValidationError, e:
            snack.ButtonChoiceWindow(self.screen, _("Error"), _("The server indicated an error:\n") + e.errmsg, buttons = [_("OK")])
            self.g.setCurrent(self.userNameEntry)
            return 0
        except up2dateErrors.CommunicationError,e:
            FatalErrorWindow(self.screen, _("There was an error communicating with the registration server:\n") + e.errmsg)
        return 1


    def saveResults(self):
        self.tui.userName = self.userNameEntry.value()
        self.tui.password = self.passwordEntry.value()
        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        valid = 0
        while not valid:
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "next":
                valid = self.validateFields()

            else:
                break

        self.screen.popWindow()
        return button
    
class OSReleaseWindow:

    def __init__(self, screen, tui):

        self.tui = tui
        # As OSReleaseWindow seems to be the next window which gets tried
        # after InfoWindow has verified the login and password, we
        # can try to activate the hardware asset code here, before
        # available_eus_channels gets called.
        if self.tui.serverType == 'hosted':
            hw_activation_code = rhnreg._activate_hardware(self.tui.userName, self.tui.password)
            if hw_activation_code != None:
                self.tui.other['registration_number'] = hw_activation_code

        if not rhnreg.server_supports_eus():
            log.log_debug("Server does not support EUS, skipping OSReleaseWindow")
            raise WindowSkipException()

        self.available_channels = rhnreg.getAvailableChannels(
	                tui.userName, tui.password)
        if len(self.available_channels['channels']) < 1:
            log.log_debug("No available EUS channels, skipping OSReleaseWindow")
            raise WindowSkipException()

        self.name = "OSReleaseWindow"
        self.screen = screen
        self.size = snack._snack.size()          

        self.selectChannel = False
 
        toplevel = snack.GridForm(self.screen, SELECT_OSRELEASE, 1, 7)
        self.g = toplevel

        self.ostext = snack.TextboxReflowed(self.size[0]-10, OS_VERSION)
        toplevel.add(self.ostext, 0, 0, anchorLeft = 1)
        optiontext1 = LIMITED_UPDATES

        if self.tui.limited_updates_button:
            self.limited_updates_button = snack.SingleRadioButton(optiontext1,
                                                None, isOn = 1)
        else:
            self.limited_updates_button = snack.SingleRadioButton(optiontext1,
                                                None)

        toplevel.add(self.limited_updates_button, 0, 1, padding = (0, 1, 0, 1),
                     anchorLeft = 1)

        self.sublabel = snack.Label(MINOR_RELEASE)
        toplevel.add(self.sublabel, 0, 2, anchorLeft = 1)

        self.channelList = snack.Listbox(self.size[1]-22, 1, 
	                         width = self.size[0]-10)
        toplevel.add(self.channelList, 0, 3)

        for key, value in sorted(self.available_channels['channels'].items(), key=lambda a:a[0]):
            if key in self.available_channels['receiving_updates']:
                value = value + "*"
            self.channelList.append(" " + value, key)

        self.tip = snack.TextboxReflowed(self.size[0]-10, CHANNEL_PAGE_TIP)
        toplevel.add(self.tip, 0, 4, anchorLeft = 1)

        optiontext2 = ALL_UPDATES

        if self.tui.all_updates_button:
            self.all_updates_button = snack.SingleRadioButton(optiontext2, 
                                            self.limited_updates_button, isOn=1)
        else:
            self.all_updates_button = snack.SingleRadioButton(optiontext2, 
                                            self.limited_updates_button)
            
        toplevel.add(self.all_updates_button, 0, 5, padding = (0, 0, 0, 1),
                     anchorLeft = 1)

        #self.warning = snack.TextboxReflowed(self.size[0]-10, 
        #                     CHANNEL_PAGE_WARNING)
        #toplevel.add(self.warning, 0, 9, anchorLeft = 1)


        self.bb = snack.ButtonBar(screen,
                          [(NEXT, "next"),
                           (BACK, "back"),
                           (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 6, growx = 1)

        self.screen.refresh()

        

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        valid = "cancel"
        while valid == "cancel":
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "next":
                valid = self.validateFields()
            else:
                break

        self.screen.popWindow()
        return button

    def validateFields(self):
        msgbox = "ok"
        later_release = False
        if self.limited_updates_button.selected():
            later_release = self.channelList.current() != \
                                 self.available_channels['default_channel']
         
        title = CONFIRM_OS_RELEASE_SELECTION
        if later_release:
            msgbox = snack.ButtonChoiceWindow(self.screen, title,
                           CONFIRM_OS_WARNING % self.channelList.current(),
			   buttons =[OK, CANCEL])
            return msgbox

        if self.all_updates_button.selected() or later_release:
            msgbox = snack.ButtonChoiceWindow(self.screen, title,
                                  CONFIRM_OS_ALL, buttons =[OK, CANCEL])
            return msgbox
        return msgbox

        if self.limited_updates_button.selected():
            #TODO: warn
            return msgbox

    def saveResults(self):
        # if limited updates save the channel and selction
        # for future use
        if self.limited_updates_button.selected():
            log.log_debug("Selected Channel %s" % self.channelList.current())
            self.tui.other['channel'] = self.channelList.current()
            self.tui.limited_updates_button = self.limited_updates_button.selected()
            self.tui.all_updates_button = 0

        # saving data for all updates button
        if self.all_updates_button.selected():
            self.tui.all_updates_button = self.all_updates_button.selected()
            self.tui.limited_updates_button = 0


class HardwareWindow:

    def __init__(self, screen, tui):
        self.name = "HardwareWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        #get the virtualization uuid and set it to other.
        (virt_uuid, virt_type) = rhnreg.get_virt_info()
        if not virt_uuid is None:
            self.tui.other['virt_uuid'] = virt_uuid
            self.tui.other['virt_type'] = virt_type

        # read all hardware in
        tui.hardware = hardware.Hardware()
        
        toplevel = snack.GridForm(screen, HARDWARE_WINDOW, 1, 7)

        text = snack.TextboxReflowed(70, HARDWARE_WINDOW_DESC1)

        toplevel.add(text, 0, 0, anchorLeft = 1)

        grid = snack.Grid(2, 2)

        label = snack.Label(_("Profile name:"))
        grid.setField(label, 0, 0, padding = (0, 0, 1, 0), anchorRight = 1)

        self.profileEntry = snack.Entry(40)
        grid.setField(self.profileEntry, 1, 0, anchorLeft = 1)

        toplevel.add(grid, 0, 1, anchorLeft = 1)
        
        if tui.includeHardware:
            self.hardwareButton = snack.Checkbox(HARDWARE_WINDOW_CHECKBOX, isOn = 1)
        else:
            self.hardwareButton = snack.Checkbox(HARDWARE_WINDOW_CHECKBOX)
            
        toplevel.add(self.hardwareButton, 0, 2, padding = (0, 1, 0, 0),
                     anchorLeft = 1)

        label = snack.Label(DESELECT)
        toplevel.add(label, 0, 3, anchorLeft = 1, padding = (0, 0, 0, 1))

        grid = snack.Grid(4, 3)
        hardware_text = ''

        hardware_text += _("Version: ") + up2dateUtils.getVersion() + "  "
        self.versionLabel = snack.Label(_("Version: "))
        grid.setField(self.versionLabel, 0, 0, padding = (0, 0, 1, 0), anchorLeft = 1)

        self.versionLabel2 = snack.Label(up2dateUtils.getVersion())
        grid.setField(self.versionLabel2, 1, 0, anchorLeft = 1)

        hardware_text += _("CPU model: ")

        for hw in tui.hardware:            
            if hw['class'] == 'CPU':
                hardware_text += hw['model'] +"\n"
                
        hardware_text += _("Hostname: ")

        for hw in tui.hardware:
            if hw['class'] == 'NETINFO':
                hardware_text += hw['hostname'] + "\n"

                if tui.profileName != "":
                    self.profileEntry.set(tui.profileName)
                else:
                    self.profileEntry.set(hw['hostname'])

        hardware_text += _("CPU speed: ")

        for hw in tui.hardware:            
            if hw['class'] == 'CPU':
                hardware_text += _("%d MHz") % hw['speed'] + "  "

        hardware_text += _("IP Address: ")

        for hw in tui.hardware:
            if hw['class'] == 'NETINFO':
                hardware_text += hw['ipaddr'] + "  "

        hardware_text += _("Memory: ")

        for hw in tui.hardware:
            if hw['class'] == 'MEMORY':
                hardware_text += _("%s megabytes") % hw['ram']

        tb = snack.TextboxReflowed(80, hardware_text)
        toplevel.add(tb, 0, 4)

        self.additionalHWLabel = snack.TextboxReflowed(size[0]-10, HARDWARE_WINDOW_DESC2)

        toplevel.add(self.additionalHWLabel, 0, 5, padding = (0, 1, 0, 0),
                     anchorLeft = 1)
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 6, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

        # self.screen.gridWrappedWindow(toplevel, 'HardwareWindow', 80, 14)

    def saveResults(self):
        self.tui.profileName = self.profileEntry.value()
        self.tui.includeHardware = self.hardwareButton.selected()

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class PackagesWindow:

    def __init__(self, screen, tui):
        self.name = "PackagesWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(screen, PACKAGES_WINDOW, 1, 5)
        self.g = toplevel


        text = snack.TextboxReflowed(size[0]-10, PACKAGES_WINDOW_DESC1)

        toplevel.add(text, 0, 0, anchorLeft = 1)

        self.packagesButton = snack.Checkbox(PACKAGES_WINDOW_DESC2, 1)
        toplevel.add(self.packagesButton, 0, 1, padding = (0, 1, 0, 1),
                     anchorLeft = 1)

        label = snack.Label(PACKAGES_WINDOW_UNCHECK)
        toplevel.add(label, 0, 2, anchorLeft = 1)

        #self.packageList = snack.Listbox(size[1]-18, 1, width = size[0]-10)
        self.packageList = snack.CheckboxTree(size[1]-18, 1)
        toplevel.add(self.packageList, 0, 3)

        # do we need to read the packages from disk?
        if tui.packageList == []:
            self.pwin = snack.GridForm(screen, PACKAGES_WINDOW_PKGLIST, 1, 1)

            self.scale = snack.Scale(40, 100)
            self.pwin.add(self.scale, 0, 0)
            self.pwin.draw()
            self.screen.refresh()
            getArch = 0
            if rhnreg.cfg['supportsExtendedPackageProfile']:
                getArch = 1
            tui.packageList = rpmUtils.getInstalledPackageList(getArch=getArch)
            self.screen.popWindow()

        for package in tui.packageList:
            self.packageList.append("%s-%s-%s" % (package['name'],
                                                  package['version'],
                                                  package['release']),
                                                  item = package['name'],
                                                  selected = 1)
            
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 4, padding = (0, 1, 0, 0),
                     growx = 1)



    def setScale(self, amount, total):
        self.scale.set(int(((amount * 1.0)/ total) * 100))
        self.pwin.draw()
        self.screen.refresh()
        

    def saveResults(self):
        self.tui.includePackages = self.packagesButton.selected()
        selection = self.packageList.getSelection()
        for pkg in self.tui.packageList:
            if pkg['name'] in selection:
                self.tui.selectedPackages.append(pkg)

        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class SendWindow:

    def __init__(self, screen, tui):
        self.screen = screen
        self.tui = tui
        self.name = "SendWindow"
        size = snack._snack.size()
        
        toplevel = snack.GridForm(screen, SEND_WINDOW, 1, 2)

        text = snack.TextboxReflowed(size[0]-15, SEND_WINDOW_DESC)
        toplevel.add(text, 0, 0)

        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class SendingWindow:

    def __init__(self, screen, tui):
        self.screen = screen
        self.tui = tui
        self.name = "SendingWindow"
        size = snack._snack.size()

        self.pwin = snack.GridForm(screen, SENDING_WINDOW, 1, 1)

        self.scale = snack.Scale(40, 100)
        self.pwin.add(self.scale, 0, 0)

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)

        self.pwin.draw()
        self.screen.refresh()

        reg_info = None
        try:
            # reg_info dict contains: 'system_id', 'channels', 
            # 'failed_channels', 'slots', 'failed_slots'
            log.log_debug('other is %s' % str(self.tui.other))

            reg_info = rhnreg.registerSystem2(self.tui.userName, self.tui.password,
                                             self.tui.profileName, 
                                             other = self.tui.other)
            reg_info = reg_info.rawDict
            
            if isinstance(reg_info['system_id'], unicode):
                systemId = unicode.encode(reg_info['system_id'], 'utf-8')
            else:
                systemId = reg_info['system_id']
                
        except up2dateErrors.CommunicationError, e:
            FatalErrorWindow(self.screen, 
                             _("Problem registering system:\n") + e.errmsg)
        except up2dateErrors.RhnUuidUniquenessError, e:
            FatalErrorWindow(self.screen, 
                             _("Problem registering system:\n") + e.errmsg)
        except up2dateErrors.InsuffMgmntEntsError, e:
            FatalErrorWindow(self.screen,
                             _("Problem registering system:\n") + e.errmsg)
        except up2dateErrors.ActivationKeyUsageLimitError, e:
            FatalErrorWindow(self.screen,
                             ACT_KEY_USAGE_LIMIT_ERROR)
        except:
            log.log_exception(*sys.exc_info())
            FatalErrorWindow(self.screen, _("Problem registering system."))

        # write the system id out.
        if not rhnreg.writeSystemId(systemId):
            FatalErrorWindow(self.screen, 
                             _("Problem writing out system id to disk."))

        self.setScale(1, 4)

        # include the info from the oeminfo file as well
        self.oemInfo = rhnreg.getOemInfo()
        
        # dont send if already registered, do send if they have oemInfo
        if ( not self.tui.alreadyRegistered ) or ( len(self.oemInfo)):
            # send product registration information
            if rhnreg.cfg['supportsUpdateContactInfo']:
                try:
                    rhnreg.updateContactInfo(self.tui.userName, self.tui.password,  self.tui.productInfo)
                except up2dateErrors.CommunicationError, e:
                    FatalErrorWindow(self.screen, _("Problem registering personal information:\n") + e.errmsg)
                except:
                    print sys.exc_info()
                    print sys.exc_type
                    
                    FatalErrorWindow(self.screen, 
                                     _("Problem registering personal information"))
                    
            else:
                rhnreg.registerProduct(systemId, self.tui.productInfo,self.tui.oemInfo)
                try:
                    rhnreg.registerProduct(systemId, self.tui.productInfo,self.tui.oemInfo)
                except up2dateErrors.CommunicationError, e:
                    FatalErrorWindow(self.screen, 
                                     _("Problem registering personal information:\n") + 
                                     e.errmsg)
                except:
                    log.log_exception(*sys.exc_info())
                    FatalErrorWindow(self.screen, _("Problem registering personal information"))

        self.setScale(2, 4)

        # maybe upload hardware profile
        if self.tui.includeHardware:
            try:
                rhnreg.sendHardware(systemId, self.tui.hardware)
            except up2dateErrors.CommunicationError, e:
                FatalErrorWindow(self.screen,
                                 _("Problem sending hardware profile:\n") + e.errmsg)
            except:
                log.log_exception(*sys.exc_info())
                FatalErrorWindow(self.screen,
                                 _("Problem sending hardware profile."))

        self.setScale(3, 4)

        # build up package list if necessary
        if self.tui.includePackages:
            try:
                rhnreg.sendPackages(systemId, self.tui.selectedPackages)
            except up2dateErrors.CommunicationError, e:
                FatalErrorWindow(self.screen, _("Problem sending package list:\n") + e.errmsg)
            except:
                log.log_exception(*sys.exc_info())
                FatalErrorWindow(self.screen, _("Problem sending package list."))

        li = None
        try:
            li = up2dateAuth.updateLoginInfo()
        except up2dateErrors.InsuffMgmntEntsError, e:
            FatalErrorWindow(self.screen, e)

        rhnreg.spawnRhnCheckForUI() 
        self.setScale(4, 4)

        # Pop the pwin (Progress bar window)
        self.screen.popWindow()

        self.tui.reg_info = reg_info

        return "next"

    def saveResults(self):
        pass

    def setScale(self, amount, total):
        self.scale.set(int(((amount * 1.0)/ total) * 100))
        self.pwin.draw()
        self.screen.refresh()


class FinishWindow:

    def __init__(self, screen, tui):
        self.name = "FinishWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        toplevel = snack.GridForm(screen, FINISH_WINDOW,
                                  1, 2)

        text = snack.TextboxReflowed(size[0]-11, FINISH_WINDOW_TEXT_TUI)
        toplevel.add(text, 0, 0)

        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(_("Finish"), "next")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class ReviewWindow:

    def __init__(self, screen, tui):
        self.name = "ReviewWindow"
        self.screen = screen
        self.tui = tui
        self.reg_info = tui.reg_info
        size = snack._snack.size()
        
        toplevel = snack.GridForm(screen, REVIEW_WINDOW, 1, 2)
    
        # Build up the review_window_text based on the data in self.reg_info
        review_window_text = REVIEW_WINDOW_PROMPT + "\n\n"

        # Create and add the text for what channels the system was
        # subscribed to.
        if len(self.reg_info['channels']) > 0:
            channel_list = ""
            for channel in self.reg_info['channels']:
                channel_list += channel + "\n"

            channels = CHANNELS_TITLE + "\n" + \
                       OK_CHANNELS + "\n" + \
                       "%s\n" 

            # If it's hosted, reference the hosted url,
            # otherwise, we don't know the url for their sat.
            log.log_debug("server type is %s " % self.tui.serverType)
            if self.tui.serverType == 'hosted':
                channels += CHANNELS_HOSTED_WARNING
            else:
                channels += CHANNELS_SAT_WARNING

            review_window_text += channels % channel_list + "\n\n"
            
        if len(self.reg_info['system_slots']) > 0:
            slot_list = ""
            for slot in self.reg_info['system_slots']:
                if slot == 'enterprise_entitled':
                    slot_list += MANAGEMENT + "\n"
                elif slot == 'provisioning_entitled':
                    slot_list += PROVISIONING + "\n"
                elif slot == 'sw_mgr_entitled':
                    slot_list += UPDATES + "\n"
                elif slot == 'monitoring_entitled':
                    slot_list += MONITORING + "\n"
                elif slot == 'virtualization_host':
                    slot_list += VIRT + "\n"
                elif slot == 'virtualization_host_platform':
                    slot_list += VIRT_PLATFORM + "\n"
                else:
                    slot_list += slot + "\n"
            review_window_text += SLOTS % slot_list + "\n\n"
            
        if len(self.reg_info['universal_activation_key']) > 0:
            act_key_list = ""
            for act_key in self.reg_info['universal_activation_key']:
                act_key_list += act_key
            review_window_text += ACTIVATION_KEY % (act_key_list)
            
        self.review_window = snack.Textbox(size[0]-10, size[1]-14, review_window_text, 1, 1)
    
        toplevel.add(self.review_window, 0, 0, padding = (0, 1, 0, 0))
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen, [(OK, "next")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

    def saveResults(self):
        return 1

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
            
        return button    
    
class Tui:

    def __init__(self, screen, test):
        self.screen = screen
        self.test = test
        self.size = snack._snack.size()
        self.drawFrame()
        self.alreadyRegistered = 0
        try:
            self.serverType = rhnreg.getServerType()
        except up2dateErrors.InvalidProtocolError:
            FatalErrorWindow(screen, _("You specified an invalid protocol." +
                                     "Only https and http are allowed."))

        self.windows = [
            AlreadyRegisteredWindow,
            ConnectWindow,
            StartWindow,
            InfoWindow,
            OSReleaseWindow,
            HardwareWindow,
            PackagesWindow,
            SendWindow,
            SendingWindow,
            ReviewWindow,
            FinishWindow
            ]

        # if serverUrl is a list in the config, only reference the first one
        # when we need it
        if type(cfg['serverURL']) == type([]):
            self.serverURL = cfg['serverURL'][0]
        else:
            self.serverURL = cfg['serverURL']
        
        if not cfg['sslCACert']:
            # Always use the path from the cert if available, else set to 
            # default location
            if self.serverType == "hosted":
                cfg.set('sslCACert', '/usr/share/rhn/RHNS-CA-CERT')
            else:
                cfg.set('sslCACert', '/usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT') 
       
    def __del__(self):
        self.screen.finish()


    def drawFrame(self):
        self.welcomeText = COPYRIGHT_TEXT
        self.screen.drawRootText(0, 0, self.welcomeText)
        self.screen.pushHelpLine(_("  <Tab>/<Alt-Tab> between elements  |  <Space> selects  |  <F12> next screen"))


    def initResults(self):
        self.userName = ""
        self.password = ""

        self.oemInfo = {}
        self.productInfo = {
            "entitlement_num" : "",
            "registration_num" : "",
            "first_name" : "",
            "last_name" : "",
            "company" : "",
            "address" : "",
            "city" : "",
            "state" : "",
            "zip" : "",
            "country" : "",
           }

        self.other = {} 
        self.other['registration_number'] = ''
        
        self.profileName = ""
        self.includeHardware = 1
        
        self.limited_updates_button = 1
        self.all_updates_button = 0
        self.includePackages = 0
        self.packageList = []
        self.selectedPackages = []

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.initResults()
        
        direction = "forward"

        try:
            index = 0
            while index < len(self.windows):

                win = None
                try:
                    win = self.windows[index](self.screen, self)
                except WindowSkipException:
                    if direction == "forward":
                        index = index + 1
                    else:
                        index = index - 1
                    continue

                log.log_debug("index is %s" % index)
                
                result = win.run()
                log.log_debug("Result %s" % result)

                if result == "back":
                    if index > 0:
                        index = index - 1

                    direction = "backward"

                elif result == "exit":
                    return

                elif result == "cancel":
                    log.log_debug("Caught a cancel request")
                    
                    # Show the confirm quit window
                    if ConfirmQuitWindow(self.screen) == 1:
                        return
                    
                elif result == "next":
                    index = index + 1
                    win.saveResults()
                    direction = "forward"

        finally:
            self.screen.finish()

        
def main():
    test = 0    
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if len(sys.argv) > 1:
        if sys.argv[1] == "-t" or sys.argv[1] == "--test":
            test = 1

    screen = snack.SnackScreen()

    if geteuid() != 0 and not test:
        FatalErrorWindow(screen, _("You must run the RHN registration program as root."))

    tui = Tui(screen, test)
    tui.run()

    
if __name__ == "__main__":
    main()
