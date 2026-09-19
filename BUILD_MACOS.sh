#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Taxo.app потрібно збирати безпосередньо на macOS." >&2
    exit 1
fi

taxo_python="${TAXO_MACOS_PYTHON:-python3}"
taxo_venv="${TAXO_MACOS_VENV:-.venv-macos}"
"${taxo_python}" -m venv "${taxo_venv}"
"${taxo_venv}/bin/python" -m pip install --upgrade pip
"${taxo_venv}/bin/python" -m pip install -r requirements-build-macos.txt
"${taxo_venv}/bin/python" -m unittest discover -s tests -v
"${taxo_venv}/bin/python" -m PyInstaller --noconfirm --clean Taxo_macos.spec

taxo_app="dist/Taxo.app"
taxo_executable="${taxo_app}/Contents/MacOS/Taxo"
taxo_arch="$(uname -m)"
taxo_bundle_dir="Taxo_v9_1_candidate_r9_9_macOS_${taxo_arch}"
taxo_zip="${taxo_bundle_dir}_Portable.zip"

[[ -x "${taxo_executable}" ]]
if find "${taxo_app}" -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -print -quit | grep -q .; then
    echo "У Taxo.app неочікувано знайдено базу даних." >&2
    exit 1
fi
codesign --verify --deep --strict "${taxo_app}"
mkdir "${taxo_bundle_dir}"
mv "${taxo_app}" "${taxo_bundle_dir}/Taxo.app"
/usr/bin/ditto -c -k --sequesterRsrc --keepParent "${taxo_bundle_dir}" "${taxo_zip}"
shasum -a 256 "${taxo_zip}" > "SHA256SUMS_v9_1_candidate_r9_9_macOS_${taxo_arch}.txt"
echo "Готово: ${taxo_zip}"
