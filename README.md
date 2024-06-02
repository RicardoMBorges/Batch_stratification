### Stratification Analysis of Herbarium Sample Data


This Jupyter Notebook performs a stratification analysis on herbarium sample data. It evaluates whether the samples are correctly stratified into batches by comparing the distribution of taxonomic families and genera within each batch to the overall distribution in the original dataset. The analysis is performed using bar plots and Chi-square statistical tests.
Contents

    Data Loading and Preparation:
        Load the expanded herbarium sample dataset.
        Create a new column for sample counts.

    Batch Generation:
        Automatically calculate the number of batches based on the dataset size and a specified batch size.
        Split the data into stratified batches.

    Visualization:
        Generate bar plots to visualize the distribution of families and genera in the overall dataset and in each batch.
        Display the bar plots in a combined subplot layout for easy comparison.

    Statistical Analysis:
        Perform Chi-square tests to compare the observed and expected frequencies of families and genera in each batch.
        Evaluate and interpret the results to determine if stratification was achieved.

    Result Interpretation:
        Print a summary message based on the Chi-square test p-values, indicating whether the stratification was successful.

How to Use

    Clone the Repository:

    sh

git clone https://github.com/yourusername/herbarium-stratification-analysis.git
cd herbarium-stratification-analysis

Install Dependencies:

    Ensure you have Jupyter Notebook installed. You can install it using pip:

sh

pip install jupyter

    Install the required Python packages:

sh

pip install pandas plotly scipy

Run the Notebook:

    Launch Jupyter Notebook:

sh

    jupyter notebook

        Open the Stratification_Analysis.ipynb notebook and run the cells.

Key Results

    Bar Plots: Visual comparisons of the distribution of families and genera in the overall dataset and in each batch.
    Chi-square Test Results: Statistical evaluation showing p-values and Chi-square statistics for each batch.
    Interpretation Message: A summary message that indicates whether the observed distributions in the batches match the expected distributions derived from the overall dataset.

Example Chi-square Test Results
batch	chi2_family	p_family	chi2_genus	p_genus
1	0.19	1.00	0.28	1.00
2	0.32	1.00	0.58	1.00
3	0.07	1.00	0.17	1.00

High p-values (close to 1) suggest that there is no significant difference between the observed and expected distributions for families and genera in each batch. This means that the observed frequencies in your batches are very close to the expected frequencies derived from the overall dataset.
License

This project is licensed under the MIT License. See the LICENSE file for details.
