### Analysis code for experiment investigating the relation between perception of the Enigma Illusion and microsaccade rates

The details of the participant you collected can be found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1fhUSIICf9VUJdbGJ3jSWCKc3_1ejxcW0oUEZCijZA_g/edit?usp=sharing)

#### Primary Analysis

- The main script to generate figures is **generateFigures.py**. Simply put in your ID (A, B, C, etc.) or "full" for the entire cohort of participants. This would generate the following two figues:
    - A figure for microsaccade saccade metrics (main sequence and distribution of direction). This output will be in the folder figures/saccadeMetric.
    - A figure showing the microssacade rate as a function of time relative to reported transitions, i.e. button presses, for both the main illusion condition (Blocks 1-4) and the control condition (Blocks 5-8). It also shows the median reaction time with a dashed vertical and the median of the standard deviation of reaction times, across subjects, with a gray band. Significant epochs, p<0.05 after correcting for multiple comparisions, is shown with red bars with a * symbol on top.
- All data files essential to running the above are provided here in the folder "datafiles".

#### Access to raw data (optional)

- The raw data for the experiment can be download from [this link](https://syncandshare.lrz.de/getlink/fiVigV7Xped7NYGfc729md/). This would allow you to also rerun the saccade detection algorithm (in saccadeDetection.py). Note that the saccade detection script would _not_ run without the raw data.
- Note that you would have to specific the path to the raw data in this script. The parameter to the function is called _rawdatadirectory_.
- You can also vizualize the detected saccades, overlaid on the raw data with the script vizualizeDetectedSaccades.py . Note again that you would have to specify the path to the raw data. 
