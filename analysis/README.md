### Analysis code for experiment investigating the relation between perception of the Enigma Illusion and microsaccade rates

The details of the participants from whom you collected data can be found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1fhUSIICf9VUJdbGJ3jSWCKc3_1ejxcW0oUEZCijZA_g/edit?usp=sharing)

#### Primary Analysis

- The main script to generate figures is **generateFigures.py**. Simply put in your ID (A, B, C, etc.) or "full" for the entire cohort of participants. This would generate the following two figures:
    - A figure for microsaccade metrics (main sequence and distribution of direction). This output will be in the folder figures/saccadeMetric.
    - A figure showing the microsaccade rate as a function of time relative to reported transitions, i.e. button presses, for both the main illusion condition (Blocks 1-4) and the control condition (Blocks 5-8). It also shows the median reaction time with a dashed vertical line and the median of the standard deviation of reaction times, across subjects, with a gray band. Significant epochs, p<0.05 after correcting for multiple comparisons, are shown with red bars with a * symbol on top.
- All data files essential to running the above are provided here in the folder "datafiles".

#### Access to raw data (optional)

- The raw data for the experiment can be downloaded from [this link](https://syncandshare.lrz.de/getlink/fiVigV7Xped7NYGfc729md/). This would also allow you to rerun the saccade detection algorithm (in saccadeDetection.py). Note that the saccade detection script would _not_ run without the raw data.
- Note that you would have to specify the path to the raw data in this script. The parameter to the function is called _rawdatadirectory_.
- You can also visualize the detected saccades, overlaid on the raw data, with the script vizualizeDetectedSaccades.py . Note again that you would have to specify the path to the raw data. 
