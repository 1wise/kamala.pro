#!/usr/bin/env python3
# Timestamp: 2026-11-01
# Version: 2.1.0
# Author & Credits: https://www.alawise.es/1-s
"""Check public-feed privacy, real counter deltas and safe atomic publication."""

import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


pth_rad = Path(__file__).resolve().parents[1]
sys_cfg = importlib.util.spec_from_file_location(
    "contemplation_feed", pth_rad / "deploy/contemplation/contemplation_feed.py"
)
dat_mod = importlib.util.module_from_spec(sys_cfg)
sys_cfg.loader.exec_module(dat_mod)


def crt_avs(txt_val, txt_cur="journal-cursor-1"):
    return {
        "_TRANSPORT": "kernel",
        "MESSAGE": txt_val,
        "__CURSOR": txt_cur,
        "_BOOT_ID": "private-boot-id",
        "_MACHINE_ID": "private-machine-id",
    }


def crt_red(cnt_rx, cnt_tx, cnt_rp, cnt_tp, est_up=True):
    return {
        "rx_bytes": cnt_rx, "tx_bytes": cnt_tx,
        "rx_packets": cnt_rp, "tx_packets": cnt_tp, "link_up": est_up,
    }


class PrbFwl(unittest.TestCase):
    def test_accepts_only_verdicts_on_the_selected_kernel_interface(self):
        dat_msg = [
            "filter_IN_public_REJECT: IN=enp6s0 OUT= MAC=aa:bb SRC=192.0.2.1 DPT=22",
            "FINAL_DROP: IN= OUT=enp6s0 SRC=198.51.100.3",
            "[PORT-CLOSED-FWD] IN=enp6s0 OUT=wg1 SRC=192.0.2.7",
            "DENIED IN=enp6s0 OUT= SRC=203.0.113.9",
            "DROP IN=wg1 OUT=enp6s0 DPT=443",
        ]
        for txt_val in dat_msg:
            with self.subTest(txt_val=txt_val):
                self.assertTrue(dat_mod.es_avs(crt_avs(txt_val), "enp6s0"))
        for txt_val in [
            "DROP IN=enp6s00 OUT= SRC=192.0.2.1",
            "REJECT IN=wg1 OUT=eth1",
            "DROP IN= OUT= DESCRIPTION=enp6s0",
            "IN=enp6s0 OUT= accepted",
            "The dropped queue of enp6s0",
        ]:
            self.assertFalse(dat_mod.es_avs(crt_avs(txt_val), "enp6s0"))
        dat_itm = crt_avs("DROP IN=enp6s0 OUT=")
        dat_itm["_TRANSPORT"] = "stdout"
        self.assertFalse(dat_mod.es_avs(dat_itm, "enp6s0"))
        dat_itm["_TRANSPORT"] = "kernel"
        dat_itm["MESSAGE"] = [68, 82, 79, 80]
        self.assertFalse(dat_mod.es_avs(dat_itm, "enp6s0"))

    def test_public_aggregate_does_not_contain_private_journal_data(self):
        dat_fwl = dat_mod.DatFwl("enp6s0")
        dat_fwl.est_dis = True
        dat_itm = crt_avs("DROP IN=enp6s0 OUT= MAC=de:ad:be:ef SRC=192.0.2.55 DPT=22")
        self.assertTrue(dat_fwl.agrega(dat_itm, sys_ts=1700000000))
        self.assertFalse(dat_fwl.agrega(dat_itm, sys_ts=1700000001))
        dat_red = dat_mod.DatRed("enp6s0", "public-process-session")
        dat_tel = dat_red.muestra(
            crt_red(100, 200, 1, 2), dat_fwl.muestra(), 1700000002, 10
        )
        txt_val = json.dumps(dat_tel)
        for txt_prv in (
            "192.0.2.55", "de:ad:be:ef", "DPT", "SRC", "MESSAGE", "__CURSOR",
            "private-boot-id", "private-machine-id", "journal-cursor-1"
        ):
            self.assertNotIn(txt_prv, txt_val)
        self.assertEqual(dat_tel["firewall"]["total"], 1)
        self.assertEqual(dat_tel["firewall"]["delta"], 1)
        self.assertTrue(dat_tel["firewall"]["available"])
        self.assertEqual(dat_fwl.muestra()["delta"], 0)
        self.assertEqual(dat_fwl.muestra()["total"], 1)
        self.assertEqual(dat_tel["session_id"], "public-process-session")

    def test_binary_or_oversized_messages_are_not_interpreted(self):
        dat_itm = crt_avs("DROP IN=enp6s0 OUT= " + "x" * 20000)
        self.assertFalse(dat_mod.es_avs(dat_itm, "enp6s0"))
        dat_lns = dat_mod.SysLns()
        dat_lns.separa(b"x" * 16000)
        dat_lns.separa(b"x" * 16000)
        self.assertLessEqual(len(dat_lns.dat_buf), dat_mod.dat_lim)
        dat_res = dat_lns.separa(b"discarded tail\n{\"safe\":true}\n")
        self.assertEqual(dat_res, [b'{"safe":true}'])


class PrbRed(unittest.TestCase):
    def test_real_elapsed_time_rates_reset_and_missing_sample_recovery(self):
        dat_red = dat_mod.DatRed("enp6s0", "stable-session")
        dat_fwl = dat_mod.DatFwl("enp6s0")
        dat_tel = dat_red.muestra(crt_red(1000, 2000, 10, 20), dat_fwl.muestra(), 1000, 10)
        self.assertEqual(dat_tel["rx_bps"], 0)
        dat_tel = dat_red.muestra(crt_red(5000, 10000, 50, 100), dat_fwl.muestra(), 1002, 12)
        self.assertEqual(dat_tel["interval_s"], 2)
        self.assertEqual(dat_tel["rx_bps"], 2000)
        self.assertEqual(dat_tel["tx_bps"], 4000)
        self.assertEqual(dat_tel["rx_pps"], 20)
        self.assertEqual(dat_tel["tx_pps"], 40)
        dat_tel = dat_red.muestra(crt_red(10, 20, 1, 2), dat_fwl.muestra(), 1003, 13)
        self.assertEqual(dat_tel["rx_bps"], 0)
        self.assertEqual(dat_tel["tx_bps"], 0)
        dat_tel = dat_red.muestra(None, dat_fwl.muestra(), 1004, 14)
        self.assertEqual(dat_tel["status"], "unavailable")
        self.assertFalse(dat_tel["link_up"])
        dat_tel = dat_red.muestra(crt_red(100000, 200000, 1000, 2000), dat_fwl.muestra(), 1014, 24)
        self.assertEqual(dat_tel["status"], "live")
        self.assertEqual(dat_tel["rx_bps"], 0)
        self.assertEqual(dat_tel["interval_s"], 0)

    def test_reads_only_counters_and_preserves_down_state(self):
        with tempfile.TemporaryDirectory() as txt_tmp:
            pth_tmp = Path(txt_tmp)
            pth_sys = pth_tmp / "enp6s0"
            (pth_sys / "statistics").mkdir(parents=True)
            for txt_nom, cnt_val in zip(dat_mod.dat_nom, (100, 200, 3, 4)):
                (pth_sys / "statistics" / txt_nom).write_text(str(cnt_val) + "\n")
            (pth_sys / "operstate").write_text("down\n")
            dat_tel = dat_mod.lee_red("enp6s0", pth_tmp)
            self.assertEqual(dat_tel, crt_red(100, 200, 3, 4, False))
            (pth_sys / "operstate").write_text("up\n")
            self.assertTrue(dat_mod.lee_red("enp6s0", pth_tmp)["link_up"])
            (pth_sys / "statistics/rx_bytes").write_text("-123\n")
            self.assertIsNone(dat_mod.lee_red("enp6s0", pth_tmp))
            self.assertIsNone(dat_mod.lee_red("missing0", pth_tmp))
        for txt_val in ("../enp6s0", "enp6s0/../../etc", "enp6s0\n", "", "a" * 16):
            self.assertRaises(ValueError, dat_mod.val_ifc, txt_val)


class PrbFil(unittest.TestCase):
    def test_atomic_public_json_is_readable_and_has_no_temporary_remnants(self):
        with tempfile.TemporaryDirectory() as txt_tmp:
            pth_dst = Path(txt_tmp) / "contemplation.json"
            dat_tel = {"schema": 1, "rx_bps": 123.5, "firewall": {"total": 1}}
            dat_mod.guarda(pth_dst, dat_tel)
            self.assertEqual(json.loads(pth_dst.read_text()), dat_tel)
            self.assertEqual(stat.S_IMODE(pth_dst.stat().st_mode), 0o644)
            dat_tel["rx_bps"] = 321
            dat_mod.guarda(pth_dst, dat_tel)
            self.assertEqual(json.loads(pth_dst.read_text()), dat_tel)
            self.assertEqual([p.name for p in Path(txt_tmp).iterdir()], ["contemplation.json"])

    def test_symlink_target_or_directory_cannot_redirect_public_writes(self):
        with tempfile.TemporaryDirectory() as txt_tmp:
            pth_tmp = Path(txt_tmp)
            pth_prv = pth_tmp / "private"
            pth_prv.write_text("private-data")
            pth_dst = pth_tmp / "contemplation.json"
            pth_dst.symlink_to(pth_prv)
            self.assertRaises(ValueError, dat_mod.guarda, pth_dst, {"schema": 1})
            self.assertEqual(pth_prv.read_text(), "private-data")
            pth_dir = pth_tmp / "real"
            pth_dir.mkdir()
            pth_lnk = pth_tmp / "link"
            pth_lnk.symlink_to(pth_dir, target_is_directory=True)
            self.assertRaises(
                ValueError, dat_mod.guarda, pth_lnk / "contemplation.json", {"schema": 1}
            )

    def test_installer_defaults_to_non_mutating_review(self):
        with tempfile.TemporaryDirectory() as txt_tmp:
            pth_tmp = Path(txt_tmp)
            (pth_tmp / "index.html").write_text("Existing site")
            dat_res = subprocess.run([
                sys.executable, str(pth_rad / "deploy/contemplation/install.py"),
                "--root", str(pth_tmp)
            ], check=True, text=True, capture_output=True)
            self.assertIn("Dry run: no files or accounts were changed.", dat_res.stdout)
            self.assertEqual([p.name for p in pth_tmp.iterdir()], ["index.html"])


if __name__ == "__main__":
    unittest.main()
