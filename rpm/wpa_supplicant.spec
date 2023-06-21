Name:       wpa_supplicant

Summary:    WPA/WPA2/IEEE 802.1X Supplicant
Version:    2.9
Release:    1
License:    GPLv2
URL:        https://github.com/sailfishos/wpa_supplicant
Source0:    %{name}-%{version}.tar.gz
Source1:    build-config
Source2:    %{name}.conf
Source3:    %{name}.service
Source4:    %{name}.sysconfig
Patch0:     0001-Revert-nl80211-Set-NL80211_ATTR_IFACE_SOCKET_OWNER-f.patch
Patch1:     0001-AP-Silently-ignore-management-frame-from-unexpected.patch
Patch2:     0001-P2P-Fix-copying-of-secondary-device-types-for-P2P-gr.patch
Patch3:     0001-P2P-Fix-a-corner-case-in-peer-addition-based-on-PD-R.patch
BuildRequires:  pkgconfig(libnl-3.0)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(systemd)
# Required for systemctl
%{?systemd_requires}
# Required for rm
Requires(post): coreutils

%description
wpa_supplicant is a WPA Supplicant for Linux, BSD and Windows with support
for WPA and WPA2 (IEEE 802.11i / RSN). Supplicant is the IEEE 802.1X/WPA
component that is used in the client stations. It implements key negotiation
with a WPA Authenticator and it controls the roaming and IEEE 802.11
authentication/association of the wlan driver.

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
pushd wpa_supplicant
cp %{SOURCE1} .config
CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;
CXXFLAGS="${CXXFLAGS:-%optflags}" ; export CXXFLAGS ;
# yes, BINDIR=_sbindir
BINDIR="%{_sbindir}" ; export BINDIR ;
LIBDIR="%{_libdir}" ; export LIBDIR ;
%make_build
popd

%install
rm -rf %{buildroot}

# init scripts
install -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

# config
install -D -m 0600 %{SOURCE2} %{buildroot}/%{_sysconfdir}/%{name}/%{name}.conf

# binary
install -d %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_passphrase %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_cli %{buildroot}/%{_sbindir}
install -m 0755 %{name}/wpa_supplicant %{buildroot}/%{_sbindir}
install -D -m 0644 %{name}/dbus/dbus-wpa_supplicant.conf %{buildroot}/%{_sysconfdir}/dbus-1/system.d/wpa_supplicant.conf
install -D -m 0644 %{name}/dbus/fi.w1.wpa_supplicant1.service %{buildroot}/%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service

# some cleanup in docs and examples
rm -f  %{name}/doc/.cvsignore
rm -rf %{name}/doc/docbook
chmod -R 0644 %{name}/examples/*.py

%preun
if [ $1 -eq 0 ] ; then
# Package removal, not upgrade
/bin/systemctl --no-reload disable wpa_supplicant.service > /dev/null 2>&1 || :
/bin/systemctl stop wpa_supplicant.service > /dev/null 2>&1 || :
fi

%post
if [ $1 -eq 1 ] ; then
# Initial installation
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
# Remove old log file that is not used anymore if it happens to exist.
rm -f /var/log/wpa_supplicant.log || :

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
# Lets not restart wpa_supplicant on postun to make sure network connectivity is not
# broken during update process.

%files
%defattr(-,root,root,-)
%license COPYING 
%config %{_sysconfdir}/%{name}/%{name}.conf
%config %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_sysconfdir}/dbus-1/system.d/%{name}.conf
%{_datadir}/dbus-1/system-services/fi.w1.wpa_supplicant1.service
%{_sbindir}/wpa_passphrase
%{_sbindir}/wpa_supplicant
%{_sbindir}/wpa_cli
%dir %{_sysconfdir}/%{name}

