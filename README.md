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
U-net :
        Loss : 0.1946
        Dice : 0.6521
        IoU  : 0.5125

