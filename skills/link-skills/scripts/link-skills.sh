#!/usr/bin/env bash
#
# link-skills.sh: give every AI tool a symlink to each skill in one hub folder.
#
# This script only ever runs `mkdir -p` and `ln -s`. It never deletes or
# overwrites anything. Works on bash 3.2 (macOS) and newer.

set -euo pipefail
unset CDPATH

PROG=$(basename "$0")
KNOWN_TOOLS="claude codex cursor gemini cline kiro"

usage() {
  cat <<USAGE
Usage: $PROG [options]

Link every skill in one hub folder into each AI tool's skills folder.
Each tool gets one symlink per skill. Nothing is deleted or overwritten.

Options:
  --hub DIR        The hub folder that holds every skill.
                   Default: \$HOME/.agents/skills
  --from DIR       A folder of skill folders. Each one with a SKILL.md is
                   linked into the hub first. Without this, only skills
                   already in the hub are linked.
  --only a,b,c     Only these skill names.
  --ai t1,t2       Only these tools. Known: claude, codex, cursor, gemini,
                   cline, kiro. Default: every tool that is installed.
                   Use --ai none to skip the tools and link only into
                   --tool-dir folders.
  --tool-dir DIR   An extra skills folder to link into, such as
                   ./.claude/skills in a project. Can be repeated.
  --dry-run        Show the plan and change nothing.
  --yes            Do not ask before creating links.
  --list-tools     Print the installed tools and their skills folders, then
                   exit. Each line is: name, display name, folder (tab separated).
  -h, --help       Show this help.

A tool counts as installed if its command is on PATH or \$HOME/.<tool> exists.
Its skills folder is \$HOME/.<tool>/skills.

Exit codes: 0 done (conflicts do not change this), 2 usage error.
USAGE
}

die_usage() {
  printf '%s: %s\n' "$PROG" "$1" >&2
  printf 'Try: %s --help\n' "$PROG" >&2
  exit 2
}

display_name() {
  case "$1" in
    claude) printf 'Claude Code' ;;
    codex) printf 'Codex' ;;
    cursor) printf 'Cursor' ;;
    gemini) printf 'Gemini CLI' ;;
    cline) printf 'Cline' ;;
    kiro) printf 'Kiro' ;;
    *) printf '%s' "$1" ;;
  esac
}

is_known_tool() {
  local t
  for t in $KNOWN_TOOLS; do
    [ "$t" = "$1" ] && return 0
  done
  return 1
}

tool_detected() {
  command -v "$1" >/dev/null 2>&1 || [ -d "$HOME/.$1" ]
}

# Split "a,b,c" into the global array CSV_OUT. Spaces are dropped.
split_csv() {
  local csv="${1// /}" item
  local IFS=','
  CSV_OUT=()
  # shellcheck disable=SC2086
  set -- $csv
  for item in "$@"; do
    if [ -n "$item" ]; then CSV_OUT[${#CSV_OUT[@]}]="$item"; fi
  done
}

# Absolute path that may not exist yet. Does not resolve symlinks.
abs_path() {
  local p="$1"
  if [ -d "$p" ]; then
    (cd "$p" && pwd)
    return
  fi
  case "$p" in
    /*) ;;
    *) p="$PWD/${p#./}" ;;
  esac
  while [ "${#p}" -gt 1 ] && [ "${p%/}" != "$p" ]; do p="${p%/}"; done
  printf '%s\n' "$p"
}

# Physical (symlink-free) path of a directory, or nothing if it is not one.
phys_dir() {
  (cd "$1" 2>/dev/null && pwd -P) || true
}

# ---------------------------------------------------------------- arguments

HUB=""
FROM=""
ONLY_CSV=""
AI_CSV=""
DRY_RUN=0
ASSUME_YES=0
LIST_TOOLS=0
TOOL_DIR_COUNT=0
TOOL_DIRS=()

need_value() {
  [ "$2" -ge 2 ] || die_usage "$1 needs a value"
  case "$3" in
    -*) die_usage "$1 needs a value, got '$3'" ;;
  esac
}

while [ $# -gt 0 ]; do
  case "$1" in
    --hub) need_value "$1" "$#" "${2:-}"; HUB="$2"; shift 2 ;;
    --from) need_value "$1" "$#" "${2:-}"; FROM="$2"; shift 2 ;;
    --only) need_value "$1" "$#" "${2:-}"; ONLY_CSV="$2"; shift 2 ;;
    --ai) need_value "$1" "$#" "${2:-}"; AI_CSV="$2"; shift 2 ;;
    --tool-dir)
      need_value "$1" "$#" "${2:-}"
      TOOL_DIRS[TOOL_DIR_COUNT]="$2"
      TOOL_DIR_COUNT=$((TOOL_DIR_COUNT + 1))
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    --yes) ASSUME_YES=1; shift ;;
    --list-tools) LIST_TOOLS=1; shift ;;
    -h | --help) usage; exit 0 ;;
    *) die_usage "unknown option '$1'" ;;
  esac
done

[ -n "${HOME:-}" ] || die_usage "HOME is not set"
[ -n "$HUB" ] || HUB="$HOME/.agents/skills"
HUB=$(abs_path "$HUB")

AI_LIST=()
AI_NONE=0
if [ "$AI_CSV" = "none" ]; then
  AI_NONE=1
elif [ -n "$AI_CSV" ]; then
  split_csv "$AI_CSV"
  AI_LIST=(${CSV_OUT[@]+"${CSV_OUT[@]}"})
  [ "${#AI_LIST[@]}" -gt 0 ] || die_usage "--ai needs at least one tool name"
  for t in "${AI_LIST[@]}"; do
    is_known_tool "$t" || die_usage "unknown tool '$t'. Known tools: ${KNOWN_TOOLS// /, }"
  done
fi

ONLY_LIST=()
if [ -n "$ONLY_CSV" ]; then
  split_csv "$ONLY_CSV"
  ONLY_LIST=(${CSV_OUT[@]+"${CSV_OUT[@]}"})
  [ "${#ONLY_LIST[@]}" -gt 0 ] || die_usage "--only needs at least one skill name"
fi

if [ -n "$FROM" ]; then
  [ -d "$FROM" ] || die_usage "--from folder not found: $FROM"
  FROM=$(abs_path "$FROM")
fi

only_allows() {
  local n
  [ "${#ONLY_LIST[@]}" -eq 0 ] && return 0
  for n in "${ONLY_LIST[@]}"; do
    [ "$n" = "$1" ] && return 0
  done
  return 1
}

ai_allows() {
  local n
  [ "$AI_NONE" -eq 1 ] && return 1
  [ "${#AI_LIST[@]}" -eq 0 ] && return 0
  for n in "${AI_LIST[@]}"; do
    [ "$n" = "$1" ] && return 0
  done
  return 1
}

# ---------------------------------------------------------------- tools

if [ "$LIST_TOOLS" -eq 1 ]; then
  for t in $KNOWN_TOOLS; do
    ai_allows "$t" || continue
    tool_detected "$t" || continue
    printf '%s\t%s\t%s\n' "$t" "$(display_name "$t")" "$HOME/.$t/skills"
  done
  exit 0
fi

TOOL_HEADS=()
TOOL_DIRS_FINAL=()
TOOL_COUNT=0

add_tool() {
  TOOL_HEADS[TOOL_COUNT]="$1"
  TOOL_DIRS_FINAL[TOOL_COUNT]="$2"
  TOOL_COUNT=$((TOOL_COUNT + 1))
}

for t in $KNOWN_TOOLS; do
  ai_allows "$t" || continue
  if tool_detected "$t"; then
    add_tool "$(display_name "$t")" "$HOME/.$t/skills"
  elif [ "${#AI_LIST[@]}" -gt 0 ]; then
    printf 'Note: %s is not installed, so it was skipped.\n' "$(display_name "$t")"
  fi
done

i=0
while [ "$i" -lt "$TOOL_DIR_COUNT" ]; do
  d=$(abs_path "${TOOL_DIRS[$i]}")
  add_tool "" "$d"
  i=$((i + 1))
done

# ---------------------------------------------------------------- planning

N_LINK=0
N_OK=0
N_CONFLICT=0
N_OWN=0
LINK_DESTS=()
LINK_TARGETS=()
SEEN="|"

STATE=""
DETAIL=""

# decide DEST TARGET [FUTURE_PHYS]
# Sets STATE (link, ok, conflict, own) and DETAIL.
# FUTURE_PHYS is the physical path TARGET will have once a planned link exists.
decide() {
  local dest="$1" target="$2" future="${3:-}" d t raw
  DETAIL=""
  t=$(phys_dir "$target")
  [ -n "$t" ] || t="$future"
  if [ -L "$dest" ]; then
    d=$(phys_dir "$dest")
    if [ -n "$d" ] && [ -n "$t" ] && [ "$d" = "$t" ]; then
      STATE="ok"
    else
      STATE="conflict"
      raw=$(readlink "$dest" 2>/dev/null || true)
      if [ -z "$d" ]; then
        DETAIL="points to ${raw:-an unknown place}, which is not a folder"
      else
        DETAIL="points to ${raw:-$d}"
      fi
    fi
  elif [ -d "$dest" ]; then
    d=$(phys_dir "$dest")
    if [ -n "$d" ] && [ -n "$t" ] && [ "$d" = "$t" ]; then
      STATE="ok"
    else
      STATE="own"
      DETAIL="real folder, left alone"
    fi
  elif [ -e "$dest" ]; then
    STATE="own"
    DETAIL="real file, left alone"
  else
    STATE="link"
  fi
}

# plan_pair DEST TARGET [FUTURE_PHYS]
plan_pair() {
  local dest="$1" target="$2" future="${3:-}"
  case "$SEEN" in
    *"|$dest|"*) return 0 ;;
  esac
  SEEN="$SEEN$dest|"
  decide "$dest" "$target" "$future"
  case "$STATE" in
    link)
      printf '  %-10s%s -> %s\n' "link" "$dest" "$target"
      LINK_DESTS[N_LINK]="$dest"
      LINK_TARGETS[N_LINK]="$target"
      N_LINK=$((N_LINK + 1))
      ;;
    ok)
      printf '  %-10s%s -> %s\n' "ok" "$dest" "$target"
      N_OK=$((N_OK + 1))
      ;;
    conflict)
      printf '  %-10s%s -> %s (%s)\n' "conflict" "$dest" "$target" "$DETAIL"
      N_CONFLICT=$((N_CONFLICT + 1))
      ;;
    own)
      printf '  %-10s%s -> %s (%s)\n' "own copy" "$dest" "$target" "$DETAIL"
      N_OWN=$((N_OWN + 1))
      ;;
  esac
}

# Names of skills (folders holding a SKILL.md, not starting with a dot).
SK_NAMES=()
SK_FUTURE=()
SK_COUNT=0
FOUND_NAMES="|"

add_skill() {
  SK_NAMES[SK_COUNT]="$1"
  SK_FUTURE[SK_COUNT]="$2"
  SK_COUNT=$((SK_COUNT + 1))
  FOUND_NAMES="$FOUND_NAMES$1|"
}

printf 'Hub: %s' "$HUB"
[ -d "$HUB" ] || printf ' (will be created)'
printf '\n'

# Step 1: add skills from --from to the hub.
FROM_NAMES=()
FROM_COUNT=0
PLANNED_NAMES=()
PLANNED_PHYS=()
PLANNED_COUNT=0
if [ -n "$FROM" ]; then
  for p in "$FROM"/*; do
    [ -f "$p/SKILL.md" ] || continue
    n=$(basename "$p")
    only_allows "$n" || continue
    FROM_NAMES[FROM_COUNT]="$n"
    FROM_COUNT=$((FROM_COUNT + 1))
  done
  printf '\nAdd to hub from %s\n' "$FROM"
  if [ "$FROM_COUNT" -eq 0 ]; then
    printf '  (no skills found)\n'
  fi
  i=0
  while [ "$i" -lt "$FROM_COUNT" ]; do
    n="${FROM_NAMES[$i]}"
    before=$N_LINK
    plan_pair "$HUB/$n" "$FROM/$n"
    if [ "$N_LINK" -gt "$before" ]; then
      PLANNED_NAMES[PLANNED_COUNT]="$n"
      PLANNED_PHYS[PLANNED_COUNT]=$(phys_dir "$FROM/$n")
      PLANNED_COUNT=$((PLANNED_COUNT + 1))
    fi
    i=$((i + 1))
  done
fi

# Skills that will be in the hub: what is there now, plus what step 1 adds.
if [ -d "$HUB" ]; then
  for p in "$HUB"/*; do
    [ -f "$p/SKILL.md" ] || continue
    n=$(basename "$p")
    only_allows "$n" || continue
    add_skill "$n" ""
  done
fi
i=0
while [ "$i" -lt "$PLANNED_COUNT" ]; do
  add_skill "${PLANNED_NAMES[$i]}" "${PLANNED_PHYS[$i]}"
  i=$((i + 1))
done

for n in ${ONLY_LIST[@]+"${ONLY_LIST[@]}"}; do
  case "$FOUND_NAMES" in
    *"|$n|"*) ;;
    *) printf 'Note: no skill named %s was found.\n' "$n" ;;
  esac
done

# Step 2: link each hub skill into each tool folder.
if [ "$TOOL_COUNT" -eq 0 ]; then
  printf '\nNo AI tools found. Use --tool-dir DIR to link into a folder.\n'
elif [ "$SK_COUNT" -eq 0 ]; then
  printf '\nNo skills found in the hub, so there is nothing to link into the tools.\n'
else
  ti=0
  while [ "$ti" -lt "$TOOL_COUNT" ]; do
    tdir="${TOOL_DIRS_FINAL[$ti]}"
    if [ -n "${TOOL_HEADS[$ti]}" ]; then
      printf '\n%s (%s)' "${TOOL_HEADS[$ti]}" "$tdir"
    else
      printf '\nFolder %s' "$tdir"
    fi
    [ -d "$tdir" ] || printf ' (folder will be created)'
    printf '\n'
    si=0
    while [ "$si" -lt "$SK_COUNT" ]; do
      plan_pair "$tdir/${SK_NAMES[$si]}" "$HUB/${SK_NAMES[$si]}" "${SK_FUTURE[$si]}"
      si=$((si + 1))
    done
    ti=$((ti + 1))
  done
fi

printf '\nSummary: %d to link, %d ok, %d conflict(s), %d own copy(ies).\n' \
  "$N_LINK" "$N_OK" "$N_CONFLICT" "$N_OWN"
if [ $((N_CONFLICT + N_OWN)) -gt 0 ]; then
  printf 'Conflicts and own copies are left alone. Fix them by hand if you want them linked.\n'
fi

# ---------------------------------------------------------------- doing it

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'Dry run. Nothing was changed.\n'
  exit 0
fi

if [ "$N_LINK" -eq 0 ]; then
  [ -d "$HUB" ] || mkdir -p "$HUB"
  printf 'Nothing to link.\n'
  exit 0
fi

if [ "$ASSUME_YES" -ne 1 ]; then
  printf 'Create %d link(s)? [y/N] ' "$N_LINK"
  ANSWER=""
  if ! read -r ANSWER 2>/dev/null </dev/tty; then
    read -r ANSWER || true
  fi
  case "$ANSWER" in
    y | Y) ;;
    *)
      printf 'No changes made.\n'
      exit 0
      ;;
  esac
fi

[ -d "$HUB" ] || mkdir -p "$HUB"

MADE=0
FAILED=0
i=0
while [ "$i" -lt "$N_LINK" ]; do
  dest="${LINK_DESTS[$i]}"
  target="${LINK_TARGETS[$i]}"
  if mkdir -p "$(dirname "$dest")" && ln -s "$target" "$dest"; then
    MADE=$((MADE + 1))
  else
    FAILED=$((FAILED + 1))
    printf 'Could not link %s\n' "$dest" >&2
  fi
  i=$((i + 1))
done

printf 'Created %d link(s).\n' "$MADE"
if [ "$FAILED" -gt 0 ]; then
  printf '%d link(s) failed.\n' "$FAILED" >&2
  exit 1
fi
exit 0
