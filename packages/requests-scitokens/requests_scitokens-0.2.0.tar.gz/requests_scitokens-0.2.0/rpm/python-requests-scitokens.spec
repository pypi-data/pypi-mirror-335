%define srcname requests-scitokens
%global distname %{lua:name = string.gsub(rpm.expand("%{srcname}"), "[.-]", "_"); print(name)}
%define version 0.1.0
%define release 1

# -- metadata ---------------

BuildArch: noarch
License:   ASL 2.0
Name:      python-%{srcname}
Packager:  Duncan Macleod <macleoddm@cardiff.ac.uk>
Prefix:    %{_prefix}
Release:   %{release}%{?dist}
Source0:   %pypi_source %distname
Summary:   SciTokens auth plugin for python3-requests
Url:       https://git.ligo.org/computing/software/requests-scitokens
Vendor:    Duncan Macleod <macleoddm@cardiff.ac.uk>
Version:   %{version}

# -- build requirements -----

# static build requirements
BuildRequires: python3-devel
BuildRequires: python3dist(pip)
BuildRequires: python3dist(setuptools)
BuildRequires: python3dist(setuptools-scm)
BuildRequires: python3dist(wheel)

# test requirements
BuildRequires: python3dist(pytest)
BuildRequires: python3dist(requests) >= 2.20.0
BuildRequires: python3dist(requests-mock)
BuildRequires: python3dist(scitokens) >= 1.7.4

# -- packages ---------------

# src.rpm
%description
requests-scitokens adds optional SciTokens authorisation support
for the python3-requests HTTP library.

%package -n python3-%{srcname}
Summary: %{summary}
%description -n python3-%{srcname}
requests-scitokens adds optional SciTokens authorisation support
for the python3-requests HTTP library.
This package provides the Python %{python3_version} library.
%files -n python3-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- build ------------------

%prep
%autosetup -n %{distname}-%{version}
# for RHEL <= 9 hack together setup.{cfg,py} for old setuptools
%if 0%{?rhel} > 0 && 0%{?rhel} <= 9
cat > setup.cfg <<EOF
[metadata]
name = %{srcname}
author-email = %{packager}
description = %{summary}
license = %{license}
license_files = LICENSE
url = %{url}
[options]
packages = find:
python_requires = >=3.6
install_requires =
	requests >= 2.20.0
	scitokens >= 1.7.4
EOF
%endif
%if %{undefined pyproject_wheel}
cat > setup.py <<EOF
from setuptools import setup
setup(use_scm_version=True)
EOF
%endif

%build
%if %{defined pyproject_wheel}
%pyproject_wheel
%else
%py3_build_wheel
%endif

%install
%if %{defined pyproject_install}
%pyproject_install
%else
%py3_install_wheel %{distname}-%{version}*.whl
%endif

%check
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
%python3 -m pip show requests-scitokens
%pytest --verbose -ra --pyargs requests_scitokens

# -- changelog --------------

%changelog
* Tue Feb 13 2024 Duncan Macleod <macleoddm@cardiff.ac.uk> - 0.1.0-1
- first release
