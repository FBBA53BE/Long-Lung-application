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
        Loss : 0.1946
        Dice : 0.6521
        IoU  : 0.5125

