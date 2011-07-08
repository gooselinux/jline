# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _without_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define _without_maven 1

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define cvs_version     0.9.94
%define repo_dir    .m2/repository

Name:           jline
Version:        0.9.94
Release:        0.8%{?dist}
Epoch:          0
Summary:        Java library for reading and editing user input in console applications
License:        BSD
URL:            http://jline.sf.net/
Group:          Development/Libraries
Source0:        http://download.sourceforge.net/sourceforge/jline/jline-%{cvs_version}.zip
Source1:        CatalogManager.properties
Source2:        jline-build.xml
Requires:       bash
# for /bin/stty
Requires:       coreutils
BuildRequires:  jpackage-utils >= 0:1.7
%if %{with_maven}
BuildRequires:  xml-commons-resolver
BuildRequires:  maven2
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-surefire
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-assembly
BuildRequires:  maven2-plugin-site
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  ant-apache-resolver
%else
BuildRequires:  ant
BuildRequires:  junit
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description
JLine is a java library for reading and editing user input in console
applications. It features tab-completion, command history, password
masking, customizable keybindings, and pass-through handlers to use to
chain to other console applications.

%package        demo
Summary:        Demos for %{name}
Group:          Development/Documentation

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description    demo
Demonstrations and samples for %{name}.

# FIXME: the maven ant:ant generated build.xml file does not contain 
#        a javadoc task
%if %{with_maven}
%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description    javadoc
Javadoc for %{name}.
%endif

%prep
# BEWARE: The jar file META-INF is not under the subdir
%setup -q -c -n %{name}-%{cvs_version}
cp -pr %{name}-%{cvs_version}/* .
rm -fr %{name}-%{cvs_version}

# Use locally installed DTDs
mkdir %{_builddir}/%{name}-%{cvs_version}/build
cp -p %SOURCE1 %{_builddir}/%{name}-%{cvs_version}/build/

cp -p %{SOURCE2} src/build.xml

%build
mkdir -p native
# Now done by Patch0 for documentation purposes
#perl -p -i -e 's|^.*<attribute name="Class-Path".*||' build.xml

# Use locally installed DTDs
export CLASSPATH=%{_builddir}/%{name}-%{cvs_version}/build

cd src/

%if %{with_maven}
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
        -e \
                -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
                -Dmaven.test.failure.ignore=true \
        install javadoc:javadoc
%else
mkdir -p $(pwd)/.m2/repository
build-jar-repository $(pwd)/.m2/repository junit
export CLASSPATH=target/classes
ant -Dmaven.mode.offline -Duser.home=$(pwd) 
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
for jar in $(find -type f -name "*.jar" | grep -E target/.*.jar); do
        install -m 644 $jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
done
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do \
ln -sf ${jar} ${jar/-%{version}/}; done)

# the maven ant:ant task did not generate a build.xml file with a javadoc task
%if %{with_maven}
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
for target in $(find -type d -name target); do
        install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
        cp -pr $target/site/apidocs/* $jar $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/`basename \`dirname $target\` | sed -e s:jline-::g`
done
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/META-INF

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%doc LICENSE.txt

%if %{with_maven}
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-0.9.9.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/*
%endif

#FIXME: add javadoc support to generated build.xml

%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/jline-0.9.9.jar.*
%endif

%changelog
* Tue Jan 26 2010 Deepak Bhole <dbhole@redhat.com> 0.9.94-0.7
- Fix switch that was causing test failure

* Tue Jan 05 2010 Andrew Overholt <overholt@redhat.com> 0.9.94-0.7
- Really build with ant.

* Mon Dec 14 2009 Andrew Overholt <overholt@redhat.com> 0.9.94-0.6
- Build with ant.

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:0.9.94-0.5
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:0.9.94-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:0.9.94-0.3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:9.94-0.2
- drop repotag

* Mon Mar 24 2008 Matt Wringe <mwringe@redhat.com> - 0:9.94-0jpp.1
- Update to 0.9.94 (BZ #436204)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:0.9.9-2jpp.1
- Autorebuild for GCC 4.3

* Tue Mar 06 2007 Matt Wringe <mwringe@redhat.com> - 0:0.9.9-1jpp.1
- Add option to build with ant.
- Fix various rpmlint issues
- Specify proper license

* Thu May 04 2006 Alexander Kurtakov <akurtkov at gmail.com> - 0:0.9.9-1jpp
- Upgrade to 0.9.9

* Thu May 04 2006 Ralph Apel <r.apel at r-apel.de> - 0:0.9.5-1jpp
- Upgrade to 0.9.5
- First JPP-1.7 release

* Mon Apr 25 2005 Fernando Nasser <fnasser@redhat.com> - 0:0.9.1-1jpp
- Upgrade to 0.9.1
- Disable attempt to include external jars

* Mon Apr 25 2005 Fernando Nasser <fnasser@redhat.com> - 0:0.8.1-3jpp
- Changes to use locally installed DTDs
- Do not try and access sun site for linking javadoc

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:0.8.1-2jpp
- Rebuild with ant-1.6.2

* Mon Jan 26 2004 David Walluck <david@anti-microsoft.org> 0:0.8.1-1jpp
- release
