%define	major 0
%define libname %mklibname atalk %{major}
%define develname %mklibname atalk -d

Summary:	Appletalk and Appleshare/IP services for Linux
Name:		netatalk
Version:	2.2.2
Release:	1
License:	BSD
Group:		System/Servers
URL:		http://netatalk.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2
Patch0:		netatalk-mdk-etc2ps.patch
Patch1:		netatalk-shared.diff
Patch2:		netatalk-2.2.1-linkage_fix.diff
Patch3:		netatalk-2.2.1-no_libdir.diff
Requires(pre):	rpm-helper
Requires:	groff-perl
Requires:	openssl
Requires:	tetex-dvips
BuildRequires:	acl-devel
BuildRequires:	attr-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	avahi-client-devel
BuildRequires:	avahi-common-devel
BuildRequires:	cracklib-devel
BuildRequires:	cups-devel
BuildRequires:	db-devel
BuildRequires:	dbus-devel
BuildRequires:	gnutls-devel
BuildRequires:	libtool-devel
BuildRequires:	libtool
BuildRequires:	openldap-devel
BuildRequires:	openslp-devel
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	quota
BuildRequires:	tcp_wrappers-devel
Conflicts:	podracer
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1 -b .mdk
%patch1 -p0 -b .shared
%patch2 -p0 -b .linkage_fix
%patch3 -p0 -b .no_libdir

#(sb) breaks autoconf
rm -fr autom4te.cache

%build
%serverbuild

libtoolize --copy --force; aclocal -I macros; autoconf; automake -a -c --foreign

export PKGLIBDIR=%{_libdir}/netatalk
export LD_PRELOAD=
export CFLAGS="$CFLAGS -fomit-frame-pointer -fsigned-char"

%configure2_5x \
    --libexecdir=%{_libdir} \
    --localstatedir=%{_var} \
    --enable-shared \
    --disable-static \
    --with-uams-path=%{_libdir}/netatalk/uams \
    --with-ssl-dir=%{_prefix} \
    --enable-redhat-systemd \
    --with-cracklib \
    --with-pam \
    --with-shadow \
    --enable-pgp-uam \
    --enable-dropkludge=no \
    --disable-shell-check \
    --enable-srvloc \
    --with-ldap \
    --with-acls \
#   --enable-timelord

%make all

%install
rm -rf %{buildroot}

### INSTALL (USING "make install") ###
install -d %{buildroot}{%{_prefix},%{_sysconfdir}/netatalk/}
install -d %{buildroot}%{_libdir}/netatalk
install -d %{buildroot}%{_libdir}/netatalk/msg
install -d %{buildroot}/var/spool/netatalk

%makeinstall_std

# (sb) change to disallow cleartext passwords, example config for guest accounts
cat >> %{buildroot}%{_sysconfdir}/%{name}/afpd.conf << EOF
# config to allow guest logins, cleartext passwords:
# - -transall -uamlist uams_guest.so,uams_clrtxt.so,uams_dhx.so -nosavepassword
# default config with no guest logins, no cleartext passwords
# Service Location Protocol is disabled also, to enable remove -noslp and 
# install openslp and run the slpd service
- -transall -uamlist uams_dhx.so -nosavepassword -noslp
EOF

# clean up installed but unpackaged files
rm -f %{buildroot}%{_includedir}/netatalk/*.c
rm -f %{buildroot}%{_libdir}/netatalk/uams/*.*a
rm -f %{buildroot}%{_datadir}/netatalk/pagecount.ps
rm -f %{buildroot}%{_libdir}/*.*a

# (sb) we don't ship the rc shell, and cleanappledouble.pl seems to do the same thing
rm -f %{buildroot}%{_bindir}/acleandir.rc
rm -f %{buildroot}%{_mandir}/man1/acleandir.1*

# (sb) name clash with yudit package
mv %{buildroot}%{_bindir}/uniconv %{buildroot}%{_bindir}/uniconvn
mv %{buildroot}%{_mandir}/man1/uniconv.1 %{buildroot}%{_mandir}/man1/uniconvn.1

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

%preun
if [ "$1" = "0" ] ; then
	/bin/systemctl disable netatalk.service > /dev/null 2>&1 || :
	/bin/systemctl stop netatalk.service > /dev/null 2>&1 || :
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

%triggerun --  netatalk < 2.2.1
/sbin/chkconfig --del netatalk >/dev/null 2>&1 || :

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTORS NEWS doc/README*
%dir %{_sysconfdir}/%{name}
%dir %{_var}/spool/%{name}
%dir %{_libdir}/netatalk
%dir %{_libdir}/netatalk/msg
%config(noreplace) %{_sysconfdir}/%{name}/Apple*
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/pam.d/netatalk
%dir %{_libdir}/%{name}/uams
%attr(0755,root,root) %{_libdir}/%{name}/uams/*.so
/lib/systemd/system/netatalk.service
%{_libdir}/netatalk/netatalk.sh
%{_bindir}/ad
%{_bindir}/adv1tov2
%{_bindir}/afpldaptest
%{_bindir}/afppasswd
%{_bindir}/apple_dump
%{_bindir}/asip-status.pl
%{_bindir}/binheader
%{_bindir}/cnid2_create
%{_bindir}/dbd
%{_bindir}/hqx2bin
%{_bindir}/lp2pap.sh
%{_bindir}/macbinary
%{_bindir}/macusers
%{_bindir}/megatron
%{_bindir}/nadheader
%{_bindir}/single2bin
%{_bindir}/unbin
%{_bindir}/unhex
%{_bindir}/uniconvn
%{_bindir}/unsingle
%{_sbindir}/afpd
%{_sbindir}/cnid_dbd
%{_sbindir}/cnid_metad
#%{_sbindir}/timelord
%{_mandir}/man[158]/*

%files -n %{libname}
%defattr(-,root,root)
%doc COPYRIGHT COPYING
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%doc doc/DEVELOPER
%{_bindir}/netatalk-config
%{_libdir}/*.so
%dir %{_includedir}/atalk
%{_includedir}/atalk/*.h
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_datadir}/aclocal/%{name}.m4
