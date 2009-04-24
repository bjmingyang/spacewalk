Name: spacewalk-web
Summary: Spacewalk Web site packages
Group: Applications/Internet
License: GPLv2
Version: 0.6.4
Release: 1%{?dist}
URL:          https://fedorahosted.org/spacewalk
Source0:      https://fedorahosted.org/releases/s/p/spacewalk/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 
BuildArch: noarch
BuildRequires: perl(ExtUtils::MakeMaker)

%description
This package contains the code for the Spacewalk Web Site.
Normally this source rpm does not generate a %{name} binary package,
but it does generate a number of subpackages

%package -n spacewalk-html
Summary: HTML document files for Spacewalk
Group: Applications/Internet
Requires: webserver
Requires: spacewalk-branding
Obsoletes: rhn-help < 5.3.0
Provides: rhn-help = 5.3.0
Obsoletes: rhn-html < 5.3.0
Provides: rhn-html = 5.3.0


%description -n spacewalk-html
This package contains the HTML files for the Spacewalk web site.


%package -n spacewalk-base
Group: Applications/Internet
Summary: Programs needed to be installed on the RHN Web base classes
Requires: spacewalk-pxt
Provides: spacewalk(spacewalk-base-minimal) = %{version}-%{release}
Provides: spacewalk(spacewalk-base) = %{version}-%{release}
Requires: webserver
Obsoletes: rhn-base < 5.3.0
Provides: rhn-base = 5.3.0


%description -n spacewalk-base
This package includes the core RHN:: packages necessary to manipulate
database.  This includes RHN::* and RHN::DB::*


%package -n spacewalk-base-minimal
Summary: Minimal .pm's for %{name} package
Group: Applications/Internet 
Provides: spacewalk(spacewalk-base-minimal) = %{version}-%{release}
Obsoletes: rhn-base-minimal < 5.3.0
Provides: rhn-base-minimal = 5.3.0

%description -n spacewalk-base-minimal
Independent perl modules in the RHN:: namespace.

%package -n spacewalk-dobby
Summary: Perl modules and scripts to administer an Oracle database
Group: Applications/Internet
Requires: spacewalk-base
Obsoletes: rhn-dobby < 5.3.0
Provides: rhn-dobby = 5.3.0

%description -n spacewalk-dobby
Dobby is collection of perl modules and scripts to administer an Oracle
database.


%package -n spacewalk-cypress
Summary: Cypress, a collection of Grail applications for Red Hat Network
Group: Applications/Internet
Obsoletes: rhn-cypress < 5.3.0
Provides: rhn-cypress = 5.3.0

%description -n spacewalk-cypress
Cypress is a collection of Components for Grail.

%package -n spacewalk-grail
Summary: Grail, a component framework for Red Hat Network
Requires: spacewalk-base
Group: Applications/Internet
Obsoletes: rhn-grail < 5.3.0
Provides: rhn-grail = 5.3.0

%description -n spacewalk-grail
A component framework for Spacewalk.


%package -n spacewalk-pxt
Summary: The PXT library for web page templating
Group: Applications/Internet
Requires: spacewalk(spacewalk-base-minimal)
Obsoletes: rhn-pxt < 5.3.0
Provides:  rhn-pxt = 5.3.0

%description -n spacewalk-pxt
This package is the core software of the new Spacewalk site.  It is responsible
for HTML, XML, WML, HDML, and SOAP output of data.  It is more or less
equlivalent to things like Apache::ASP and Mason


%package -n spacewalk-sniglets
Group: Applications/Internet 
Summary: PXT Tag handlers
Requires: mod_perl >= 2.0.0
%if 0%{?rhel} == 4
Requires: mod_jk-ap20
%else
Requires: httpd
%endif
Obsoletes: rhn-sniglets < 5.3.0
Provides:  rhn-sniglets = 5.3.0

%description -n spacewalk-sniglets
This package contains the tag handlers for the PXT templates


%package -n spacewalk-moon
Group: Applications/Internet  
Summary: The Moon library for manipulating and charting data
Obsoletes: rhn-moon < 5.3.0
Provides:  rhn-moon = 5.3.0

%description -n spacewalk-moon
Modules for loading, manipulating, and rendering graphed data.

%prep
%setup -q

%build
make -f Makefile.spacewalk-web PERLARGS="INSTALLDIRS=vendor"

%install
rm -rf $RPM_BUILD_ROOT
make -C modules install DESTDIR=$RPM_BUILD_ROOT PERLARGS="INSTALLDIRS=vendor"
make -C html install PREFIX=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT -type f -name perllocal.pod -exec rm -f {} \;
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} \;

mkdir -p $RPM_BUILD_ROOT/%{_var}/www/html/pub
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rhn/default
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/init.d
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/cron.daily

install -m 644 conf/rhn_web.conf $RPM_BUILD_ROOT/%{_sysconfdir}/rhn/default
install -m 644 conf/rhn_dobby.conf $RPM_BUILD_ROOT/%{_sysconfdir}/rhn/default
install -m 755 modules/dobby/scripts/check-oracle-space-usage.sh $RPM_BUILD_ROOT/%{_sysconfdir}/cron.daily/check-oracle-space-usage.sh


%clean
rm -rf $RPM_BUILD_ROOT

%files -n spacewalk-base
%defattr(644,root,root,755)
%dir %{perl_vendorlib}/RHN
%dir %{perl_vendorlib}/PXT
%{perl_vendorlib}/RHN.pm
%{perl_vendorlib}/RHN/API/
%{perl_vendorlib}/RHN/Access.pm
%{perl_vendorlib}/RHN/Access/
%{perl_vendorlib}/RHN/Action.pm
%{perl_vendorlib}/RHN/AppInstall/
%{perl_vendorlib}/RHN/Cache/
%{perl_vendorlib}/RHN/Catalog.pm
%{perl_vendorlib}/RHN/Cert.pm
%{perl_vendorlib}/RHN/Channel.pm
%{perl_vendorlib}/RHN/ChannelEditor.pm
%{perl_vendorlib}/RHN/Cleansers.pm
%{perl_vendorlib}/RHN/Command.pm
%{perl_vendorlib}/RHN/CommandParameter.pm
%{perl_vendorlib}/RHN/ConfigChannel.pm
%{perl_vendorlib}/RHN/ConfigFile.pm
%{perl_vendorlib}/RHN/ConfigRevision.pm
%{perl_vendorlib}/RHN/ContactGroup.pm
%{perl_vendorlib}/RHN/ContactMethod.pm
%{perl_vendorlib}/RHN/CryptoKey.pm
%{perl_vendorlib}/RHN/CustomInfoKey.pm
%{perl_vendorlib}/RHN/DB/
%{perl_vendorlib}/RHN/Daemon.pm
%{perl_vendorlib}/RHN/DataSource.pm
%{perl_vendorlib}/RHN/DataSource/
%{perl_vendorlib}/RHN/Date.pm
%{perl_vendorlib}/RHN/EmailAddress.pm
%{perl_vendorlib}/RHN/Entitlements.pm
%{perl_vendorlib}/RHN/Errata.pm
%{perl_vendorlib}/RHN/ErrataEditor.pm
%{perl_vendorlib}/RHN/ErrataMailer.pm
%{perl_vendorlib}/RHN/ErrataTmp.pm
%{perl_vendorlib}/RHN/FileList.pm
%{perl_vendorlib}/RHN/Form.pm
%{perl_vendorlib}/RHN/Form/
%{perl_vendorlib}/RHN/Grail.pm
%{perl_vendorlib}/RHN/I18N.pm
%{perl_vendorlib}/RHN/KSTree.pm
%{perl_vendorlib}/RHN/Kickstart.pm
%{perl_vendorlib}/RHN/Kickstart/
%{perl_vendorlib}/RHN/Mail.pm
%{perl_vendorlib}/RHN/Manifest.pm
%{perl_vendorlib}/RHN/Message.pm
%{perl_vendorlib}/RHN/MonitoringConfigMacro.pm
%{perl_vendorlib}/RHN/Org.pm
%{perl_vendorlib}/RHN/Package.pm
%{perl_vendorlib}/RHN/Package/
%{perl_vendorlib}/RHN/Postal.pm
%{perl_vendorlib}/RHN/Probe.pm
%{perl_vendorlib}/RHN/ProbeParam.pm
%{perl_vendorlib}/RHN/Product.pm
%{perl_vendorlib}/RHN/Profile.pm
%{perl_vendorlib}/RHN/ProxyInstall.pm
%{perl_vendorlib}/RHN/SCDB.pm
%{perl_vendorlib}/RHN/SatCluster.pm
%{perl_vendorlib}/RHN/SatInstall.pm
%{perl_vendorlib}/RHN/SatNode.pm
%{perl_vendorlib}/RHN/SatelliteCert.pm
%{perl_vendorlib}/RHN/Scheduler.pm
%{perl_vendorlib}/RHN/Search.pm
%{perl_vendorlib}/RHN/SearchTypes.pm
%{perl_vendorlib}/RHN/Server.pm
%{perl_vendorlib}/RHN/ServerActions.pm
%{perl_vendorlib}/RHN/ServerGroup.pm
%{perl_vendorlib}/RHN/ServerMessage.pm
%{perl_vendorlib}/RHN/ServerNotes.pm
%{perl_vendorlib}/RHN/ServerPackage.pm
%{perl_vendorlib}/RHN/Session.pm
%{perl_vendorlib}/RHN/Set.pm
%{perl_vendorlib}/RHN/SimpleStruct.pm
%{perl_vendorlib}/RHN/StoredMessage.pm
%{perl_vendorlib}/RHN/SystemSnapshot.pm
%{perl_vendorlib}/RHN/TSDB.pm
%{perl_vendorlib}/RHN/Tag.pm
%{perl_vendorlib}/RHN/TemplateString.pm
%{perl_vendorlib}/RHN/TextMessage.pm
%{perl_vendorlib}/RHN/TinyURL.pm
%{perl_vendorlib}/RHN/Token.pm
%{perl_vendorlib}/RHN/TokenGen/
%{perl_vendorlib}/RHN/User.pm
%{perl_vendorlib}/RHN/UserActions.pm
%{perl_vendorlib}/RHN/UserGroup.pm
%{perl_vendorlib}/RHN/Utils.pm
%{_mandir}/man3/RHN::Command.3pm.gz
%{_mandir}/man3/RHN::CommandParameter.3pm.gz
%{_mandir}/man3/RHN::ContactGroup.3pm.gz
%{_mandir}/man3/RHN::ContactMethod.3pm.gz
%{_mandir}/man3/RHN::DB::Command.3pm.gz
%{_mandir}/man3/RHN::DB::CommandParameter.3pm.gz
%{_mandir}/man3/RHN::DB::ContactGroup.3pm.gz
%{_mandir}/man3/RHN::DB::ContactMethod.3pm.gz
%{_mandir}/man3/RHN::DB::MonitoringConfigMacro.3pm.gz
%{_mandir}/man3/RHN::DB::Probe.3pm.gz
%{_mandir}/man3/RHN::DB::ProbeParam.3pm.gz
%{_mandir}/man3/RHN::DB::SatCluster.3pm.gz
%{_mandir}/man3/RHN::DB::SatNode.3pm.gz
%{_mandir}/man3/RHN::DB::ServerGroup.3pm.gz
%{_mandir}/man3/RHN::MonitoringConfigMacro.3pm.gz
%{_mandir}/man3/RHN::Probe.3pm.gz
%{_mandir}/man3/RHN::ProbeParam.3pm.gz
%{_mandir}/man3/RHN::SCDB.3pm.gz
%{_mandir}/man3/RHN::SatCluster.3pm.gz
%{_mandir}/man3/RHN::SatNode.3pm.gz
%{_mandir}/man3/RHN::Session.3pm.gz
%{_mandir}/man3/RHN::TSDB.3pm.gz

%files -n spacewalk-base-minimal
%defattr(644,root,root,755)
%dir %{perl_vendorlib}/RHN
%dir %{perl_vendorlib}/PXT
%{perl_vendorlib}/RHN/SessionSwap.pm
%{perl_vendorlib}/RHN/Exception.pm
%{perl_vendorlib}/RHN/DB.pm
%{perl_vendorlib}/PXT/Config.pm
%attr(640,root,apache) %config %{_sysconfdir}/rhn/default/rhn_web.conf

%files -n spacewalk-cypress 
%defattr(644,root,root,755)
%{perl_vendorlib}/Cypress.pm
%{perl_vendorlib}/Cypress/

%files -n spacewalk-dobby
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/db-control
%{_mandir}/man1/db-control.1.gz
%{perl_vendorlib}/Dobby.pm
%attr(640,root,apache) %config %{_sysconfdir}/rhn/default/rhn_dobby.conf
%attr(0755,root,root) %{_sysconfdir}/cron.daily/check-oracle-space-usage.sh
%{perl_vendorlib}/Dobby/

%files -n spacewalk-grail
%defattr(644,root,root,755)
%{perl_vendorlib}/Grail.pm
%{perl_vendorlib}/Grail/

%files -n spacewalk-pxt 
%defattr(644,root,root,755)
%{perl_vendorlib}/PXT.pm
%attr(640,root,apache) %config %{_sysconfdir}/rhn/default/rhn_web.conf
%{perl_vendorlib}/PXT/
%{_mandir}/man3/PXT::ApacheHandler.3pm.gz

%files -n spacewalk-sniglets 
%defattr(644,root,root,755)
%{perl_vendorlib}/Sniglets.pm
%{perl_vendorlib}/Sniglets/

%files -n spacewalk-moon
%defattr(644,root,root,755)
%{perl_vendorlib}/Moon/
%{_mandir}/man3/Moon*

%files -n spacewalk-html
%defattr(644,root,root,755)
%{_var}/www/html/*
%{_var}/www/html/.htaccess

# $Id$
%changelog
* Fri Apr 24 2009 jesus m. rodriguez <jesusr@redhat.com> 0.6.4-1
- 485981 - fix web proxy installer help links (bbuckingham@redhat.com)

* Wed Apr 22 2009 jesus m. rodriguez <jesusr@redhat.com> 0.6.3-1
- 485020 - errata clone names consistent in perl/java (jsherril@redhat.com)
- 474567 - Stop running commands on SSM systems that don't have provisioning. (dgoodwin@redhat.com)
- 436851 - Removed dead references (jason.dobies@redhat.com)
- 496710 - system.listSystemEvents - convert dates in return to use Date (bbuckingham@redhat.com)
- 496214 - Fix About links in Perl sitenav. (dgoodwin@redhat.com)

* Fri Apr 17 2009 Devan Goodwin <dgoodwin@redhat.com> 0.6.2-1
- 496161 - removing find a system box from system group details page
  (jsherril@redhat.com)
- 476248 - add correct lang to proxy install guide url (jesusr@redhat.com)
- 494450 - api - add permissions_mode to ConfigRevisionSerializer & fix doc on
  system.config.createOrUpdatePath (bbuckingham@redhat.com)

* Thu Apr 16 2009 jesus m. rodriguez <jesusr@redhat.com> 0.6.1-1
- remove Proxy Release Notes link and unused Developer's area. (jesusr@redhat.com)
- 494714 - fixing 404 after cloning channel with selective errata (jsherril@redhat.com)
- 484294 - can't delete channel with distros (paji@redhat.com)
- 495722 - fixing issue where /ty/TOKEn wasnt being rendered properly (jsherril@redhat.com)
- 490904 - change all references to /rhn/help/*/en/ -> /rhn/help/*/en-US/ (jesusr@redhat.com)
- api doclet - enhanced to support a 'since' tag, tagged snapshot apis and
  bumped api version (bbuckingham@redhat.com)
- 494475,460136 - remove faq & feedback code which used customerservice emails. (jesusr@redhat.com)
- Revert "484702 - remove dead function generate_server_pem from RHN::SatInstall." (mzazrivec@redhat.com)
- Revert "484703 - remove dead function generate_satcon_dict from RHN::SatInstall." (mzazrivec@redhat.com)
- Revert "484705 - remove dead function satcon_deploy from RHN::SatInstall." (mzazrivec@redhat.com)
- bump Versions to 0.6.0 (jesusr@redhat.com)

* Thu Mar 26 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.23-1
- 489736 - generate non-expiring kickstart package download url
- 489736 - download_url_lifetime of 0 disables expiration server wide
- 489736 - can disable experiation by package name by non_expirable_package_urls

* Thu Mar 26 2009 Miroslav Suchy <msuchy@redhat.com> 0.5.22-1
- 491667 - do not fail if none of the packages are installed
- code cleanup - remove 3.6 and 3.7 proxy installer (EOL)
- 491670 - add rhn-proxy-branding to list of package to remove in 5.3
- 491670 - add conflicting package from older proxy versions
- remove libidn from conflictin packages from proxy installer

* Wed Mar 25 2009 Jan Pazdziora 0.5.20-1
- 491687 - call wrapper around sudo invocations, to change SELinux domain

* Fri Mar 20 2009 Mike McCune <mmccune@gmail.com> 0.5.19-1
- space05 - bumping release footer/config for 0.5 release

* Thu Mar 19 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.18-1
- 472595 - fixes for kickstart performance, start of porting ks downloads to java
- 490726 - minor updates to about.pxt
- added support for db-control extend TEMP_TBS
- 466502 - fixes issues related to repo command addition and proper ks url generation

* Thu Mar 12 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.17-1
- forgot to remove an alert, arg

* Wed Mar 11 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.16-1
- 249459 - fixing issue where org trust page was busted
- 481236 - fix issue where rewrite was not being inherited by virtual host, making package downloads didn't work
- 483287 - Added ability to do a cobbler sync thru the UI
- 465775 - adding synopsis to errata clone page
- Use /usr/sbin/rhn-satellite for restart
- Revert "code cleanup - enable_notification_cron and disable_notification_ cron are not used any more" 

* Thu Mar 05 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.15-1
- 487563 - switching take_snapshots to enable_snapshots
- 193788 - converting a few pages to java, so we can sort better
- 459827 - mention the 64 character limit.
- 485497 - adding IQ back to t6 list
- 487563 - adding on/off switch for snapshots

* Thu Feb 26 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.14-1
- rebuild

* Thu Feb 19 2009 Miroslav Suchy <msuchy@redhat.com> 0.5.13-1
- fix proxy webui installer 

* Thu Feb 19 2009 Jan Pazdziora 0.5.12-1
- 479742 - changes to make doc links from Help and About pages configurable (Brad B.)
- 486057 - reworked proxy install xml file for 530 support (Shannon H.)
- 485878 - missing options in db-control.1 (Milan Z.)
- 485985 - remove references to obsolete package rhns-proxy-management (Shannon H.)
- 484717 - remove dead function store_ssl_cert from RHN::SatInstall
- 484709 - remove dead function sat_sync from RHN::SatInstall
- 484705 - remove dead function satcon_deploy from RHN::SatInstall
- 484703 - remove dead function generate_satcon_dict from RHN::SatInstall
- 484702 - remove dead function generate_server_pem from RHN::SatInstall
- 484701 - remove dead function deploy_ca_cert from RHN::SatInstall
- 484685 - remove dead function install_server_cert from RHN::SatInstall
- 484681 - remove dead function populate_tablespace_name from RHN::SatInstall
- 484699 - remove dead function populate_database from RHN::SatInstall
- 484680 - remove dead function write_tnsnames from RHN::SatInstall
- code cleanup: remove acl="global_config(satellite)" (Miroslav S.)
- code cleanup - remove unreachable pages (old hosted content) (Miroslav S.)

* Mon Feb 16 2009 Pradeep Kilambi <pkilambi@redhat.com> 0.5.11-1
- yum repodata regen changes to taskomatic
 
* Thu Feb 12 2009 Jan Pazdziora 0.5.10-1
- code cleanup - enable_notification_cron, disable_notification_cron,
  monitoring_available are not used any more (Miroslav S.)
- 483798 - added index.pxt to catch redirect to perl files, and
  direct to the docs base page (about.pxt) (Jason D.)
- 482926 - fixed webui proxy activation (Shannon H.)
- 484481 - 2nd part of errata cloning patch, with modification to pull
  in all but the first two characters (Justin S.)
- 484481 - patch to make errata clone names more consistent ((Justin S.)
- 426472 - replacing grep | awk with awk
- 483606 - incorporated UI feedback and moved link to status to leftnav,
  making each status filter its own context tab (Jason D.)

* Thu Feb 05 2009 jesus m. rodriguez <jesusr@redhat.com> 0.5.9-1
- 483603 - First pass at display of async SSM operations in the UI

* Wed Feb 04 2009 Devan Goodwin <dgoodwin@redhat.com> 0.5.8-1
- Remove favicon.ico. (moved to branding rpm)

* Fri Jan 30 2009 Miroslav Suchý <msuchy@redhat.com> 0.5.7-1
- 483058 - subscribe to proxy channel if requested

* Thu Jan 29 2009 Miroslav Suchý <msuchy@redhat.com> 0.5.6-1
- 482926 - fix proxy webui installer

* Wed Jan 28 2009 Dennis Gilmore <dennis@ausil.us> 0.5.4-1
- use %%files correctly
- make sure perl modules get installed in %%{perl_vendorlib}
- add provides for Obsoletes

* Thu Jan 22 2009 Miroslav Suchý <msuchy@redhat.com> 0.5.3-1
- 468180 - warn that after proxy deactivation user should run rhn_check

* Wed Jan 21 2009 Miroslav Suchý <msuchy@redhat.com> 0.5.2-1
- 480894 - add to Channel.pm 5.3 channels

* Tue Jan 20 2009 Miroslav Suchý <msuchy@redhat.com> 0.5.1-1
- add proxy 5.3 webui installer
- 480328 - rhn-proxy is not service any more

* Thu Jan 15 2009 Jan Pazdziora 0.4.18-1
- 479948 - add missing use RHN::Mail

* Mon Jan 12 2009 Mike McCune <mmccune@gmail.com> 0.4.17-1
- adding editarea as reqquired by Colin.Coe@woodside.com.au's patches coming up.
- 479738 - update Help to point to the help page
- 479600 - fixed typo

* Mon Jan 12 2009 Michael Mraka <michael.mraka@redhat.com> 0.4.16-1
- resolved #479600

* Thu Jan 08 2009 Mike McCune <mmccune@gmail.com> 0.4.15-1
- spacewalk-httpd removal and latest changes

* Wed Jan  7 2009 Michael Mraka <michael.mraka@redhat.com> 0.4.14-1
- fixed db-control shrink-segments

* Mon Dec 22 2008 Michael Mraka <michael.mraka@redhat.com> 0.4.13-1
- added product_name branding

* Thu Dec 18 2008 Jan Pazdziora 0.4.12-1
- 461162 - adding support for cobbler auth for taskomatic that actually works
- more fixes for the $sth variable

* Thu Dec 18 2008 Jan Pazdziora 0.4.10-1
- WebUI will report Spacewalk release 0.4
- fixing duplicated $sth variable

* Wed Dec 17 2008 Jesus M. Rodriguez <jesusr@redhat.com> 0.4.9-1
- 476893 - update perl package verify access query to be multiorg aware
- 461593 - fixing web site nav for package details

* Wed Dec 17 2008 Miroslav Suchý <msuchy@redhat.com> 0.4.8-1
- 226915 - db_name can be different from db instance name

* Wed Dec 17 2008 Miroslav Suchy <msuchy@redhat.com> 0.4.7-1
- 476812 - monitoring should be aware of multiorg

* Mon Dec  8 2008 Michael Mraka <michael.mraka@redhat.com> 0.4.6-1
- resolved #474545 - fixed Obsoletes

* Fri Nov 28 2008 Michael Mraka <michael.mraka@redhat.com> 0.4.5-1
- removed rhn-database
- resolved #472563 - fidex error in db-control extend

* Thu Nov 20 2008 Miroslav Suchy <msuchy@redhat.com> 0.4.2-1
- 472346 - Bump up API version and make the versioning independent on web.version

* Wed Oct 29 2008 Michael Mraka <michael.mraka@redhat.com> 0.3.4-1
- resolved #468153 - fixed in, out fd handling

* Thu Oct 23 2008 Michael Mraka <michael.mraka@redhat.com> 0.3.3-1
- fixed #467877 - use runuser instead of su
- fixed #467512 - db-control man page

* Wed Sep 24 2008 Milan Zazrivec 0.3.1-1
- bumped versions for spacewalk 0.3
- fixed package obsoletes

* Wed Sep  3 2008 Mike McCune 0.2.3-1
- bumping rhn_web.conf version to 0.2

* Fri Aug 29 2008 Jesus M. Rodriguez <jesusr@redhat.com 0.2.2-1
- fix release
- remove remnants of test-conn

* Wed Aug 13 2008 Mike McCune <mmccune@redhat.com 0.2-1
- fix Requires: statement to reflect new spacewalk-pxt name 

* Mon Aug  4 2008 Miroslav Suchy <msuchy@redhat.com> 0.2-0
- rename package from rhn-* to spacewalk-*
- clean up spec

* Fri Jun  6 2008 Miroslav Suchy <msuchy@redhat.com> - 5.2.0-10
- add support for proxy on RHEL5

* Wed May 21 2008 Jan Pazdziora 5.2.0-7
- changing perl-Time-HiRes to perl(Time::HiRes)
- changing mod_jk-ap20 to mod_proxy_ajp.so on RHEL 5

* Tue May 20 2008 Michael Mraka <michael.mraka@redhat.com> 5.2.0-5
- added stats options to db-control

* Fri May 16 2008 Jan Pazdziora - 5.2.0-4
- rebuilt with latest code

* Wed Apr 30 2008 Jan Pazdziora <jpazdziora@redhat.com> 5.2.0-3
- rebuilt via brew / dist-cvs

* Thu Sep  6 2007 Jan Pazdziora <jpazdziora@redhat.com>
- updated to use default httpd from distribution and mod_perl 2

* Mon May 1 2006 Partha Aji <paji@redhat.com>
- Added a cron job that checks the oracle table/space usage and emails it to the user. (Bug 182054)

* Mon Nov  7 2005 Robin Norwood <rnorwood@redhat.com>
- Remove rhn-swab, because it annoys taw

* Thu Aug  8 2002 Cristian Gafton <gafton@redhat.com>
- unified all web stuff into a single src.rpm

* Thu Mar 14 2002 Chip Turner <cturner@minbar.devel.redhat.com>
- updated for the new bs

* Thu Jun 21 2001 Cristian Gafton <gafton@redhat.com>
- build system changes

* Mon Jun  4 2001 Cristian Gafton <gafton@redhat.com>
- created first package
