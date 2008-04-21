%define	major 0
%define libname %mklibname atalk %{major}
%define develname %mklibname atalk -d

Summary:	Appletalk and Appleshare/IP services for Linux
Name:		netatalk
Version:	2.0.3
Release:	%mkrel 11
License:	BSD
Group:		System/Servers
URL:		http://%{name}.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2
Patch0:		netatalk-mdk-etc2ps.patch
Patch1:		netatalk-2.0.3-pinit.patch
Patch2:		netatalk-shared.diff
Patch3:		netatalk-2008.diff
Patch4:		netatalk-bug25158.diff
Requires(pre):	rpm-helper
Requires:	groff-perl
Requires:	openssl
Requires:	tetex-dvips
BuildRequires:	libtool
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	chrpath
BuildRequires:	cracklib-devel
BuildRequires:	cups-devel
BuildRequires:	db4.2-devel 
BuildRequires:	gnutls-devel
BuildRequires:	libltdl-devel
BuildRequires:	openslp-devel
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	quota
BuildRequires:	tcp_wrappers-devel
BuildConflicts: xfs-devel
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
Requires:	%{libname} = %{version}

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
%patch1 -p1 -b .pinit
%patch2 -p0 -b .shared
%patch3 -p0 -b .2008
%patch4 -p0 -b .bug25158

#(sb) breaks autoconf
rm -fr autom4te.cache

# (sb) name clash with yudit
sed -i 's|uniconv|uniconvn|g' man/man1/uniconv.1.tmpl
mv doc/htmldocs/uniconv.1.html doc/htmldocs/uniconvn.1.html
sed -i 's|uniconv|uniconvn|g' doc/htmldocs/uniconvn.1.html

%build
libtoolize --copy --force; aclocal -I macros; autoconf; automake -a -c --foreign

export PKGLIBDIR=%{_libdir}/netatalk
export LD_PRELOAD=

CFLAGS="$RPM_OPT_FLAGS -fomit-frame-pointer -fsigned-char"
%configure2_5x \
    --libexec=%{_bindir} \
    --localstatedir=%{_var} \
    --enable-shared \
    --enable-static \
    --with-uams-path=%{_libdir}/netatalk/uams \
    --with-msg-dir=%{_libdir}/netatalk/msg \
    --with-ssl-dir=%{_prefix} \
    --enable-redhat \
    --with-cracklib \
    --with-pam \
    --with-shadow \
    --with-tcp-wrappers \
    --enable-pgp-uam \
    --enable-timelord \
    --enable-dropkludge=no \
    --disable-shell-check \
    --enable-srvloc

%make all

%install
rm -rf %{buildroot}

### INSTALL (USING "make install") ###
install -d %{buildroot}{%{_prefix},%{_sysconfdir}/netatalk/}
install -d %{buildroot}/%{_libdir}/netatalk
install -d %{buildroot}/%{_libdir}/netatalk/msg

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
rm -f %{buildroot}%{_libdir}/netatalk/uams/*.la
rm -f %{buildroot}%{_libdir}/netatalk/uams/*.a
rm -f %{buildroot}%{_datadir}/netatalk/pagecount.ps

# (sb) we don't ship the rc shell, and cleanappledouble.pl seems to do the same thing
rm -f %{buildroot}%{_bindir}/acleandir.rc
rm -f %{buildroot}%{_mandir}/man1/acleandir.1*

# (sb) rpath cleanup
#chrpath -d %{buildroot}%{_sbindir}/papd

# (sb) mutliarch
%multiarch_binaries %{buildroot}%{_bindir}/%{name}-config

# (sb) name clash with yudit package
mv %{buildroot}%{_bindir}/uniconv %{buildroot}%{_bindir}/uniconvn
mv %{buildroot}%{_mandir}/man1/uniconv.1 %{buildroot}%{_mandir}/man1/uniconvn.1

%post
%_post_service atalk
/sbin/ldconfig
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
%_preun_service atalk

%postun
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

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTORS NEWS README TODO doc/README* doc/FAQ doc/Netatalk* doc/htmldocs/*
%attr(0755,root,root) %{_initrddir}/atalk
%dir %{_sysconfdir}/%{name}
%dir %{_var}/spool/%{name}
%dir %{_libdir}/netatalk
%dir %{_libdir}/netatalk/msg
%config(noreplace) %{_sysconfdir}/%{name}/Apple*
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/pam.d/netatalk
%dir %{_libdir}/%{name}/uams
%attr(0755,root,root) %{_libdir}/%{name}/uams/*.so
%{_bindir}/*
%exclude %{_bindir}/%{name}-config
%exclude %{multiarch_bindir}
%{_sbindir}/*
%{_mandir}/man[158]/*

%files -n %{libname}
%defattr(-,root,root)
%doc COPYRIGHT COPYING 
%{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%doc doc/DEVELOPER
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/*.la
%dir %{_includedir}/atalk
%{_includedir}/atalk/*.h
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_datadir}/aclocal/%{name}.m4
%multiarch %{multiarch_bindir}/%{name}-config
%{_mandir}/man[34]/*
