# NLP-Job-Finder
Analysis of different Machine Learning models for the task of categorizing job descriptions
![Diagram of Data Flow](https://raw.githubusercontent.com/ShohamWeiss/NLP-Job-Finder/main/Graphs/general_diagram.png?token=GHSAT0AAAAAACAZNVMNPQ2JVGKCF2CBCPHMZCO6FQQ)

## Google Drive Folder
https://drive.google.com/drive/folders/1aZVaT2xd5K0hF9vRTa6_LW6NBeFL6sLG?usp=sharing

## Results
| Model  |Parameter Count/ Features Used | Experience Level F1 score | Education Level F1 score | Job Type F1 score | Job Title F1 score |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| Multinomial Naive Bayes | 39,458 | 0.73 | 0.37 | 0.89 | 0.57 |
| Gaussian Naive Bayes | 39,458 | **0.83** | 0.36 | **0.95** | 0.60 |
| Support Vector Machine | 39,458 | 0.73 | 0.46 | 0.92 | 0.56 |
| Random Forest Classifier | 39,458 | 0.51 | **0.49** | 0.89 | 0.26 |
| Custom Transformer | 7,263,706 | 0.70 | 0.43 | 0.92 | **0.67** | 
| Finetuned Distilbert | 66,958,086 | 0.75| 0.46 | **0.95** | 0.60 |
