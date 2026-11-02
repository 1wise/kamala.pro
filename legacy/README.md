# Owner-supplied application references

Timestamp: 2026-10-30 | Version: 2.0.1
Author and Credits: https://www.alawise.es/1-s

These files come from the owner's Google Drive folder:
1wise / www.kamala.pro / kamala / bior.
Retrieved on October 30, 2026; the source files were last modified in Drive
on October 15, 2026. They are a reference snapshot, not a pull from Excalibur.

The collection includes the biorhythm generator, image compositor, stylesheet,
entry page, SMS helper, and the three SolarSimulator files. The astronomy
engine retains its original third-party license and attribution header.
Generated consultations, visitor records, logs and the bundled PHPMailer
directory are excluded.

## Configuration changes in this copy

Inline service credentials have been removed from bior.php and compose.php.
Their existing variables now read the following server environment settings:

| Setting | Purpose |
| --- | --- |
| KAMALA_SMS_USER | SMS service account |
| KAMALA_SMS_PASSWORD | SMS service password |
| KAMALA_ASTRONOMY_APP_ID | AstronomyAPI account identifier |
| KAMALA_ASTRONOMY_APP_SECRET | AstronomyAPI account secret |

These are separate from the AstroApp JavaScript access code. No values are
included. The historical SMTP helper, which also contained inline credentials,
is replaced by the maintained adapter from deploy/send/public/bior/sense_mail.php.
It uses the existing private Send installation on Excalibur.

## Deployment boundary

The static build and Excalibur installer do not copy legacy/ into the public
site. They preserve the running bior/ applications. Compare this snapshot with
the current server before migrating any original application source.

Original algorithms, field names, UI copy and clipboard behavior are retained.
PHP syntax and JavaScript syntax have been checked. The original compositor
passes request fields to an ImageMagick shell command without filename
validation; this reference copy is not approved for a fresh public deployment.
Its validation and the remaining legacy application behavior need a separate
migration before replacing the running server files.
