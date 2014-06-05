%define _dqsegdb_prefix /usr
%define _sysconfdir %{_dqsegdb_prefix}/etc
%define _docdir %{_datadir}/doc
%{!?dqsegdb_python_sitearch: %define dqsegdb_python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1,prefix='%{_dqsegdb_prefix}')")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}



Name: 		dqsegdb
Summary:	The DQSEGDB Client Package
Version:	1.0
Release:	1.0
License:	None
Group:		Development/Libraries
Source:		%{name}-%{version}.tar.gz
Url:		http://www.lsc-group.phys.uwm.edu/daswg/projects/dqsegdb.html
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
Requires:	python python-cjson glue 
BuildRequires:  python-devel
Prefix:         %{_dqsegdb_prefix}
%description
Python package with executables containing client tools and code for interacting with the DQSEGDB.

%prep
%setup 

%build
CFLAGS="%{optflags}" %{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 \
        --skip-build \
        --root=%{buildroot} \
        --prefix=%{_dqsegdb_prefix}
rm -rf $RPM_BUILD_ROOT/usr/lib64/python2.6/site-packages/dqsegdb--py2.6.egg-info

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{dqsegdb_python_sitearch}/dqsegdb/
%{_dqsegdb_prefix}/bin/
%exclude %{_dqsegdb_prefix}/etc/
%exclude %{_dqsegdb_prefix}/var/
%exclude %{_dqsegdb_prefix}/share/nmi/lalsuite-build*
%exclude %{dqsegdb_python_sitearch}/dqsegdb/__init__.py
%exclude %{dqsegdb_python_sitearch}/dqsegdb/__init__.pyc
%exclude %{dqsegdb_python_sitearch}/dqsegdb/iterutils.py
%exclude %{dqsegdb_python_sitearch}/dqsegdb/git_version.py
%exclude %{dqsegdb_python_sitearch}/dqsegdb/segments.pyc
%exclude %{dqsegdb_python_sitearch}/dqsegdb/iterutils.pyc
%exclude %{dqsegdb_python_sitearch}/dqsegdb/git_version.pyc
%exclude %{dqsegdb_python_sitearch}/dqsegdb/__segments.so
#%exclude %{_dqsegdb_prefix}/src/segments/
#%exclude %{_dqsegdb_prefix}/test/segment_verify.py
#%exclude %{_dqsegdb_prefix}/test/segmentsUtils_verify.py
#%exclude %{_dqsegdb_prefix}/test/verifyutils.py


%changelog
* Wed Jun 4 2014 Ryan Fisher <rpfisher@syr.edu>
- First test version.
