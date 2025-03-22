def render(code, title, description):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error {code} - {title}</title>
</head>
<body>
    <h1>{code} - {title}</h1>
    <p>{description}</p>
</body>
</html>
"""
