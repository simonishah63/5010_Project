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

    print(final)
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
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))

    # Subplot 1: Cost
    axs[0].hist(final['cost'], bins=10, color='skyblue', alpha=0.8)
    axs[0].set_title("Distribution of Cost")
    axs[0].set_xlabel("Cost")
    axs[0].set_ylabel("Frequency")
    axs[0].grid(True)

    # Subplot 2: Availability
    axs[1].hist(final['availability'], bins=10, color='lightgreen', alpha=0.8)
    axs[1].set_title("Distribution of Availability")
    axs[1].set_xlabel("Availability")
    axs[1].set_ylabel("Frequency")
    axs[1].grid(True)

    # Subplot 3: Latency
    axs[2].hist(final['latency'], bins=10, color='salmon', alpha=0.8)
    axs[2].set_title("Distribution of Latency")
    axs[2].set_xlabel("Latency")
    axs[2].set_ylabel("Frequency")
    axs[2].grid(True)

    # Adjust layout to avoid overlap
    plt.subplots_adjust(hspace=0.5)
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