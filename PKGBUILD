pkgname=python-neetbox
pkgver=0.4.8
pkgrel=1
pkgdesc="Logging/Debugging/Tracing/Managing/Facilitating long running python projects, especially a replacement of tensorboard for deep learning projects"
arch=('any')
url="https://neetbox.550w.host"
license=('MIT')
makedepends=('python-pip')
noextract=()
sha256sums=()

package() {
    python -m pip install --no-deps --ignore-installed --prefix=/usr --root="$pkgdir" neetbox==$pkgver
}
