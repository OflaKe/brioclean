import pandas as pd
import matplotlib.pyplot as plt

# Function to fetch measurements from the database
def fetch_measurements():
    conn = sqlite3.connect {data.db}
    c = conn.cursor()
    c.execute(f"SELECT * FROM {value} ORDER BY measurement DESC LIMIT 10")
    measurements = c.fetchall()
    conn.close()
    return measurements

# Route for historical data analysis and visualization
@app.route('/history')
def history():
    measurements = fetch_measurements()  # Fetch measurements from the database
    df = pd.DataFrame(measurements, columns=['measurement', 'value'])
    
    # Perform data analysis and visualization tasks
    # Example: Create a line plot of measurement values over time
    plt.plot(df['measurement'], df['value'])
    plt.xlabel('Measurement')
    plt.ylabel('Value')
    plt.title('Historical Measurement Data')
    plt.show()

    return '', 200
