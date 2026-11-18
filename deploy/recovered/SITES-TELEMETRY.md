# Public telemetry for the restored Sites mirror

Timestamp: 2026-11-16 | Version: 2.4.1
Author & Credits: https://www.alawise.es/1-s

The recovered browser interfaces read the original public JSON feeds on
https://www.kamala.pro. The new Site has a different origin. Excalibur must
allow that origin before browsers can read those feeds across domains.

In the existing Nginx locations for these public JSON files, include the two
response-header directives from sites-telemetry-cors.conf:

- /telemetry-pendulum/state.json
- /telemetry-crystallization/state.json

Keep the current location's root/alias/proxy and access policy. Do not replace
the location with this fragment. Validate with nginx -t before reloading.
These headers authorize browser reads; they do not start a camera or collector.
The original workspace links remain available from the restored feature pages.
No synthetic measurements are used when a feed is unavailable or stale.
