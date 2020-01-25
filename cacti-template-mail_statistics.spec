%define		template	mail_statistics
Summary:	Mail logs Graphing with Cacti
Name:		cacti-template-%{template}
Version:	0.1
Release:	0.6
License:	GPL v2
Group:		Applications/WWW
Source0:	http://forums.cacti.net/download/file.php?id=4091#/postfix_mailserver.tar.gz
# Source0-md5:	3cd539df3669c72b0679f18cbf74f164
URL:		http://forums.cacti.net/about6657.html
Patch0:		cachetime.patch
Patch1:		more-matches.patch
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
%define		dbfile			/var/spool/postfix/mailstats.db
%define		agentscript		%{_libdir}/snmpd-agent-cacti-mail_statistics
# This is officially registered: http://www.oid-info.com/get/1.3.6.1.4.1.16606
%define		snmpoid			.1.3.6.1.4.1.16606.2

%description
Postifix monitoring with Cacti.

%package -n net-snmp-agent-mail_statistics
Summary:	SNMPd agent to provide mail stats
Group:		Networking/Daemons
Requires:	net-snmp

%description -n net-snmp-agent-mail_statistics
SNMPd agent to provide mail stats for Cacti.

%prep
%setup -qc
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{resourcedir},%{scriptsdir},%{snmpdconfdir},%{_libdir}}
cp -a *.xml $RPM_BUILD_ROOT%{resourcedir}
install -p fetch_mail_statistics.pl $RPM_BUILD_ROOT%{agentscript}
# ghost the dbfile
install -d $RPM_BUILD_ROOT$(dirname %{dbfile})
touch $RPM_BUILD_ROOT%{dbfile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%cacti_import_template %{resourcedir}/cacti_host_template_postfix_mailserver.xml

%post -n net-snmp-agent-mail_statistics
if ! grep -qF %{snmpoid} %{snmpdconfdir}/snmpd.local.conf; then
	echo "pass %{snmpoid} cacti_postfix %{agentscript} /var/log/maillog %{dbfile} %{snmpoid}" >> %{snmpdconfdir}/snmpd.local.conf
	%service -q snmpd reload
fi

%preun -n net-snmp-agent-mail_statistics
if [ "$1" = 0 ]; then
	if [ -f %{snmpdconfdir}/snmpd.local.conf ]; then
		%{__sed} -i -e "/pass %(echo %{snmpoid} | sed -e 's,\.,\\.,g')/d" %{snmpdconfdir}/snmpd.local.conf
		%service -q snmpd reload
	fi
fi

%files
%defattr(644,root,root,755)
%{resourcedir}/*.xml

%files -n net-snmp-agent-mail_statistics
%defattr(644,root,root,755)
%attr(755,root,root) %{agentscript}
%ghost %attr(700,root,root) %{dbfile}
