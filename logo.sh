sudo tee /var/www/time.1-s.es/html/favicon.svg > /dev/null << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <!--
    Timestamp: 2026-11-04
    Version: 1.0.0
    PanIpSys 16-section (4 equal quarters) radial clock emblem
    Author and Credits: https://www.alawise.es/1-s
  -->
  <g stroke-width="2.6" stroke-linecap="round" fill="none">
    <!-- Quarter 1 (0 to 90 deg) -->
    <line x1="32" y1="24" x2="32" y2="5" stroke="#5b57e6" transform="rotate(0 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#3dbb78" transform="rotate(22.5 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#eac445" transform="rotate(45 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#e45c67" transform="rotate(67.5 32 32)"/>
    <!-- Quarter 2 (90 to 180 deg) -->
    <line x1="32" y1="24" x2="32" y2="5" stroke="#5b57e6" transform="rotate(90 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#3dbb78" transform="rotate(112.5 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#eac445" transform="rotate(135 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#e45c67" transform="rotate(157.5 32 32)"/>
    <!-- Quarter 3 (180 to 270 deg) -->
    <line x1="32" y1="24" x2="32" y2="5" stroke="#5b57e6" transform="rotate(180 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#e45c67" transform="rotate(202.5 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#eac445" transform="rotate(225 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#3dbb78" transform="rotate(247.5 32 32)"/>
    <!-- Quarter 4 (270 to 360 deg) -->
    <line x1="32" y1="24" x2="32" y2="5" stroke="#5b57e6" transform="rotate(270 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#e45c67" transform="rotate(292.5 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#eac445" transform="rotate(315 32 32)"/>
    <line x1="32" y1="24" x2="32" y2="5" stroke="#3dbb78" transform="rotate(337.5 32 32)"/>
  </g>
</svg>
EOF

sudo chmod 0644 /var/www/time.1-s.es/html/favicon.svg
sudo restorecon -v /var/www/time.1-s.es/html/favicon.svg
