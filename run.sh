NOTEBOOK_PATH="$1"
CONFIGURATION_PATH="$2"
SOURCE_FOLDER="$3"
TARGET_FOLDER="$4"

SCRIPT_PATH="${1%.ipynb}.py"

$VIRTUAL_ENV/bin/jupyter nbconvert "$NOTEBOOK_PATH" --to script
$VIRTUAL_ENV/bin/python "$SCRIPT_PATH" "$CONFIGURATION_PATH" \
    --source_folder "$SOURCE_FOLDER" \
    --target_folder "$TARGET_FOLDER"
