from flask import Flask, render_template
import main # Import your existing logic!

app = Flask(__name__)

@app.route("/")
def dashboard():
    # --- FIX IS HERE: These two lines were missing ---
    filepath = 'requirements.txt'
    dependencies = main.parse_requirements(filepath)
    
    results = []
    # Now the 'dependencies' list exists before the loop starts
    for package in dependencies:
        data = main.get_package_data(package)
        if data:
            # Get the latest version to pass to the scanner
            latest_version = data.get('info', {}).get('version')
            score, factors = main.calculate_trust_score(data, latest_version)
            results.append({"name": package, "score": score, "factors": factors})
    
    # --- Calculate summary stats ---
    if results:
        results.sort(key=lambda x: x['score'])
        lowest_score = results[0]['score']
        average_score = int(sum(r['score'] for r in results) / len(results))
    else:
        lowest_score = "N/A"
        average_score = "N/A"

    # --- Send all data to the HTML page ---
    return render_template('index.html', 
                           results=results, 
                           package_count=len(results),
                           lowest_score=lowest_score,
                           average_score=average_score)

if __name__ == '__main__':
    app.run(debug=True)