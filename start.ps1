get-content .env | ForEach-Object {
    $name, $value = $_.split('=')
    set-content env:\$name $value
}

pip install -r requirements.txt
python main.py