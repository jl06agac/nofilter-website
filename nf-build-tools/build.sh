#!/bin/bash
# Rebuild NoFilter-Website-Master.html from its base plus the patch chain.
#
# Paths are relative to this script, so it runs wherever the folder sits.
# Made portable 4 Sep 2026; it previously hard-coded a cloud session's paths
# and so could not be run on Alex's machine at all — which mattered, because
# "the generator works" is the entire reason the dated master backups were
# safe to delete. Run it, and the master is reproducible. That is the backup.
#
#   ./build.sh            rebuild in place, overwriting the master
#   ./build.sh /tmp/x.html  rebuild to somewhere else, leaving the master alone
set -e
cd "$(dirname "$0")"
M="${1:-../NoFilter-Website-Master.html}"
BASE=base/NoFilter-Website-Master-2026-08-31.html

cp "$BASE" "$M"
for s in patch_css patch_js patch_default patch_badge patch_cursor patch_panel patch_hier patch_cover patch_ladder patch_calib patch_cover2 patch_permachine patch_exit patch_cover3 patch_pill patch_copy patch_steps patch_repin patch_polish patch_gate patch_tidy patch_qty patch_reveal patch_morph2 patch_tile2 patch_morph3 patch_scroll patch_clear patch_once patch_perf patch_freeze patch_row patch_origin patch_abs patch_spec patch_btnpos patch_bounce patch_details patch_noscroll patch_deadspace patch_squeeze patch_rubber patch_failsafe patch_steptop patch_morphstuck patch_qbar patch_switchgap patch_flags patch_perkg patch_hitch patch_footleft patch_bag80 patch_topup patch_settle patch_settle2 patch_settle3 patch_lock patch_hero patch_polish2 patch_ground patch_grid patch_hug patch_6535 patch_wizard patch_dash patch_breathe patch_aed patch_aedcard patch_uk patch_tilefoot patch_gutfoot patch_ukaddr patch_access patch_ukfoot patch_lazyvideo patch_paths patch_idle patch_warm patch_still patch_board patch_gis patch_sound patch_partners patch_pour patch_black patch_access2 patch_paste patch_flow patch_record patch_dossier patch_railroute patch_leadgap patch_volume patch_mobile patch_boot patch_layers patch_routesafe patch_ukmarket patch_ratesplit patch_ratefetch patch_bandmarks patch_machcat patch_media2 patch_scrollroute patch_media3; do
  python3 "patches/$s.py" "$M" >/dev/null || { echo "FAILED at $s"; exit 1; }
done
echo "built OK  $(wc -c < "$M") bytes  $(md5sum "$M" | cut -c1-12)"
