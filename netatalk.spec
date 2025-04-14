%define _disable_ld_no_undefined 1

%define	major 19
%define oldlibname %mklibname atalk 0
%define libname %mklibname atalk
%define develname %mklibname atalk -d

Summary:	Appletalk and Appleshare/IP services for Linux
Name:		netatalk
Version:	4.2.1
Release:	1
License:	BSD
Group:		System/Servers
URL:		https://netatalk.io/
Source0:	https://github.com/Netatalk/netatalk/releases/download/netatalk-%(echo %{version} | sed -e 's,\.,-,g')/netatalk-%{version}.tar.xz
Requires(pre):	rpm-helper
Requires:	groff-perl
Requires:	openssl
Requires:	tetex-dvips
BuildRequires:	acl-devel
BuildRequires:	attr-devel
BuildRequires:	avahi-client-devel
BuildRequires:	avahi-common-devel
BuildRequires:	cracklib-devel
BuildRequires:	cups-devel
BuildRequires:	db-devel
BuildRequires:	dbus-devel
BuildRequires:	gnutls-devel
BuildRequires:	iniparser-devel
BuildRequires:	pkgconfig(ldap)
BuildRequires:	openslp-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pam-devel
BuildRequires:	quota
BuildRequires:	tcp_wrappers-devel
Conflicts:	podracer
BuildSystem:	meson

%description
netatalk is an implementation of the AppleTalk Protocol Suite for Unix/Linux
systems. The current release contains support for Ethertalk Phase I and II,
DDP, RTMP, NBP, ZIP, AEP, ATP, PAP, ASP, and AFP. It provides Appletalk file
printing and routing services on Solaris 2.5, Linux, FreeBSD, SunOS 4.1 and
Ultrix 4. It also supports AFP 2.1 and 2.2 (Appleshare IP).

Note: The default configuration disables both guest accounts and plain-text
      passwords.  To enable these options, review the configuration file
      %{_sysconfdir}/netatalk/afpd.conf. Service Location Protocol is also
      disabled, remove -noslp in afpd.conf and install openslp if you want
      use it.

%package -n	%{libname}
Summary:	Shared library for Appletalk and Appleshare/IP services for Linux
Group:          System/Libraries
Requires:	tcp_wrappers
# Renamed 2025/04/14 before OM 6.0
%rename %{oldlibname}

%description -n	%{libname}
netatalk is an implementation of the AppleTalk Protocol Suite for Unix/Linux
systems. The current release contains support for Ethertalk Phase I and II,
DDP, RTMP, NBP, ZIP, AEP, ATP, PAP, ASP, and AFP. It provides Appletalk file
printing and routing services on Solaris 2.5, Linux, FreeBSD, SunOS 4.1 and
Ultrix 4. It also supports AFP 2.1 and 2.2 (Appleshare IP).

This package provides the shared atalk library.

%package -n	%{develname}
Summary:	Static library and header files for the atalk library
Group:		Development/C
Provides:	%{name}-devel = %{version}
Obsoletes:	%{name}-devel
Requires:	%{libname} >= %{version}

%description -n	%{develname}
netatalk is an implementation of the AppleTalk Protocol Suite for Unix/Linux
systems. The current release contains support for Ethertalk Phase I and II,
DDP, RTMP, NBP, ZIP, AEP, ATP, PAP, ASP, and AFP. It provides Appletalk file
printing and routing services on Solaris 2.5, Linux, FreeBSD, SunOS 4.1 and
Ultrix 4. It also supports AFP 2.1 and 2.2 (Appleshare IP).

This package contains the static atalk library and its header files.

%post
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
# after the first install only
if [ "$1" = 1 ]; then
	# add the ddp lines to /etc/services
	if (grep '[0-9][0-9]*/ddp' /etc/services >/dev/null); then
		cat <<'_EOD1_' >&2
warning: The DDP services appear to be present in /etc/services.
warning: Please check them against services.atalk in the documentation.
_EOD1_
		true
	else
		cat <<'_EOD2_' >>/etc/services
# start of DDP services
#
# Everything between the 'start of DDP services' and 'end of DDP services'
# lines will be automatically deleted when the netatalk package is removed.
#
rtmp		1/ddp		# Routing Table Maintenance Protocol
nbp		2/ddp		# Name Binding Protocol
echo		4/ddp		# AppleTalk Echo Protocol
zip		6/ddp		# Zone Information Protocol

afpovertcp	548/tcp		# AFP over TCP
afpovertcp	548/udp
# end of DDP services
_EOD2_
	fi
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
# do only for the last un-install
if [ "$1" = 0 ]; then
	# remove the ddp lines from /etc/services
	if (grep '^# start of DDP services$' /etc/services >/dev/null && \
	    grep '^# end of DDP services$'   /etc/services >/dev/null ); then
	  sed -e '/^# start of DDP services$/,/^# end of DDP services$/d' \
	    </etc/services >/etc/services.tmp$$
	  cat /etc/services.tmp$$ >/etc/services
	  rm /etc/services.tmp$$
	else
	  cat <<'_EOD3_' >&2
warning: Unable to find the lines `# start of DDP services` and
warning: `# end of DDP services` in the file /etc/services.
warning: You should remove the DDP services from /etc/services manually.
_EOD3_
	fi
fi

%files
%{_sysconfdir}/afp.conf
%{_sysconfdir}/extmap.conf
%{_sysconfdir}/pam.d/netatalk
%{_bindir}/*
%{_libdir}/netatalk
%{_datadir}/dbus-1/system.d/netatalk-dbus.conf
%{_mandir}/man1/*
%{_mandir}/man4/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_localstatedir}/netatalk

%files -n %{libname}
%doc COPYRIGHT COPYING
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%{_libdir}/*.so
%{_includedir}/atalk
%{_mandir}/man3/*
