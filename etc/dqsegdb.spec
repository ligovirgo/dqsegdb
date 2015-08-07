%define name dqsegdb
%define version 1.2.1
%define unmangled_version 1.2.1
%define unmangled_version 1.2.1
%define release 1

Summary: Client library for DQSegDB
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
Requires: python, python-pyRXP, glue >= 1.47
BuildRequires: python-setuptools, git
BuildArch: noarch
Vendor: Ryan Fisher <ryan.fisher@ligo.org>

%description
This package provides the client tools to connect to LIGO/VIRGO
DQSEGDB server instances.

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
rm -rf $RPM_BUILD_ROOT/dqsegdb.egg-info
rm -rf $RPM_BUILD_ROOT/etc/dqsegdb-user-env.sh
rm -rf $RPM_BUILD_ROOT/etc/dqsegdb-user-env.csh
rm -rf $RPM_BUILD_ROOT/dqsegdb-1.2.1-py2.6.egg-info

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
#%exclude %{_prefix}/untracked/
#%exclude %{_prefix}/usr/untracked/
