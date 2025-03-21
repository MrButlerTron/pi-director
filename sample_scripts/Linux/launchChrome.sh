#!/bin/bash
#test domain for Internet access
test=google.com
#put the domain you are hosting pi-director after the equal sign
URL=

function check-internet () {
	if nc -zw1 $test 443 && echo |openssl s_client -connect $test:443 2>&1 |awk '
	  $1 == "SSL" && $2 == "handshake" { handshake = 1 }
	    handshake && $1 == "Verification:" { ok = $2; exit }
	      END { exit ok != "OK" }'
      then
			return
	else
		return 1
	fi
}

#wait until we have internet
until check-internet; do : ; done

DISPLAY=:0 chromium --start-fullscreen --disable-session-crashed-bubble --noerrordialogs --hide-crash-restore-bubble --noerrors http://$URL?host=$HOSTNAME &
