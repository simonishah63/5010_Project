import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Load actual output
convergence = pd.read_csv("/app/plot_data/convergence_all.csv")
final = pd.read_csv("/app/plot_data/final_generation_all.csv")
jmeter_df = pd.read_csv("/app/plot_data/results.csv")

output_pdf = "/app/plot_data/GA_Evaluation_From_Real_Run.pdf"

with PdfPages(output_pdf) as pdf:

    # Figure 1: Convergence
    plt.figure()
    plt.plot(convergence['generation'], convergence['avg_cost'], label="Avg Cost", linewidth=2)
    plt.plot(convergence['generation'], convergence['avg_availability'], label="Avg Availability", linewidth=2)
    plt.xlabel("Generation")
    plt.ylabel("Metric Value")
    plt.title("Figure 1: GA Convergence of Avg Cost & Availability Across Generations")
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # Figure 2: Pareto Front
    plt.figure()
    plt.scatter(final['latency'], final['cost'], c=final['availability'], cmap='viridis', s=80, edgecolors='k')
    plt.colorbar(label='Availability')
    plt.xlabel("Latency (s)")
    plt.ylabel("Cost ($)")
    plt.title("Figure 2: Pareto Front (Final Generation)")
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # Figure 3: Distribution
    plt.figure()
    plt.hist(final['cost'], bins=10, alpha=0.6, label='Cost')
    plt.hist(final['availability'], bins=10, alpha=0.6, label='Availability')
    plt.hist(final['latency'], bins=10, alpha=0.6, label='Latency')
    plt.title("Figure 3: Final Generation Metric Distribution")
    plt.xlabel("Metric Value")
    plt.ylabel("Individuals")
    plt.legend()
    plt.grid(True)
    pdf.savefig()
    plt.close()

    jmeter_df['second'] = (jmeter_df['timeStamp'] / 1000).astype(int)
    grouped = jmeter_df.groupby('second')['elapsed'].mean().reset_index()

    # Plot response time over time/load
    plt.figure()
    plt.plot(grouped['second'], grouped['elapsed'], color='blue', label='Avg Response Time')
    plt.xlabel("Time (s)")
    plt.ylabel("Response Time (ms)")
    plt.title("Figure 4: Response Time vs Time (Load Simulation)")
    plt.grid(True)
    plt.legend()
    pdf.savefig()
    plt.close()

print(f"✅ PDF generated at: {output_pdf}")