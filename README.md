# Long-Lung-application
Long Lung application demo for lung cancer CT-scan classification and segmentation in adddition to showing Pathway of patient-related mutated gene and Drug recommendation 
Input : CT-scan pics (.jpg or .png) and mutated gene from NGS (.csv)
Output : Classification ; Adenocarcinoma, Large cell carcinoma, Squamous cell carcinoma, Benign, Normal 
        Heat map 
        Segmentation : highlighted tumor area 
        Pathway viewer
        Drug recommendation
Model : EfficienNet & U-net
Dataset for Models : https://www.kaggle.com/datasets/lalosalamanca1261/lung-cancer-ct-scans
Datset for drug recommendation : Oncokb

EfficientNet :
              accuracy : 96.47%   support - 736
U-net :
        Dice Score : 0.8324 +/- 0.0832
        IoU Score  : 0.7211 +/- 0.1123
        Precision  : 0.8728 +/- 0.0890
        Recall     : 0.8048 +/- 0.1073

