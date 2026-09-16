#!/usr/bin/env bash
# Builds the Vespergard web export inside a Vercel build container.
#
# Vercel's build image carries no game engine, so this fetches Godot and the
# web export template, imports the project, and exports into build/web — the
# directory vercel.json names as outputDirectory. Nothing here is Vercel
# specific beyond the defaults; `tools/vercel_build.sh` on any Linux box with
# curl produces the same directory, which is what tools/serve_web.sh serves.
#
# The engine binary only links glibc (X11/GL are dlopen'd and --headless never
# asks for them), so it runs on the stock build image without extra packages.
set -euo pipefail
cd "$(dirname "$0")/.."

GODOT_VERSION="${GODOT_VERSION:-4.7}"
BASE="https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}-stable"
TOOLS_DIR="${TOOLS_DIR:-$PWD/.godot-toolchain}"
TEMPLATE_DIR="$HOME/.local/share/godot/export_templates/${GODOT_VERSION}.stable"
GODOT_BIN="$TOOLS_DIR/godot"

# GitHub's CDN drops long transfers now and then; resume rather than restart.
fetch() {
	local url="$1" out="$2"
	for attempt in 1 2 3 4 5; do
		if curl -sSL -C - --retry 3 --retry-delay 2 -o "$out" "$url"; then
			return 0
		fi
		echo "  attempt $attempt cut off at $(stat -c%s "$out" 2>/dev/null || echo 0) bytes, resuming"
		sleep $((attempt * 2))
	done
	echo "!!! could not download $url" >&2
	return 1
}

# unzip is present on the stock image; python3 is the fallback if it ever isn't.
extract() {
	local zip="$1" dest="$2"; shift 2
	mkdir -p "$dest"
	if command -v unzip >/dev/null 2>&1; then
		unzip -oq "$zip" "$@" -d "$dest"
	else
		python3 - "$zip" "$dest" "$@" <<-'PY'
			import sys, zipfile, fnmatch
			zf, dest, pats = sys.argv[1], sys.argv[2], sys.argv[3:]
			with zipfile.ZipFile(zf) as z:
			    names = z.namelist() if not pats else [
			        n for n in z.namelist() if any(fnmatch.fnmatch(n, p) for p in pats)]
			    z.extractall(dest, names)
		PY
	fi
}

mkdir -p "$TOOLS_DIR"

if [ ! -x "$GODOT_BIN" ]; then
	echo "==> Godot ${GODOT_VERSION} editor"
	fetch "$BASE/Godot_v${GODOT_VERSION}-stable_linux.x86_64.zip" "$TOOLS_DIR/godot.zip"
	extract "$TOOLS_DIR/godot.zip" "$TOOLS_DIR"
	mv "$TOOLS_DIR/Godot_v${GODOT_VERSION}-stable_linux.x86_64" "$GODOT_BIN"
	chmod +x "$GODOT_BIN"
	rm -f "$TOOLS_DIR/godot.zip"
fi

if [ ! -f "$TEMPLATE_DIR/web_release.zip" ]; then
	echo "==> web export template"
	# The template bundle ships every platform in one 1.3 GB archive; only the
	# web entries are unpacked, so the build stays inside the disk allowance.
	fetch "$BASE/Godot_v${GODOT_VERSION}-stable_export_templates.tpz" "$TOOLS_DIR/templates.tpz"
	extract "$TOOLS_DIR/templates.tpz" "$TOOLS_DIR/tpl" "templates/web*" "templates/version.txt"
	mkdir -p "$TEMPLATE_DIR"
	mv "$TOOLS_DIR/tpl/templates/"* "$TEMPLATE_DIR/"
	rm -rf "$TOOLS_DIR/tpl" "$TOOLS_DIR/templates.tpz"
fi

echo "==> importing project resources"
"$GODOT_BIN" --headless --path . --import 2>&1 | tail -2 || true

echo "==> exporting Web preset"
mkdir -p build/web
"$GODOT_BIN" --headless --path . --export-release "Web" build/web/index.html 2>&1 | tail -3

# An export that fails part way still exits 0, so check the artifacts it owes.
for f in index.html index.js index.wasm index.pck; do
	if [ ! -s "build/web/$f" ]; then
		echo "!!! export did not produce build/web/$f" >&2
		exit 1
	fi
done

echo "==> build/web ready"
ls -la build/web
