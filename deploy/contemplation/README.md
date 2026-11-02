# Excalibur contemplation feed

Timestamp: 2026-11-01  
Version: 2.1.0  
Author & Credits: https://www.alawise.es/1-s

The candle and crystal-ball pages read /telemetry/contemplation.json from
the same website. This optional host collector supplies the real enp6s0
traffic and aggregate kernel firewall notices. A browser cannot inspect
Excalibur's network device or journal directly.

## Install on Fedora 44

Run these commands on Excalibur from the extracted contemplation/ package.
Python 3 and systemd are the only runtime dependencies.

    python3 install.py --root /var/www/kamala.pro/html --dry-run
    sudo python3 install.py --root /var/www/kamala.pro/html --install
    sudo systemctl enable --now kamala-contemplation.service

The installer creates the non-login kamala-flow account, installs the collector
and service, and gives that service access to systemd-journal through its
unit. The collector does not run as root. Its only writable public directory
is html/telemetry/, owned by the service account with mode 0755; its JSON
file has mode 0644. This directory is dedicated to this feed. Existing
application files, AstroApp credentials, mail settings and biorhythm apps
are untouched. Existing collector environment settings are preserved;
replaced collector and unit files are backed up under
/var/backups/kamala-contemplation/.

The install command reloads systemd units but does not start a service,
change firewall logging/rules, or edit nginx. The final command starts it
explicitly. The service can also be stopped with:

    sudo systemctl disable --now kamala-contemplation.service

The existing JSON then becomes stale. It is never substituted with invented
traffic. The application can offer a separately labeled demonstration.
After replacing a previously installed collector, also run
sudo systemctl restart kamala-contemplation.service; enable --now does not
restart a service that is already running.

## Read the result

    systemctl status kamala-contemplation.service
    curl -fsS https://www.kamala.pro/telemetry/contemplation.json
    sudo journalctl -u kamala-contemplation.service -n 30 --no-pager

The first sample establishes a baseline and has zero rates. Later samples
contain real counter differences divided by elapsed monotonic time.
The default write interval is one second; the pages poll about every
two seconds. Sampling and HTTP requests themselves contribute a small
amount of normal server traffic.

The rx_bps and tx_bps fields mean **bytes per second**, despite their compact
names. Multiply by eight when displaying bits per second. Packet rates
are counts per second. These are Linux interface statistics, not an
application-level throughput meter or a count of successful user requests.

An optional exact nginx location is included as nginx-contemplation.conf.
It belongs inside the existing www.kamala.pro server block. The normal
site root serves the file without a new endpoint or proxy. The snippet
adds Cache-Control: no-store and nosniff. Review it, run sudo nginx -t
and reload nginx only after the configuration passes. Frontend requests
also bypass browser caches.

SELinux stays enforcing. The installer restores the normal labels of its
files and the telemetry directory. With the existing /var/www/ layout,
the JSON should receive the site's normal read-only web-content label.
If a custom root has no web-content context rule, add a persistent file
context for that specific root and run restorecon; do not make the whole
web root writable or disable SELinux.

## Firewall activity

The collector follows **new kernel journal records**. It counts a record
only when:

1. The journal transport is kernel.
2. The log includes a recognized verdict/prefix such as DROP, REJECT,
   DENIED, DENY, BLOCK or [PORT-CLOSED-FWD].
3. Its IN= or OUT= field is exactly enp6s0.

Accepted firewall events can produce a brief amber disturbance in the candle
and a concentric light ripple in the crystal. Incoming and outgoing traffic
can control the continuous height, drift or luminosity. These are artistic
mappings of measured activity; they are not severity scores or evidence of
an attack. A single packet can cause more than one logged record, while
rate limiting or disabled logging can cause packets to leave no record.

Only totals, interval counts and a timestamp leave the collector. Public
JSON contains **no IP addresses, MAC addresses, ports, rule text, journal
cursors, host IDs, packet contents or log lines**. The private cursor is
used only in memory to resume the journal follower after interruption.
Starting a new collector session begins at the current journal tail and
does not replay historical notices.
If rotation invalidates an in-memory cursor, following resumes at the current
tail. Records lost during that gap are not reconstructed or invented.

A true firewall.available means the service can read and follow the kernel
journal. It does **not** confirm that denied-packet logging is enabled.
Zero events may mean no matching records, disabled logging, or rate limiting.
An inaccessible journal is represented by available: false. The counter
remains an aggregate count of notices that were actually read.

Check the current firewalld setting without changing it:

    sudo firewall-cmd --get-log-denied

Firewalld documents off as the default. If a deliberate logging change is
needed, sudo firewall-cmd --set-log-denied=unicast enables unicast denied
logging. This command changes both runtime and permanent configuration and
reloads the firewall. It is an optional administrator action, **not run by
the installer**. sudo firewall-cmd --set-log-denied=off turns that setting
off again. Existing explicit nftables/iptables logging can already supply
the required notices without changing firewalld's global setting.

Remote RouterOS/syslog alerts without local kernel IN=/OUT= interface
fields are excluded. This prevents unrelated devices' notices from being
presented as Excalibur's enp6s0 activity.

## Feed contract

    {
      "schema": 1,
      "session_id": "public-process-session-token",
      "interface": "enp6s0",
      "sampled_at": "2026-11-01T12:00:01.000Z",
      "interval_s": 1.001,
      "rx_bps": 14283.25,
      "tx_bps": 337104.5,
      "rx_pps": 67.2,
      "tx_pps": 293.8,
      "link_up": true,
      "firewall": {
        "available": true,
        "delta": 2,
        "total": 19,
        "last_at": "2026-11-01T12:00:00.733Z"
      },
      "status": "live"
    }

This is an example of the format, not a bundled live data file. The
collector never installs sample JSON in the website.

The session_id is a fresh random process identifier without a host or boot ID.
The total is monotonic within that collector process. The delta covers one
collector interval, so a browser polling every two seconds must use
differences in **total**, not sum arbitrary sampled delta values. Establish
a baseline on the first response and on every changed session ID; suppress
old-event animation then. Missing polls do not lose events from the total.
A counter reset is handled by creating a new baseline, never by generating
a huge negative/wrapped traffic rate.

A status of unavailable means the interface counters cannot be read.
A false link_up with a live status means the interface was observed
down. If no fresh sampled_at arrives, the frontend must show stale/offline
state and stop treating animation as a current measurement. A missing feed
on Sites is expected until this optional collector is installed on
Excalibur; Sites hosting cannot read the external server's sysfs or journal.

## Configuration

/etc/sysconfig/kamala-contemplation contains:

    KAMALA_FLOW_INTERFACE=enp6s0
    KAMALA_FLOW_INTERVAL=1

The collector accepts KAMALA_FLOW_OUTPUT when run directly, but the service
pins --output to its one writable directory. Changing a service output
requires updating both ExecStart and ReadWritePaths, then reloading
systemd. The current pages expect enp6s0; changing the interface also
requires an intentional frontend configuration update.

The unit retains the host network namespace so enp6s0 remains visible in
sysfs. RestrictAddressFamilies=AF_UNIX permits journal access while
preventing IP sockets; the collector needs no Internet connection.

For a single real interface sample without journal access:

    python3 contemplation_feed.py --interface enp6s0 --output /existing/review-directory/contemplation.json --once --no-firewall

The output parent directory must already exist. Symbolic links in the
output path are refused. No private logs are saved.

## Primary references

- Linux kernel: [Interface statistics](https://docs.kernel.org/networking/statistics.html).
- systemd: [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
  and [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html).
- firewalld: [firewall-cmd, Log Denied Options](https://firewalld.org/documentation/man-pages/firewall-cmd).
- Fedora: [nginx and SELinux labels](https://fedoraproject.org/wiki/Nginx)
  and [managing file contexts](https://fedoraproject.org/wiki/SELinux/ManagingFileContext).
