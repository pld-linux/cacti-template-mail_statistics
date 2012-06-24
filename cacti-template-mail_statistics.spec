%define		template	postfix
%include	/usr/lib/rpm/macros.perl
Summary:	Postifix monitoring with Cacti
Name:		cacti-template-%{template}
Version:	0.1
Release:	0.4
License:	GPL v2
Group:		Applications/WWW
Source0:	http://forums.cacti.net/download/file.php?id=4091#/postfix_mailserver.tar.gz
# Source0-md5:	3cd539df3669c72b0679f18cbf74f164
URL:		http://forums.cacti.net/about6657.html
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.554
Requires:	cacti
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		cactidir		/usr/share/cacti
%define		resourcedir		%{cactidir}/resource
%define		scriptsdir		%{cactidir}/scripts
%define		snmpdconfdir	/etc/snmp
%define		_libdir			%{_prefix}/lib
# This is officially registered: http://www.oid-info.com/get/1.3.6.1.4.1.16606
%define		snmpoid			.1.3.6.1.4.1.16606.2

%description
Postifix monitoring with Cacti.

%package -n net-snmp-agent-cacti_postfix
Summary:	SNMPd agent to provide Postfix stats
Group:		Networking/Daemons
Requires:	net-snmp

%description -n net-snmp-agent-cacti_postfix
SNMPd agent to provide Postfix stats for cacti.

%prep
%setup -qc

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{resourcedir},%{scriptsdir},%{snmpdconfdir},%{_libdir}}
cp -a *.xml $RPM_BUILD_ROOT%{resourcedir}
install -p fetch_mail_statistics.pl $RPM_BUILD_ROOT%{_libdir}/snmpd-agent-cacti_postfix

%clean
rm -rf $RPM_BUILD_ROOT

%post
%cacti_import_template %{resourcedir}/cacti_host_template_postfix_mailserver.xml

%post -n net-snmp-agent-cacti_postfix
if ! grep -qF %{snmpoid} %{snmpdconfdir}/snmpd.local.conf; then
	echo "extend %{snmpoid} cacti_postfix %{_libdir}/snmpd-agent-cacti_postfix /var/log/maillog /var/log/mailstats.db %{snmpoid}" >> %{snmpdconfdir}/snmpd.local.conf
	%service -q snmpd reload
fi

%preun -n net-snmp-agent-cacti_postfix
if [ "$1" = 0 ]; then
	if [ -f %{snmpdconfdir}/snmpd.local.conf ]; then
		%{__sed} -i -e "/extend %(echo %{snmpoid} | sed -e 's,\.,\\.,g')/d" %{snmpdconfdir}/snmpd.local.conf
		%service -q snmpd reload
	fi
fi

%files
%defattr(644,root,root,755)
%{resourcedir}/*.xml

%files -n net-snmp-agent-cacti_postfix
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/snmpd-agent-cacti_postfix
