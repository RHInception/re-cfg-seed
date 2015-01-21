%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name recfgseed
%global _src_name recfgseed

Name: re-cfg-seed
Summary: Release Engine etcd configuration seeder
Version: 0.0.3
Release: 1%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-cfg-seed

BuildArch: noarch
BuildRequires: python2-devel, python-setuptools
Requires: python-requests, python-setuptools, python-argparse

%description
A etcd configuration seeding tool. It can ask for config variables
and push in sane defaults if it isn't already created. The seeder
also applies the variables to a local configuration file.


%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-cfg-seed-files.txt

%files -f re-cfg-seed-files.txt
%defattr(-, root, root)
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}


%changelog
* Mon Jan 19 2015 Steve Milner <stevem@gnulinux.net> - 0.0.3-1
- If conf_file can set out_file if conf_file ends with .in

* Mon Jan 19 2015 Steve Milner <stevem@gnulinux.net> - 0.0.2-1
- Basic templates now can be used for non json files.

* Mon Nov 18 2014 Ryan Cook <rcook@redhat.com> - 0.0.1-3
- Requires python argparse.

* Mon Nov 17 2014 Steve Milner <stevem@gnulinux.net> - 0.0.1-2
- Requires setuptools and removed exclude.

* Thu Nov 13 2014 Steve Milner <stevem@gnulinux.net> - 0.0.1-1
- Initial spec
