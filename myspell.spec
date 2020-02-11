%define		major	3
%define		rel		8
Summary:	myspell - spellchecker derived from ispell
Summary(pl.UTF-8):	myspell - narzędzie do sprawdzania pisowni wywodzące się z myspella
Name:		myspell
Version:	3.1
Release:	0.pre.%{rel}
License:	BSD
Group:		Libraries
Source0:	http://ftp.debian.org/debian/pool/main/m/myspell/%{name}_3.0+pre%{version}.orig.tar.gz
# Source0-md5:	b487ec9287d5d006dadc73f2c0bb68e9
Source1:	%{name}-debian.tar.bz2
# Source1-md5:	585eda508195d44ba2886aa6d2f972fc
Source2:	http://ftp.debian.org/debian/pool/main/m/myspell/%{name}_3.0+pre%{version}-23.diff.gz
# Source2-md5:	765baa0ae6bd3cab449ec4f7889e8d49
URL:		http://lingucomponent.openoffice.org/
BuildRequires:	libstdc++-devel
BuildRequires:	perl-tools-pod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MySpell is a Spellchecker as (and derived from) ispell.

%description -l pl.UTF-8
MySpell to narzędzie do sprawdzania pisowni podobne do ispella (i z
niego się wywodzące).

# NOTE: munch,unmunch collide with hunspell-tools
%package tools
Summary:	MySpell tools
Summary(pl.UTF-8):	Narzędzia MySpella
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description tools
This package contains scripts which may be helpful for converting
ispell dictionaries to myspell ones.

%description tools -l pl.UTF-8
Ten pakiet zawiera skrypty przydatne do konwersji słowników ispella do
słowników myspella.

%package devel
Summary:	MySpell spellchecking library development files
Summary(pl.UTF-8):	Pliki programistyczne biblioteki MySpella
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
This package contains the headers to use for programs wanting to use
myspell.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe dla programów używających
myspella.

%package static
Summary:	Static myspell library
Summary(pl.UTF-8):	Statyczna biblioteka myspella
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
This package contains the static library to use for programs wanting
to use myspell.

%description static -l pl.UTF-8
Ten pakiet zawiera bibliotekę statyczną dla programów używających
myspella.

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
	ln -s $(echo libmyspell.so.*.*) libmyspell.so.%{major} && \
	ln -s $(echo libmyspell.so.*.*) libmyspell.so
cd -

install -p utils/ispellaff2myspell $RPM_BUILD_ROOT%{_bindir}
pod2man utils/ispellaff2myspell \
> $RPM_BUILD_ROOT%{_mandir}/man1/ispellaff2myspell.1

cat myspell.pc.in \
| sed -e s,@prefix@,%{_prefix}, | sed -e s,@version@,%{version}, \
	> $RPM_BUILD_ROOT%{_pkgconfigdir}/myspell.pc

# packaged by myspell-dictionaries
%{__rm} $RPM_BUILD_ROOT%{_datadir}/myspell/en_US.{aff,dic}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.* CONTRIBUTORS
%attr(755,root,root) %{_libdir}/libmyspell.so.*.*
%ghost %{_libdir}/libmyspell.so.3

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/ispellaff2myspell
%attr(755,root,root) %{_bindir}/munch
%attr(755,root,root) %{_bindir}/unmunch
%{_mandir}/man1/ispellaff2myspell.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmyspell.so
%{_includedir}/myspell
%{_pkgconfigdir}/myspell.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libmyspell.a
%{_libdir}/libmyspell_pic.a
