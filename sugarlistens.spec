%define name sugarlistens
%define version 0.0.1
%define unmangled_version 0.0.1
%define release 1

Summary: Speech Recognition Project for the Sugar Learning Platform
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Rodrigo Parra <rodpar07@gmail.com>

%description
Speech recognition for the Sugar Learning Platform.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
mkdir -p $RPM_BUILD_ROOT/etc/dbus-1/system.d/
install -m644 $RPM_BUILD_DIR/%{name}-%{version}/sugarlistens/sugarlistens.conf $RPM_BUILD_ROOT/etc/dbus-1/system.d/
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
/etc/dbus-1/system.d/sugarlistens.conf
%defattr(-,root,root)
