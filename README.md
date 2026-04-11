# Long-Lung-application
Long Lung application demo for lung cancer CT-scan classification and segmentation
Input : CT-scan pics (.jpg or .png)
Output : Classification ; Adenocarcinoma, Large cell carcinoma, Squamous cell carcinoma, Benign, Normal 
        Heat map 
        Segmentation : highlighted tumor area 
Model : EfficienNet & U-net
Dataset for Models : https://www.kaggle.com/datasets/lalosalamanca1261/lung-cancer-ct-scans

EfficientNet :
              accuracy : 96.47%   support - 736
                        Precision      recall      f1-score    support
Adenocarcinoma             0.93        0.94          0.94      100
Benign                     0.96        0.98          0.97      198
Large cell carcinoma       1.00        0.91          0.95      54
Squamous cell carcinoma    0.92        0.92          0.92      77
Normal                     0.98        0.98          0.98      307

U-net :
        Loss : 0.1946
        Dice : 0.6521
        IoU  : 0.5125

