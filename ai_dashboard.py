from flask import Flask, render_template, request
import ai_analyzer

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def dashboard():
    result = None
    if request.method == 'POST':
        package_name = request.form.get('package_name')
        if package_name:
            result = ai_analyzer.run_ai_analysis(package_name)
    return render_template('ai_index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Using a different port