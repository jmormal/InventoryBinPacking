import os
import pandas as pd
import shutil
# In this script we are going to expand the datasets

# Each instance is a folder in the dataset is in the folder datasets
# We want to expand the dataset by adding more instances to it
# To do so we are going to duplicate the instances in the dataset and change the Demanda.csv file
# by taking into account the firs t days. For example, if we have 10 days in the dataset and we want to
# expand it to 20 days, we are going to take the first 10 days of the Demanda.csv file and duplicate them
# in the new Demanda.csv file
# We can also reduce the number of days in the dataset by taking the first days of the Demanda.csv file

# First we are going to reduce the number of days in the dataset
folders = os.listdir('datasets')

for t in [2,5,7]:
    # Get the folders in the dataset
    # For each folder in the dataset
    for folder in folders:
        # Copy the folder to a new folder using shutil
        shutil.copytree('datasets/' + folder, 'datasets/' + folder + '_reduced_' + str(t))
        # Open the Demanda.csv file
        # The headers are i,t,Demanda
        # We are going to use pandas
        df = pd.read_csv('datasets/' + folder + '_reduced_' + str(t) + '/Demanda.csv')
        # eliminate any line that is not a header or a line with t > t
        df = df[df['t'] <= t]
        # Save the new Demanda.csv file
        df.to_csv('datasets/' + folder + '_reduced_' + str(t) + '/Demanda.csv', index=False)


