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
taxo_zip="Taxo_v8_66_TEST_r1_macOS_${taxo_arch}_Portable.zip"

[[ -x "${taxo_executable}" ]] || { echo "Не знайдено ${taxo_executable}" >&2; exit 1; }
find "${taxo_app}" -name 'Бланк підтвердження.docx' -print -quit | grep -q .
find "${taxo_app}" -name 'attestation_visual_template.pdf' -print -quit | grep -q .
if find "${taxo_app}" -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -print -quit | grep -q .; then
    echo "У Taxo.app неочікувано знайдено базу даних." >&2
    exit 1
fi

codesign --verify --deep --strict "${taxo_app}"
/usr/bin/ditto -c -k --sequesterRsrc --keepParent "${taxo_app}" "${taxo_zip}"
shasum -a 256 "${taxo_zip}" > "SHA256SUMS_v8_66_macOS_${taxo_arch}.txt"

echo "Готово: ${taxo_zip}"
cat "SHA256SUMS_v8_66_macOS_${taxo_arch}.txt"
