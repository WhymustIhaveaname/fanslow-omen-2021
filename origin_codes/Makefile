fs = $(DESTDIR)/usr/bin/fanslow
ec = $(DESTDIR)/usr/bin/probook_ec
sc = $(DESTDIR)/usr/lib/systemd/system/fanslow.service

# Without proper packaging the following paths should be used instead! In this
# case you also need to modify the `fanslow` and `fanslow.service` files which
# contain hardcoded file paths.

# fs = $(DESTDIR)/usr/local/bin/fanslow
# ec = $(DESTDIR)/usr/local/bin/probook_ec
# sc = $(DESTDIR)/etc/systemd/system/fanslow.service

install: fanslow probook_ec fanslow.service
	@install -Dm 755 fanslow $(fs)
	@install -Dm 755 probook_ec $(ec)
	@install -Dm 644 fanslow.service $(sc)

uninstall:
	@rm $(fs) $(ec) $(sc)
