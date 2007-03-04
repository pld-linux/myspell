%define		_major	3
Summary:	myspell
Name:		myspell
Version:	3.0
Release:	0.3
License:	?
Group:		Libraries
Source0:	ftp://ftp.debian.org/debian/pool/main/m/myspell/%{name}_%{version}+pre3.1.orig.tar.gz
# Source0-md5:	b487ec9287d5d006dadc73f2c0bb68e9
Source1:	%{name}-debian.tar.bz2
URL:		http://lingucomponent.openoffice.org/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MySpell is a Spellchecker as (and derived from) ispell.

%package -n myspell-en_US
Summary:	MySpell spelling dictionaries for English (US)
License:	BSD
Group:		Applications/Text
#Requires:	locales-en
Provides:	myspell-dictionary = %{version}
Provides:	myspell-en = %{version}
Obsoletes:	myspell-en

%description -n myspell-en_US
myspell-en_US contains spell checking data in English (US) to be used
by OpenOffice.org or MySpell-capable applications like Mozilla. With
this extension, you can compose a document in English and check for
the typos easily.

# NOTE: munch,unmunch collide with hunspell-devel
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
%setup -q -n %{name}-%{version}+pre3.1 -a1
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
install -d $RPM_BUILD_ROOT{%{_prefix},%{_pkgconfigdir},%{_mandir}/man1}
%{__make} install STATICLIB=libmyspell-%{version}.a PREFIX=$RPM_BUILD_ROOT%{_prefix}
%{__make} install PREFIX=$RPM_BUILD_ROOT%{_prefix}

# create the links since the Makefile does create them in the dir
# but does not install them
cd $RPM_BUILD_ROOT%{_libdir} && \
	ln -s libmyspell.so.%{version} libmyspell.so.%{_major} && \
	ln -s libmyspell.so.%{version} libmyspell.so
cd -

install utils/ispellaff2myspell $RPM_BUILD_ROOT%{_bindir}
pod2man utils/ispellaff2myspell \
> $RPM_BUILD_ROOT%{_mandir}/man1/ispellaff2myspell.1

cat myspell.pc.in \
| sed -e s,@prefix@,%{_prefix}, | sed -e s,@version@,%{version}, \
	> $RPM_BUILD_ROOT%{_pkgconfigdir}/myspell.pc

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.* CONTRIBUTORS
%attr(755,root,root) %{_libdir}/libmyspell.so.*.*

%files -n myspell-en_US
%defattr(644,root,root,755)
%dir %{_datadir}/myspell
%{_datadir}/myspell/en_US.aff
%{_datadir}/myspell/en_US.dic

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
%{_libdir}/libmyspell-3.0.a
%{_libdir}/libmyspell-3.1_pic.a
