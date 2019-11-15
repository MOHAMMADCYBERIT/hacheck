
all: itest_trusty

DATE := $(shell date +'%Y-%m-%d')
HACHECKVERSION := $(shell sed 's/.*(\(.*\)).*/\1/;q' debian/changelog)
bintray.json: bintray.json.in
	sed -e 's/@DATE@/$(DATE)/g' -e 's/@HACHECKVERSION@/$(HACHECKVERSION)/g' -e 's/@CODENAME@/$(CODENAME)/g' $< > $@

setup:
	echo "Go"
	# mkdir src && cp -R hacheck src && cp -R debian src

package_trusty: setup
	[ -d dist ] || mkdir dist
	tox -e package_trusty

itest_trusty: CODENAME=trusty
itest_trusty: package_trusty bintray.json
	tox -e itest_trusty

package_xenial: setup
	[ -d dist ] || mkdir dist
	tox -e package_xenial

itest_xenial: CODENAME=xenial
itest_xenial: package_xenial bintray.json
	tox -e itest_xenial

clean:
	git clean -Xfd
