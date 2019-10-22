%global commit 6enkw
%define major 80
%define libname %mklibname %name %major
%define libnamedev %mklibname %name -d
%define lib_name_orig libcoin
%define _disable_lto %nil

%global __requires_exclude cmake\\(simage|superglu\\)

Name:           coin4
Version:        4.0.0
Release:        1
Summary:        High-level 3D visualization library

License:        BSD and GPLv3+

URL:            https://bitbucket.org/Coin3D/coin/wiki/Home

Source0:        https://bitbucket.org/Coin3D/coin/downloads/coin-%{version}-src.zip

Patch3:         0003-man3.patch
Patch5:         0005-gcc-4.7.patch
Patch6:         0006-inttypes.patch
Patch11:        0011-Fix-SoCamera-manpage.patch

BuildRequires:  cmake
BuildRequires:  doxygen
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(xext)
BuildRequires:	boost-devel
BuildRequires:  zlib-devel
BuildRequires:  bzip2-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel

%description
Coin3D is a high-level, retained-mode toolkit for effective 3D graphics
development. It is API compatible with Open Inventor 2.1.

%package -n %{libname}
Summary:	Main library for Coin
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with Coin.

%package -n %{libnamedev}
Summary:	Headers for developing programs that will use Coin
Group:		Development/C++
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	cmake(coin)
Provides:	cmake(coin4)

%description -n %{libnamedev}
This package contains the headers that programmers will need to develop
applications which will use Coin.


%package doc
Summary:        HTML developer documentation for Coin

%description doc
%{summary}.


%prep
%autosetup -p1 -n coin-%{commit}

# Update doxygen configuration
doxygen -u docs/coin.doxygen.in

#find -name 'Makefile.*' -exec sed -i -e 's,\$(datadir)/Coin,$(datadir)/Coin4,' {} \;

# bogus permissions
find . \( -name '*.h' -o -name '*.cpp' -o -name '*.c' \) -a -executable -exec chmod -x {} \;

# convert sources to utf-8
#for a in $(find . -type f -exec file -i {} \; | grep -i iso | sed -e 's,:.*,,'); do \
#  /usr/bin/iconv -f ISO-8859-1 -t utf-8 $a > $a~; \
#  mv $a~ $a; \
#done

# get rid of bundled boost headers
rm -rf include/boost


%build
mkdir build-%{_arch}
pushd build-%{_arch}
cmake -DCOIN_BUILD_DOCUMENTATION=TRUE \
       -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
       -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
       -DCOIN_THREADSAFE=ON \
       -DCOIN_BUILD_DOCUMENTATION_MAN=TRUE \
       -DCOIN_BUILD_TESTS=FALSE \
       -DHAVE_MULTIPLE_VERSION=TRUE \
       -DUSE_EXTERNAL_EXPAT=TRUE ..

%make_build
popd

%install
%make_install -C build-%{_arch}

cd %{buildroot}%{_mandir}
/usr/bin/rename .3 .3coin4 man3/*
cd - 

mkdir -p %{buildroot}%{_libdir}/Coin4
mkdir -p %{buildroot}%{_bindir}

cat > %{buildroot}%{_libdir}/Coin4/coin-config << EOF
coin-config for Coin4 is here for alternatives compatibility only with Coin2/3.
Use the CMake import targets instead.
EOF

ln -s %{_libdir}/Coin4/coin-config %{buildroot}%{_bindir}/coin-config
mv %{buildroot}%{_libdir}/pkgconfig/Coin.pc %{buildroot}%{_libdir}/pkgconfig/Coin4.pc
ln -s %{_libdir}/pkgconfig/Coin4.pc %{buildroot}%{_libdir}/pkgconfig/Coin.pc


%post -n %{libnamedev}
link=$(readlink -e "%{_bindir}/coin-config")
if [ "$link" = "%{_bindir}/coin-config" ]; then
  rm -f %{_bindir}/coin-config
fi
if [ "$link" = "%{_libdir}/Coin4/coin-config" ]; then
  rm -f %{_bindir}/coin-config
fi

/usr/sbin/alternatives --install "%{_bindir}/coin-config" coin-config \
  "%{_libdir}/Coin4/coin-config" 80 \
  --slave %{_libdir}/pkgconfig/Coin.pc Coin.pc %{_libdir}/pkgconfig/Coin4.pc \
  --slave %{_libdir}/libCoin.so libCoin.so %{_libdir}/libCoin.so.80

%preun -n %{libnamedev}
if [ $1 = 0 ]; then
  /usr/sbin/alternatives --remove coin-config "%{_libdir}/Coin4/coin-config"
fi


%files
%doc AUTHORS ChangeLog README{,.UNIX} THANKS FAQ*
%license COPYING
%dir %{_datadir}/Coin4
%{_datadir}/Coin4/scxml

%files -n %{libname}
%{_libdir}/libCoin.so.%{major}*
%{_libdir}/libCoin.so.4.*

%files -n %{libnamedev}
%ghost %{_bindir}/coin-config
%ghost %{_libdir}/libCoin.so
%ghost %{_libdir}/pkgconfig/Coin.pc
%{_includedir}/Coin4/
%{_libdir}/cmake/Coin-%{version}/
%{_libdir}/Coin4/coin-config
%{_libdir}/pkgconfig/Coin4.pc
%dir %{_datadir}/Coin4
%{_datadir}/Coin4/draggerDefaults
%{_datadir}/Coin4/shaders
%{_mandir}/man?/*

%files doc
%{_docdir}/Coin4/html/
