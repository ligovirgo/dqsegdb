%define srcname dqsegdb
%define version 1.6.1
%define release 2

Name: python-%{srcname}
Version: %{version}
Release: %{release}%{?dist}
Summary: Client library for DQSegDB
Vendor: Robert Bruntz <robert.bruntz@ligo.org>

License: GPLv3
Url:     https://github.com/ligovirgo/dqsegdb
Source0: %pypi_source

BuildArch: noarch
Prefix: %{_prefix}

# rpmbuild dependencies
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros

# build requirements
BuildRequires: python%{python3_pkgversion}
BuildRequires: python%{python3_pkgversion}-setuptools

# test requirements
BuildRequires: python%{python3_pkgversion}-pyOpenSSL >= 0.14
BuildRequires: python%{python3_pkgversion}-pytest

# -- src.rpm

%description
This package provides the client tools to connect to LIGO/VIRGO
DQSEGDB server instances.
Binary RPMs are split into the Python libraries in the
'python*-dqsegdb' package(s) and the command-line tools in the
'dqsegdb' package.

# -- dqsegdb

%package -n %{srcname}
Summary: %{summary}
BuildArch: noarch
Requires: python%{python3_pkgversion}-%{srcname} = %{version}-%{release}
%description -n %{srcname}
This package provides the client tools to connect to LIGO/VIRGO
DQSEGDB server instances.

# -- python3x-dqsegdb

%package -n python%{python3_pkgversion}-%{srcname}
Summary: Python %{python3_version} client library for the DQSEGDB service
Requires: python%{python3_pkgversion}-glue >= 1.55
Requires: python%{python3_pkgversion}-gwdatafind
Requires: python%{python3_pkgversion}-ligo-segments
Requires: python%{python3_pkgversion}-pyOpenSSL >= 0.14
Requires: python%{python3_pkgversion}-pyRXP
%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}
%description -n python%{python3_pkgversion}-%{srcname}
Python %{python3_version} interface libraries for the DQSEGDB client
tools.

# -- build

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build

%install
%py3_install

%check
cd %{_builddir}  # move out of the source tree
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
export PATH="%{buildroot}%{_bindir}:${PATH}"
%{__python3} -m pytest -ra -v --pyargs dqsegdb

%clean
rm -rf $RPM_BUILD_ROOT

# -- files

%files -n %{srcname}
%defattr(-,root,root)
%license LICENSE
%doc README.md
%{_bindir}/*dqsegdb

%files -n python%{python3_pkgversion}-dqsegdb
%defattr(-,root,root)
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- changelog

%changelog
* Tue Dec 7 2021 Duncan Macleod <duncan.macleod@ligo.org> 1.6.1-2
- build python3 packages
- bundle command-line tools separately
