#
# Licensed under the GNU General Public License Version 3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2010 Aron Parsons <aron@redhat.com>
#

# NOTE: the 'self' variable is an instance of SpacewalkShell

import shlex
from operator import itemgetter
from optparse import Option
from xml.parsers.expat import ExpatError
from spacecmd.utils import *

__PKG_COMPARISONS = { 0 : 'Same',
                      1 : 'Only here',
                      2 : 'Newer here',
                      3 : 'Only there',
                      4 : 'Newer there' }

def print_package_comparison(self, results):
        max_name  = max_length( map(itemgetter('package_name'), results) )

        # sometimes 'this_system' or 'other_system' can be None
        tmp_this = []
        tmp_other = []
        for item in results:
            tmp_this.append(str(item.get('this_system')))
            tmp_other.append(str(item.get('other_system')))

        max_this  = max_length(tmp_this)
        max_other = max_length(tmp_other)

        max_comparison = 11

        # print headers
        print '%s  %s  %s  %s' % (
                'Package'.ljust(max_name),
                'This System'.ljust(max_this),
                'Other System'.ljust(max_other),
                'Difference'.ljust(max_comparison))

        print '%s  %s  %s  %s' % (
                '-' * max_name,
                '-' * max_this,
                '-' * max_other,
                '-' * max_comparison)

        for item in results:
            # don't show packages that are the same
            if item.get('comparison') == 0: continue

            print '%s  %s  %s  %s' % (
                  item.get('package_name').ljust(max_name),
                  str(item.get('this_system')).ljust(max_this),
                  str(item.get('other_system')).ljust(max_other),
                  __PKG_COMPARISONS[item.get('comparison')])

####################

def manipulate_child_channels(self, args, remove=False):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        if remove:
            self.help_system_removechildchannels()
        else:
            self.help_system_addchildchannels()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    new_channels = args

    print 'Systems'
    print '-------'
    print '\n'.join(sorted(systems))
    print

    if remove:
        print 'Removing Channels'
        print '-----------------'
    else:
        print 'Adding Channels'
        print '---------------'

    print '\n'.join(sorted(new_channels))

    if not self.user_confirm(): return

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        child_channels = \
            self.client.system.listSubscribedChildChannels(self.session,
                                                           system_id)

        child_channels = [c.get('label') for c in child_channels]

        if remove:
            for channel in new_channels:
                if channel in child_channels:
                   child_channels.remove(channel)
        else:
            for channel in new_channels:
                if channel not in child_channels:
                    child_channels.append(channel)

        self.client.system.setChildChannels(self.session,
                                            system_id,
                                            child_channels)

####################

def help_system_list(self):
    print 'system_list: List all system profiles'
    print 'usage: system_list'

def do_system_list(self, args, doreturn=False):
    if doreturn:
        return self.get_system_names()
    else:
        if len(self.get_system_names()):
            print '\n'.join(sorted(self.get_system_names()))

####################

def help_system_reboot(self):
    print 'system_reboot: Reboot a system'
    print 'usage: system_reboot <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_reboot(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_reboot(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_reboot()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    if not self.user_confirm('Reboot these systems [y/N]:'): return

    action_time = parse_time_input('now')

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.scheduleReboot(self.session, id, action_time)

####################

def help_system_search(self):
    print 'system_search: List systems that match the given criteria'
    print 'usage: system_search QUERY'
    print
    print 'Available Fields:'
    print '\n'.join(self.SYSTEM_SEARCH_FIELDS)
    print
    print 'Examples:'
    print '> system_search device:vmware'
    print '> system_search ip:192.168.82'

def do_system_search(self, args, doreturn=False):
    (args, options) = parse_arguments(args)

    if len(args) != 1:
        self.help_system_search()
        return

    query = args[0]

    if re.search(':', query):
        try:
            (field, value) = query.split(':')
        except ValueError:
            logging.error('Invalid query')
            return []
    else:
        field = 'name'
        value = query

    if not value:
        logging.warning('Invalid query')
        return []

    results = []
    if field == 'name':
        results = self.client.system.search.nameAndDescription(self.session,
                                                               value)
        key = 'name'
    elif field == 'id':
        # build an array of key/value pairs from our local system cache
        self.generate_system_cache()
        results = [ {'id' : k, 'name' : self.all_systems[k] } \
                    for k in self.all_systems ]
        key = 'id'
    elif field == 'ip':
        results = self.client.system.search.ip(self.session, value)
        key = 'ip'
    elif field == 'hostname':
        results = self.client.system.search.hostname(self.session, value)
        key = 'hostname'
    elif field == 'device':
        results = self.client.system.search.deviceDescription(self.session,
                                                              value)
        key = 'hw_description'
    elif field == 'vendor':
        results = self.client.system.search.deviceVendorId(self.session,
                                                           value)
        key = 'hw_vendor_id'
    elif field == 'driver':
        results = self.client.system.search.deviceDriver(self.session,
                                                         value)
        key = 'hw_driver'
    else:
        logging.warning('Invalid search field')
        return []

    systems = []
    max_size = 0
    for s in results:
        # only use real matches, not the fuzzy ones we get back
        if re.search(value, str(s.get(key)), re.I):
            if len(s.get('name')) > max_size:
                max_size = len(s.get('name'))

            systems.append( (s.get('name'), s.get(key)) )

    if doreturn:
        return [s[0] for s in systems]
    else:
        if len(systems):
            for s in sorted(systems):
                if key == 'name':
                    print s[0]
                else:
                    print '%s  %s' % (s[0].ljust(max_size),
                                      str(s[1]).strip())

####################

def help_system_runscript(self):
    print 'system_runscript: Schedule a script to run on the list of'
    print '                  systems provided'
    print '''usage: system_runscript <SYSTEMS> [options]

options:
  -u USER
  -g GROUP
  -t TIMEOUT
  -s START_TIME
  -f FILE'''
    print
    print self.HELP_SYSTEM_OPTS
    print
    print self.HELP_TIME_OPTS

def complete_system_runscript(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_runscript(self, args):
    options = [ Option('-u', '--user', action='store'),
                Option('-g', '--group', action='store'),
                Option('-t', '--timeout', action='store'),
                Option('-s', '--start-time', action='store'),
                Option('-f', '--file', action='store') ]

    (args, options) = parse_arguments(args, options)

    if not len(args):
        self.help_system_runscript()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    if not len(systems):
        logging.warning('No systems selected')
        return

    if is_interactive(options):
        options.user  = prompt_user('User [root]:')
        options.group = prompt_user('Group [root]:')

        # defaults
        if not options.user:  options.user  = 'root'
        if not options.group: options.group = 'root'

        try:
            options.timeout = prompt_user('Timeout (in seconds) [600]:')
            if options.timeout:
                options.timeout = int(options.timeout)
            else:
                options.timeout = 600
        except ValueError:
            logging.error('Invalid timeout')
            return

        options.start_time = prompt_user('Start Time [now]:')
        options.start_time = parse_time_input(options.start_time)

        script_file = prompt_user('Script File [create]:')

        # read the script provided by the user
        if script_file:
            keep_script_file = True

            options.script = read_file(os.path.abspath(script_file))
        else:
            # have the user write their script
            (options.script, script_file) = editor('#!/bin/bash')
            keep_script_file = False

        if not options.script:
            logging.error('No script provided')
            return
    else:
        if not options.user: options.user = 'root'
        if not options.group: options.group = 'root'
        if not options.timeout: options.timeout = 600
        if not options.start_time: options.start_time = parse_time_input('now')

        if not options.file:
            logging.error('A script file is required')
            return

        options.script = read_file(options.file)

    # display a summary
    print
    print 'User:       %s' % options.user
    print 'Group:      %s' % options.group
    print 'Timeout:    %i seconds' % options.timeout
    print 'Start Time: %s' % options.start_time
    print
    print 'Script Contents'
    print '---------------'
    print options.script

    # have the user confirm
    if not self.user_confirm(): return

    scheduled = 0

    if self.check_api_version('10.11'):
        logging.debug('Scheduling all systems for the same action')

        # schedule all systems for the same action
        system_ids = [ self.get_system_id(s) for s in systems ]

        action_id = self.client.system.scheduleScriptRun(self.session,
                                                         system_ids,
                                                         options.user,
                                                         options.group,
                                                         options.timeout,
                                                         options.script,
                                                         options.start_time)

        logging.info('Action ID: %i' % action_id)
        scheduled = len(system_ids)
    else:
        # older versions of the API require each system to be
        # scheduled individually
        for system in systems:
            system_id = self.get_system_id(system)
            if not system_id: return

            try:
                action_id = \
                    self.client.system.scheduleScriptRun(self.session,
                                                         system_id,
                                                         options.user,
                                                         options.group,
                                                         options.timeout,
                                                         options.script,
                                                         options.start_time)

                logging.info('Action ID: %i' % action_id)
                scheduled += 1
            except Exception, detail:
                logging.debug(detail)
                logging.error('Failed to schedule %s' % system)

    logging.info('Scheduled: %i system(s)' % scheduled)

    # don't delete a pre-existing script that the user provided
    if not keep_script_file:
        try:
            os.remove(script_file)
        except OSError:
            logging.error('Could not remove %s' % script_file)

####################

def help_system_listhardware(self):
    print 'system_listhardware: List the hardware details of a system'
    print 'usage: system_listhardware <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listhardware(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listhardware(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listhardware()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        cpu = self.client.system.getCpu(self.session, system_id)
        memory = self.client.system.getMemory(self.session, system_id)
        devices = self.client.system.getDevices(self.session, system_id)
        network = self.client.system.getNetworkDevices(self.session,
                                                       system_id)

        # Solaris systems don't have these value s
        for v in ('cache', 'vendor', 'family', 'stepping'):
            if not cpu.get(v):
                cpu[v] = ''

        try:
            dmi = self.client.system.getDmi(self.session, system_id)
        except ExpatError:
            dmi = None

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system
            print

        if len(network):
            print 'Network'
            print '-------'

            count = 0
            for device in network:
                if count: print
                count += 1

                print 'Interface:   %s' % device.get('interface')
                print 'MAC Address: %s' % device.get('hardware_address').upper()
                print 'IP Address:  %s' % device.get('ip')
                print 'Netmask:     %s' % device.get('netmask')
                print 'Broadcast:   %s' % device.get('broadcast')
                print 'Module:      %s' % device.get('module')

            print

        print 'CPU'
        print '---'
        print 'Count:    %i' % cpu.get('count')
        print 'Arch:     %s' % cpu.get('arch')
        print 'MHz:      %s' % cpu.get('mhz')
        print 'Cache:    %s' % cpu.get('cache')
        print 'Vendor:   %s' % cpu.get('vendor')
        print 'Model:    %s' % re.sub('\s+', ' ', cpu.get('model'))

        print
        print 'Memory'
        print '------'
        print 'RAM:  %i' % memory.get('ram')
        print 'Swap: %i' % memory.get('swap')

        if dmi:
            print
            print 'DMI'
            print 'Vendor:       %s' % dmi.get('vendor')
            print 'System:       %s' % dmi.get('system')
            print 'Product:      %s' % dmi.get('product')
            print 'Board:        %s' % dmi.get('board')

            print
            print 'Asset'
            print '-----'
            for asset in dmi.get('asset').split(') ('):
                print re.sub('\)|\(', '', asset)

            print
            print 'BIOS Release: %s' % dmi.get('bios_release')
            print 'BIOS Vendor:  %s' % dmi.get('bios_vendor')
            print 'BIOS Version: %s' % dmi.get('bios_version')

        if len(devices):
            print
            print 'Devices'
            print '-------'

            count = 0
            for device in devices:
                if count: print
                count += 1

                print 'Description: %s' % (
                         wrap(device.get('description'), 60)[0])
                print 'Driver:      %s' % device.get('driver')
                print 'Class:       %s' % device.get('device_class')
                print 'Bus:         %s' % device.get('bus')

####################

def help_system_installpackage(self):
    print 'system_installpackage: Install a package on a system'
    print 'usage: system_installpackage <SYSTEMS> <PACKAGE ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_installpackage(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.get_package_names(), text)

def do_system_installpackage(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_installpackage()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()

        # remove 'ssm' from the argument list
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    packages_to_install = args

    # get the ID for each system
    system_ids = []
    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: continue
        system_ids.append(system_id)

    jobs = {}

    if self.check_api_version('10.11'):
        for package in packages_to_install:
            logging.debug('Finding the latest version of %s' % package)

            avail_packages = \
                self.client.system.listLatestAvailablePackage(self.session,
                                                              system_ids,
                                                              package)

            for system in avail_packages:
                system_id = system.get('id')
                if system_id not in jobs:
                    jobs[system_id] = []

                # add this package to the system's queue
                jobs[system_id].append(system.get('package').get('id'))
    else:
        #XXX: Satellite 5.3 compatibility
        for system_id in system_ids:
            logging.debug('Getting available packages for %s' % \
                          self.get_system_name(system_id))

            avail_packages = \
                self.client.system.listLatestInstallablePackages(self.session,
                                                                 system_id)

            for package in avail_packages:
                if package.get('name') in packages_to_install:
                    if system_id not in jobs:
                        jobs[system_id] = []

                    jobs[system_id].append(package.get('id'))

    if not len(jobs):
        logging.warning('No packages to install')
        return

    add_separator = False

    warnings = []
    for system_id in jobs:
        if add_separator: print self.SEPARATOR
        add_separator = True

        # warn the user if the request can not be 100% fulfilled
        if len(jobs[system_id]) != len(packages_to_install):
            # stash the warnings and show at the end so the user can see them
            warnings.append(system_id)

        print '%s:' % self.get_system_name(system_id)
        for package_id in jobs[system_id]:
            print self.get_package_name(package_id)

    # show the warnings to the user
    if len(warnings): print
    for system_id in warnings:
        logging.warning('%s does not have access to all requested packages' % \
                        self.get_system_name(system_id))

    if not self.user_confirm('Install these packages [y/N]:'): return

    scheduled = 0
    for system_id in jobs:
        action_time = parse_time_input('now')

        try:
            self.client.system.schedulePackageInstall(self.session,
                                                      system_id,
                                                      jobs[system_id],
                                                      action_time)

            scheduled += 1
        except:
            logging.error('Failed to schedule %s' % self.get_system_name(system_id))

    logging.info('Scheduled %i system(s)' % scheduled)

####################

def help_system_removepackage(self):
    print 'system_removepackage: Remove a package from a system'
    print 'usage: system_removepackage <SYSTEMS> <PACKAGE ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_removepackage(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.get_package_names(), text)

def do_system_removepackage(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_removepackage()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()

        # remove 'ssm' from the argument list
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    package_list = args

    # get all matching package names
    logging.debug('Finding matching packages')
    matching_packages = \
        filter_results(self.get_package_names(True), package_list)

    jobs = {}
    packages_by_id = {}
    for package_name in matching_packages:
        logging.debug('Finding systems with %s' % package_name)

        package_id = self.get_package_id(package_name)

        installed_systems = \
            self.client.system.listSystemsWithPackage(self.session, package_id)

        installed_systems = [ s.get('name') for s in installed_systems ]

        # each system has a list of packages to remove so that only one
        # API call needs to be made to schedule all the package removals
        # for each system
        for system in systems:
            if system in installed_systems:
                if system not in jobs:
                    jobs[system] = []

                jobs[system].append(package_id)

    add_separator = False

    for system in jobs:
        if add_separator: print self.SEPARATOR
        add_separator = True

        print '%s:' % system
        for package in jobs[system]:
            print self.get_package_name(package)

        spacer = True

    if not len(jobs): return
    if not self.user_confirm('Remove these packages [y/N]:'): return

    action_time = parse_time_input('now')

    scheduled = 0
    for system in jobs:
        system_id = self.get_system_id(system)
        if not system_id: continue

        try:
            action_id = self.client.system.schedulePackageRemove(self.session,
                                                                 system_id,
                                                                 jobs[system],
                                                                 action_time)

            logging.info('Action ID: %i' % action_id)
            scheduled += 1
        except:
            logging.error('Failed to schedule %s' % system)

    logging.info('Scheduled %i system(s)' % scheduled)

####################

def help_system_upgradepackage(self):
    print 'system_upgradepackage: Upgrade a package on a system'
    print 'usage: system_upgradepackage <SYSTEMS> <PACKAGE ...>|*'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_upgradepackage(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.get_package_names(), text)

def do_system_upgradepackage(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_upgradepackage()
        return

    # install and upgrade for individual packages are the same
    if not '.*' in args[1:]:
        return self.do_system_installpackage(' '.join(args))

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()

        # remove 'ssm' from the argument list
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    # make a dictionary of each system and the package IDs to install
    jobs = {}
    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        packages = \
            self.client.system.listLatestUpgradablePackages(self.session,
                                                            system_id)

        if len(packages):
            package_ids = [ p.get('to_package_id') for p in packages ]
            jobs[system] = package_ids
        else:
            logging.warning('No upgrades available for %s' % system)

    if not len(jobs): return

    add_separator = False

    for system in jobs:
        if add_separator: print self.SEPARATOR
        add_separator = True

        print system
        print '-' * len(system)

        # build a temporary list so we can sort by package name
        package_names = []
        for package in jobs[system]:
            name = self.get_package_name(package)

            if name:
                package_names.append(name)
            else:
                logging.error("Couldn't get name for package %i" % package)

        print '\n'.join(sorted(package_names))

    if not self.user_confirm('Upgrade these packages [y/N]:'): return

    action_time = parse_time_input('now')

    scheduled = 0
    for system in jobs:
        system_id = self.get_system_id(system)

        try:
            self.client.system.schedulePackageInstall(self.session,
                                                      system_id,
                                                      jobs[system],
                                                      action_time)

            scheduled += 1
        except Exception, e:
            logging.error('Failed to schedule %s' % system)

    logging.info('Scheduled %i system(s)' % scheduled)

####################

def help_system_listupgrades(self):
    print 'system_listupgrades: List the available upgrades for a system'
    print 'usage: system_listupgrades <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listupgrades(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listupgrades(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listupgrades()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        packages = \
            self.client.system.listLatestUpgradablePackages(self.session,
                                                            system_id)

        if not len(packages):
            logging.warning('No upgrades available for %s' % system)
            continue

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print system
            print '-' * len(system)

        for package in sorted(packages, key=itemgetter('name')):
            # listLatestUpgradablePackages doesn't give us the arch,
            # so use the package ID to get that information
            print self.get_package_name(package.get('to_package_id'))

####################

def help_system_listinstalledpackages(self):
    print 'system_listinstalledpackages: List the installed packages on a'
    print '                              system'
    print 'usage: system_listinstalledpackages <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listinstalledpackages(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listinstalledpackages(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listinstalledpackages()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        packages = self.client.system.listPackages(self.session,
                                                   system_id)

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system
            print

        print '\n'.join(build_package_names(packages))

####################

def help_system_listconfigchannels(self):
    print 'system_listconfigchannels: List the config channels of a system'
    print 'usage: system_listconfigchannels <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listconfigchannels(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listconfigchannels(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listconfigchannels()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system

        try:
            channels = self.client.system.config.listChannels(self.session,
                                                              system_id)
        except:
            logging.warning('%s does not support configuration channels' % \
                            system)
            continue

        print '\n'.join([ c.get('label') for c in channels ])

####################

def help_system_addconfigchannels(self):
    print 'system_addconfigchannels: Add config channels to a system'
    print '''usage: system_addconfigchannels <SYSTEMS> <CHANNEL ...> [options]

options:
  -t add channels to the top of the list
  -b add channels to the bottom of the list'''
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_addconfigchannels(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.do_configchannel_list('', True),
                                  text)

def do_system_addconfigchannels(self, args):
    options = [ Option('-t', '--top', action='store_true'),
                Option('-b', '--bottom', action='store_true') ]

    (args, options) = parse_arguments(args, options)

    if len(args) < 2:
        self.help_system_addconfigchannels()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    channels = args

    if is_interactive(options):
        answer = prompt_user('Add to top or bottom? [T/b]:')
        if re.match('b', answer, re.I):
            options.top = False
        else:
            options.top = True
    else:
        if options.bottom:
            options.top = False
        else:
            options.top = True

    system_ids = [ self.get_system_id(s) for s in systems ]

    self.client.system.config.addChannels(self.session,
                                          system_ids,
                                          channels,
                                          options.top)

####################

def help_system_removeconfigchannels(self):
    print 'system_removeconfigchannels: Remove config channels from a ' \
          'system'
    print 'usage: system_removeconfigchannels <SYSTEMS> <CHANNEL ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_removeconfigchannels(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.do_configchannel_list('', True),
                                  text)

def do_system_removeconfigchannels(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_removeconfigchannels()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    channels = args

    system_ids = [ self.get_system_id(s) for s in systems ]

    self.client.system.config.removeChannels(self.session,
                                             system_ids,
                                             channels)

####################

def help_system_setconfigchannelorder(self):
    print 'system_setconfigchannelorder: Set the ranked order of ' \
          'configuration channels'
    print 'usage: system_setconfigchannelorder <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_setconfigchannelorder(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_setconfigchannelorder(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_setconfigchannelorder()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args.pop(0))

    # get the current configuration channels from the first system
    # in the list
    system_id = self.get_system_id(systems[0])
    new_channels = self.client.system.config.listChannels(self.session,
                                                          system_id)
    new_channels = [ c.get('label') for c in new_channels ]

    # call an interface for the user to make selections
    all_channels = self.do_configchannel_list('', True)
    new_channels = config_channel_order(all_channels, new_channels)

    print
    print 'New Configuration Channels'
    print '--------------------------'
    for i in range(len(new_channels)):
        print '[%i] %s' % (i + 1, new_channels[i])

    if not self.user_confirm(): return

    system_ids = [ self.get_system_id(s) for s in systems ]

    self.client.system.config.setChannels(self.session,
                                          system_ids,
                                          new_channels)

####################

def help_system_deployconfigfiles(self):
    print 'system_deployconfigfiles: Deploy all configuration files for ' \
          'a system'
    print 'usage: system_deployconfigfiles <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_deployconfigfiles(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_deployconfigfiles(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_deployconfigfiles()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    if not len(systems): return

    print 'Systems'
    print '-------'
    print '\n'.join(sorted(systems))

    message = 'Deploy ALL configuration files to these systems [y/N]:'
    if not self.user_confirm(message): return

    system_ids = [ self.get_system_id(s) for s in systems ]

    action_time = parse_time_input('now')

    self.client.system.config.deployAll(self.session,
                                        system_ids,
                                        action_time)

    logging.info('Scheduled deployment for %i system(s)' % len(system_ids))

####################

def help_system_delete(self):
    print 'system_delete: Delete a system profile'
    print 'usage: system_delete <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_delete(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_delete(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_delete()
        return

    system_ids = []

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    # get the system ID for each system
    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: return

        system_ids.append(system_id)

    if not len(system_ids):
        logging.warning('No systems to delete')
        return

    # make the column the right size
    colsize = max_length([ self.get_system_name(s) for s in system_ids ])
    if colsize < 7: colsize = 7

    print '%s  System ID' % 'Profile'.ljust(colsize)
    print '%s  ---------' % ('-' * colsize)

    # print a summary for the user
    for system_id in system_ids:
        print '%s  %i' % \
              (self.get_system_name(system_id).ljust(colsize), system_id)

    if not self.user_confirm('Delete these systems [y/N]:'):
        return

    self.client.system.deleteSystems(self.session, system_ids)

    logging.info('Deleted %i system(s)', len(system_ids))

    # regenerate the system name cache
    self.generate_system_cache(True)

    # remove these systems from the SSM
    for s in systems:
        if s in self.ssm:
            self.ssm.remove(s)

####################

def help_system_lock(self):
    print 'system_lock: Lock a system'
    print 'usage: system_lock <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_lock(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_lock(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_lock()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.setLockStatus(self.session, system_id, True)

####################

def help_system_unlock(self):
    print 'system_unlock: Unlock a system'
    print 'usage: system_unlock <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_unlock(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_unlock(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_unlock()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.setLockStatus(self.session, system_id, False)

####################

def help_system_rename(self):
    print 'system_rename: Rename a system profile'
    print 'usage: system_rename OLDNAME NEWNAME'

def complete_system_rename(self, text, line, beg, end):
    if len(line.split(' ')) == 2:
        return tab_completer(self.get_system_names(), text)

def do_system_rename(self, args):
    (args, options) = parse_arguments(args)

    if len(args) != 2:
        self.help_system_rename()
        return

    (old_name, new_name) = args

    system_id = self.get_system_id(old_name)
    if not system_id: return

    print '%s (%s) -> %s' % (old_name, system_id, new_name)
    if not self.user_confirm(): return

    self.client.system.setProfileName(self.session,
                                      system_id,
                                      new_name)

    # regenerate the cache of systems
    self.generate_system_cache(True)

    # update the SSM
    if old_name in self.ssm:
        self.ssm.remove(old_name)
        self.ssm.append(new_name)

####################

def help_system_listcustomvalues(self):
    print 'system_listcustomvalues: List the custom values for a system'
    print 'usage: system_listcustomvalues <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listcustomvalues(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listcustomvalues(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listcustomvalues()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    add_separator = False

    for system in systems:
        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system
            print

        system_id = self.get_system_id(system)
        if not system_id: continue

        values = self.client.system.getCustomValues(self.session,
                                                    system_id)

        for v in values:
            print '%s = %s' % (v, values[v])

####################

def help_system_addcustomvalue(self):
    print 'system_addcustomvalue: Set a custom value for a system'
    print 'usage: system_addcustomvalue <SYSTEMS> KEY VALUE'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_addcustomvalue(self, text, line, beg, end):
    if len(line.split(' ')) == 2:
        return self.tab_complete_systems(text)
    elif len(line.split(' ')) == 3:
        return tab_completer(self.do_custominfo_listkeys('', True),
                                  text)

def do_system_addcustomvalue(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 3:
        self.help_system_addcustomvalue()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    key   = args[1]
    value = ' '.join(args[2:])

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.setCustomValues(self.session,
                                           system_id,
                                           {key : value})

####################

def help_system_updatecustomvalue(self):
    print 'system_updatecustomvalue: Update a custom value for a system'
    print 'usage: system_updatecustomvalue <SYSTEMS> KEY VALUE'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_updatecustomvalue(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) == 3:
        return tab_completer(self.do_custominfo_listkeys('', True),
                                  text)

def do_system_updatecustomvalue(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 3:
        self.help_system_updatecustomvalue()
        return

    return self.do_system_addcustomvalue(' '.join(args))

####################

def help_system_removecustomvalues(self):
    print 'system_removecustomvalues: Remove a custom value for a system'
    print 'usage: system_removecustomvalues <SYSTEMS> <KEY ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_removecustomvalues(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) == 3:
        return tab_completer(self.do_custominfo_listkeys('', True),
                                  text)

def do_system_removecustomvalues(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_removecustomvalues()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    keys = args[1:]

    if not self.user_confirm('Delete these values [y/N]:'): return

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.deleteCustomValues(self.session,
                                              system_id,
                                              keys)

####################

def help_system_addnote(self):
    print 'system_addnote: Set a note for a system'
    print '''usage: system_addnote <SYSTEM> [options]

options:
  -s SUBJECT
  -b BODY'''
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_addnote(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_addnote(self, args):
    options = [ Option('-s', '--subject', action='store'),
                Option('-b', '--body', action='store') ]

    (args, options) = parse_arguments(args, options)

    if len(args) < 1:
        self.help_system_addnote()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    if is_interactive(options):
        options.subject = prompt_user('Subject of the Note:', noblank = True)

        message = 'Note Body (ctrl-D to finish):'
        options.body = prompt_user(message, noblank = True, multiline = True)
    else:
        if not options.subject:
            logging.error('A subject is required')
            return

        if not options.body:
            logging.error('A body is required')
            return

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.addNote(self.session,
                                   system_id,
                                   options.subject,
                                   options.body)

####################

def help_system_deletenotes(self):
    print 'system_deletenotes: Delete notes from a system'
    print 'usage: system_deletenotes <SYSTEM> <ID|*>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_deletenotes(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_deletenotes(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listnotes()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    note_ids = args

    if not len(args):
        logging.warning('No notes to delete')
        return

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        if '.*' in note_ids:
            self.client.system.deleteNotes(self.session, system_id)
        else:
            for note_id in note_ids:
                try:
                    note_id = int(note_id)
                except ValueError:
                    logging.warning('%s is not a valid note ID' % note_id)
                    continue

                # deleteNote does not throw an exception
                self.client.system.deleteNote(self.session, system_id, note_id)

####################

def help_system_listnotes(self):
    print 'system_listnotes: List the available notes for a system'
    print 'usage: system_listnotes <SYSTEM>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listnotes(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listnotes(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listnotes()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    add_separator = False

    for system in sorted(systems):
        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system
            print

        system_id = self.get_system_id(system)
        if not system_id: continue

        notes = self.client.system.listNotes(self.session, system_id)

        for n in notes:
            print '%d. %s (%s)' % (n['id'], n['subject'], n['creator'])
            print n['note']
            print

####################

def help_system_setbasechannel(self):
    print "system_setbasechannel: Set a system's base software channel"
    print 'usage: system_setbasechannel <SYSTEMS> CHANNEL'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_setbasechannel(self, text, line, beg, end):
    if len(line.split(' ')) == 2:
        return self.tab_complete_systems(text)
    elif len(line.split(' ')) == 3:
        system = line.split(' ')[1]
        return tab_completer(self.list_base_channels(), text)

def do_system_setbasechannel(self, args):
    (args, options) = parse_arguments(args)

    if len(args) != 2:
        self.help_system_setbasechannel()
        return

    new_channel = args.pop()

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    add_separator = False

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        old = self.client.system.getSubscribedBaseChannel(self.session,
                                                          system_id)

        if add_separator: print self.SEPARATOR
        add_separator = True

        print 'System:           %s' % system
        print 'Old Base Channel: %s' % old.get('label')
        print 'New Base Channel: %s' % new_channel

    if not self.user_confirm(): return

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.setBaseChannel(self.session,
                                          system_id,
                                          new_channel)

####################

def help_system_listbasechannel(self):
    print 'system_listbasechannel: List the base channel for a system'
    print 'usage: system_listbasechannel <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listbasechannel(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listbasechannel(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listbasechannel()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system

        channel = \
            self.client.system.getSubscribedBaseChannel(self.session,
                                                        system_id)

        print channel.get('label')

####################

def help_system_listchildchannels(self):
    print 'system_listchildchannels: List the child channels for a system'
    print 'usage: system_listchildchannels <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listchildchannels(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listchildchannels(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listchildchannels()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system

        channels = \
            self.client.system.listSubscribedChildChannels(self.session,
                                                           system_id)

        print '\n'.join(sorted([ c.get('label') for c in channels ]))

####################

def help_system_addchildchannels(self):
    print "system_addchildchannels: Add child channels to a system"
    print 'usage: system_addchildchannels <SYSTEMS> <CHANNEL ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_addchildchannels(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.list_child_channels(), text)

def do_system_addchildchannels(self, args):
    self.manipulate_child_channels(args)

####################

def help_system_removechildchannels(self):
    print "system_removechildchannels: Remove child channels from a system"
    print 'usage: system_removechildchannels <SYSTEMS> <CHANNEL ...>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_removechildchannels(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return tab_completer(self.list_child_channels(), text)

def do_system_removechildchannels(self, args):
    self.manipulate_child_channels(args, True)

####################

def help_system_details(self):
    print 'system_details: Show the details of a system profile'
    print 'usage: system_details <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_details(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_details(self, args, short=False):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_details()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        last_checkin = \
            self.client.system.getName(self.session,
                                       system_id).get('last_checkin')

        details = self.client.system.getDetails(self.session, system_id)

        registered = self.client.system.getRegistrationDate(self.session,
                                                            system_id)

        if add_separator: print self.SEPARATOR
        add_separator = True

        print 'Name:          %s' % system
        print 'System ID:     %i' % system_id
        print 'Locked:        %s' % details.get('lock_status')
        print 'Registered:    %s' % registered
        print 'Last Checkin:  %s' % last_checkin
        print 'OSA Status:    %s' % details.get('osa_status')

        # only print basic information if requested
        if short: continue

        network = self.client.system.getNetwork(self.session, system_id)

        entitlements = self.client.system.getEntitlements(self.session,
                                                          system_id)

        base_channel = \
            self.client.system.getSubscribedBaseChannel(self.session,
                                                        system_id)

        child_channels = \
            self.client.system.listSubscribedChildChannels(self.session,
                                                           system_id)

        groups = self.client.system.listGroups(self.session,
                                               system_id)

        kernel = self.client.system.getRunningKernel(self.session,
                                                     system_id)

        keys = self.client.system.listActivationKeys(self.session,
                                                     system_id)

        ranked_config_channels = []
        if 'provisioning_entitled' in entitlements:
            config_channels = \
                self.client.system.config.listChannels(self.session,
                                                       system_id)

            for channel in config_channels:
                ranked_config_channels.append(channel.get('label'))

        print
        print 'Hostname:      %s' % network.get('hostname')
        print 'IP Address:    %s' % network.get('ip')
        print 'Kernel:        %s' % kernel

        if len(keys):
            print
            print 'Activation Keys'
            print '---------------'
            print '\n'.join(sorted(keys))

        print
        print 'Software Channels'
        print '-----------------'
        print base_channel.get('label')

        for channel in child_channels:
            print '  |-- %s' % channel.get('label')

        if len(ranked_config_channels):
            print
            print 'Configuration Channels'
            print '----------------------'
            print '\n'.join(ranked_config_channels)

        print
        print 'Entitlements'
        print '------------'
        print '\n'.join(sorted(entitlements))

        if len(groups):
            print
            print 'System Groups'
            print '-------------'
            for group in groups:
                if group.get('subscribed') == 1:
                    print group.get('system_group_name')

####################

def help_system_listerrata(self):
    print 'system_listerrata: List available errata for a system'
    print 'usage: system_listerrata <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listerrata(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listerrata(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listerrata()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system
            print

        errata = self.client.system.getRelevantErrata(self.session,
                                                      system_id)

        print_errata_list(errata)

####################

def help_system_applyerrata(self):
    print 'system_applyerrata: Apply errata to a system'
    print 'usage: system_applyerrata <SYSTEMS> [ERRATA|search:XXX ...]'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_applyerrata(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return self.tab_complete_errata(text)

def do_system_applyerrata(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_applyerrata()
        return

    # use the systems applyed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args.pop(0))

    # allow globbing and searching of errata
    errata_list = self.expand_errata(args)

    if not len(errata_list) or not len(systems):
        return

    return self.do_errata_apply(' '.join(errata_list), systems)

####################

def help_system_listevents(self):
    print 'system_listevents: List the event history for a system'
    print 'usage: system_listevents <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listevents(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listevents(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listevents()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    add_separator = False

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system

        events = self.client.system.getEventHistory(self.session, system_id)

        for e in events:
            print
            print 'Summary:   %s' % e.get('summary')
            print 'Completed: %s' % e.get('completed')
            print 'Details:   %s' % e.get('details')

####################

def help_system_listentitlements(self):
    print 'system_listentitlements: List the entitlements for a system'
    print 'usage: system_listentitlements <SYSTEMS>'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_listentitlements(self, text, line, beg, end):
    return self.tab_complete_systems(text)

def do_system_listentitlements(self, args):
    (args, options) = parse_arguments(args)

    if not len(args):
        self.help_system_listentitlements()
        return

    add_separator = False

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in sorted(systems):
        system_id = self.get_system_id(system)
        if not system_id: return

        if add_separator: print self.SEPARATOR
        add_separator = True

        if len(systems) > 1:
            print 'System: %s' % system

        entitlements = self.client.system.getEntitlements(self.session,
                                                          system_id)

        print '\n'.join(sorted(entitlements))

####################

def help_system_addentitlements(self):
    print 'system_addentitlements: Add entitlements to a system'
    print 'usage: system_addentitlements <SYSTEMS> ENTITLEMENT'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_addentitlements(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    else:
        return tab_completer(self.ENTITLEMENTS, text)

def do_system_addentitlements(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_addentitlements()
        return

    entitlement = args.pop()

    for e in self.ENTITLEMENTS:
        if re.match(entitlement, e, re.I):
            entitlement = e
            break

    # use the systems applyed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.addEntitlements(self.session,
                                           system_id,
                                           [entitlement])

####################

def help_system_removeentitlement(self):
    print 'system_removeentitlement: Remove an entitlement from a system'
    print 'usage: system_removeentitlement <SYSTEMS> ENTITLEMENT'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_removeentitlement(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    else:
        return tab_completer(self.ENTITLEMENTS, text)

def do_system_removeentitlement(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_removeentitlement()
        return

    entitlement = args.pop()

    for e in self.ENTITLEMENTS:
        if re.match(entitlement, e, re.I):
            entitlement = e
            break

    # use the systems applyed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
    else:
        systems = self.expand_systems(args)

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        self.client.system.removeEntitlements(self.session,
                                              system_id,
                                              [entitlement])

####################

def help_system_listpackageprofiles(self):
    print 'system_listpackageprofiles: List all package profiles'
    print 'usage: system_listpackageprofiles'

def do_system_listpackageprofiles(self, args, doreturn=False):
    profiles = self.client.system.listPackageProfiles(self.session)
    profiles = [ p.get('name') for p in profiles ]

    if doreturn:
        return profiles
    else:
        if len(profiles):
            print '\n'.join(sorted(profiles))

####################

def help_system_deletepackageprofile(self):
    print 'system_deletepackageprofile: Delete a package profile'
    print 'usage: system_deletepackageprofile PROFILE'

def complete_system_deletepackageprofile(self, text, line, beg, end):
    parts = shlex.split(line)
    if line[-1] == ' ': parts.append('')

    if len(parts) == 2:
        return self.tab_complete_systems(\
                   self.do_system_listpackageprofiles('', True), text)

def do_system_deletepackageprofile(self, args):
    if not len(args):
        self.help_system_deletepackageprofile()
        return

    label = args

    if not self.user_confirm('Delete this profile [y/N]:'): return

    all_profiles = self.client.system.listPackageProfiles(self.session)

    profile_id = 0
    for profile in all_profiles:
        if label == profile.get('name'):
            profile_id = profile.get('id')

    if not profile_id:
        logging.warning('%s is not a valid profile' % label)
        return

    self.client.system.deletePackageProfile(self.session, profile_id)

####################

def help_system_createpackageprofile(self):
    print 'system_createpackageprofile: Create a package profile'
    print '''usage: system_createpackageprofile SYSTEM [options]

options:
  -n NAME
  -d DESCRIPTION'''

def complete_system_createpackageprofile(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) == 2:
        return self.tab_complete_systems(text)

def do_system_createpackageprofile(self, args):
    options = [ Option('-n', '--name', action='store'),
                Option('-d', '--description', action='store') ]

    (args, options) = parse_arguments(args, options)

    if len(args) != 1:
        self.help_system_createpackageprofile()
        return

    system_id = self.get_system_id(args[0])
    if not system_id:
        logging.error('Invalid system')
        return

    if is_interactive(options):
        options.name = prompt_user('Profile Label:', noblank = True)
        options.description = prompt_user('Description:', multiline = True)
    else:
        if not options.name:
            logging.error('A profile name is required')
            return

        if not options.description:
            logging.error('A profile description is required')
            return

    results = self.client.system.createPackageProfile(self.session,
                                                      system_id,
                                                      options.name,
                                                      options.description)

    logging.info("Created package profile '%s'" % options.name)

####################

def help_system_comparepackageprofile(self):
    print 'system_comparepackageprofile: Compare a system against a ' + \
          'package profile'
    print 'usage: system_comparepackageprofile <SYSTEMS> PROFILE'
    print
    print self.HELP_SYSTEM_OPTS

def complete_system_comparepackageprofile(self, text, line, beg, end):
    parts = shlex.split(line)
    if line[-1] == ' ': parts.append('')

    if len(parts) == 2:
        return self.tab_complete_systems(text)
    elif len(parts) > 2:
        return self.tab_complete_systems(\
                   self.do_system_listpackageprofiles('', True), parts[-1])

def do_system_comparepackageprofile(self, args):
    (args, options) = parse_arguments(args)

    if len(args) < 2:
        self.help_system_comparepackageprofile()
        return

    # use the systems listed in the SSM
    if re.match('ssm', args[0], re.I):
        systems = self.ssm.keys()
        args.pop(0)
    else:
        systems = self.expand_systems(args[:-1])

    profile = args[-1]

    add_separator = False

    for system in systems:
        system_id = self.get_system_id(system)
        if not system_id: continue

        results = self.client.system.comparePackageProfile(self.session,
                                                           system_id,
                                                           profile)

        if add_separator: print self.SEPARATOR
        add_separator = True

        print '%s:' % system
        self.print_package_comparison(results)

####################

def help_system_comparepackages(self):
    print 'system_comparepackages: Compare the packages between two systems'
    print 'usage: system_comparepackages SOME_SYSTEM ANOTHER_SYSTEM'

def complete_system_comparepackages(self, text, line, beg, end):
    parts = line.split(' ')

    if len(parts) < 3:
        return self.tab_complete_systems(text)

def do_system_comparepackages(self, args):
    (args, options) = parse_arguments(args)

    if len(args) != 2:
        self.help_system_comparepackages()
        return

    this_system = self.get_system_id(args[0])
    other_system = self.get_system_id(args[1])

    results = self.client.system.comparePackages(self.session,
                                                 this_system,
                                                 other_system)

    self.print_package_comparison(results)

# vim:ts=4:expandtab:
