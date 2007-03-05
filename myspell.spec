%define		_major	3
%define		_rel	1
Summary:	myspell
Name:		myspell
Version:	3.1
Release:	0.pre.%{_rel}
License:	?
Group:		Libraries
Source0:	ftp://ftp.debian.org/debian/pool/main/m/myspell/%{name}_3.0+pre%{version}.orig.tar.gz
# Source0-md5:	b487ec9287d5d006dadc73f2c0bb68e9
Source1:	%{name}-debian.tar.bz2
# Source1-md5:	585eda508195d44ba2886aa6d2f972fc
URL:		http://lingucomponent.openoffice.org/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MySpell is a Spellchecker as (and derived from) ispell.

# NOTE: munch,unmunch collide with hunspell-tools
%package tools
Summary:	MySpell tools
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description tools
This package contains scripts which may be helpful for converting
ispell dictionaries to myspell ones.

%package devel
Summary:	MySpell spellchecking library development files
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
This package contains the headers and the static library to use for
programs wanting to use myspell.

%package static
Summary:	Static myspell library
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
This package contains the static library to use for programs wanting
to use myspell.

%prep
%setup -q -n %{name}-3.0+pre%{version} -a1
for a in $(cat patches/00list); do
	patch -p1 < patches/$a.dpatch;
done

%build
for i in $(grep 'OBJS =' Makefile | cut -d"=" -f2 | sed -e s/\.o/\.cxx/g); do
	%{__cc} %{rpmcflags} -c $i;
done
ar rc $(grep STATICLIB= Makefile | head -n 1 | cut -d"=" -f2 | sed -s s/_pic// | sed -e s/$\(VERSION\)/%{version}/) \
	$(grep OBJS\ = Makefile | cut -d"=" -f2)
rm *.o

%{__make} CXXFLAGS="%{rpmcxxflags}" CFLAGS="%{rpmcflags}" CXX="%{__cxx}" CC="%{__cc}"
%{__make} check

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libdir},%{_pkgconfigdir},%{_mandir}/man1}
%if "lib" != "%{_lib}"
ln -s %{_lib} $RPM_BUILD_ROOT%{_prefix}/lib
%endif
%{__make} install \
	STATICLIB=libmyspell.a \
	PREFIX=$RPM_BUILD_ROOT%{_prefix}
%{__make} install \
	STATICLIB=libmyspell_pic.a \
	PREFIX=$RPM_BUILD_ROOT%{_prefix}

# create the links since the Makefile does create them in the dir
# but does not install them
cd $RPM_BUILD_ROOT%{_libdir} && \
	ln -s $(echo libmyspell.so.*.*) libmyspell.so.%{_major} && \
	ln -s $(echo libmyspell.so.*.*) libmyspell.so
cd -

install utils/ispellaff2myspell $RPM_BUILD_ROOT%{_bindir}
pod2man utils/ispellaff2myspell \
> $RPM_BUILD_ROOT%{_mandir}/man1/ispellaff2myspell.1

cat myspell.pc.in \
| sed -e s,@prefix@,%{_prefix}, | sed -e s,@version@,%{version}, \
	> $RPM_BUILD_ROOT%{_pkgconfigdir}/myspell.pc

# packaged by myspell-dictionaries
rm -f $RPM_BUILD_ROOT%{_datadir}/myspell/en_US.{aff,dic}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.* CONTRIBUTORS
%attr(755,root,root) %{_libdir}/libmyspell.so.*.*

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ispellaff2myspell
%attr(755,root,root) %{_bindir}/munch
%attr(755,root,root) %{_bindir}/unmunch
%{_mandir}/man1/ispellaff2myspell.1*

%files devel
%defattr(644,root,root,755)
%{_libdir}/libmyspell.so
%{_includedir}/myspell
%{_pkgconfigdir}/myspell.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libmyspell.a
%{_libdir}/libmyspell_pic.a
