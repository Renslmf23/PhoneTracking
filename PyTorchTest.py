import os
import numpy as np
import cv2
import torchvision.models.segmentation
import torch
import torchvision.transforms as tf
# if torch.cuda.is_available() and torch.version.hip:
Learning_Rate = 1e-5
width = 800
height = 600  # image width and height
batchSize = 3

TrainFolder = "/home/rens/PycharmProjects/PhoneRecognition/TestData/"
ListImages = os.listdir(os.path.join(TrainFolder, "Images"))  # Create list of images
# ----------------------------------------------Transform image-------------------------------------------------------------------
transformImg = tf.Compose([tf.ToPILImage(), tf.Resize((height, width)), tf.ToTensor(),
                           tf.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
transformAnn = tf.Compose([tf.ToPILImage(), tf.Resize((height, width), tf.InterpolationMode.NEAREST), tf.ToTensor()])


# ---------------------Read image ---------------------------------------------------------
def ReadRandomImage():  # First lets load random image and  the corresponding annotation
    idx = np.random.randint(0, len(ListImages))  # Select random image
    Img = cv2.imread(os.path.join(TrainFolder, "Images", ListImages[idx]))[:, :, 0:3]
    Filled = cv2.imread(os.path.join(TrainFolder, "Annotations", ListImages[idx].replace("render", "unlit")))[:,:,0]
    AnnMap = np.zeros(Img.shape[0:2], np.float32)
    if Filled is not None:  AnnMap[Filled >= 128] = 1
    Img = transformImg(Img)
    AnnMap = transformAnn(AnnMap)
    return Img, AnnMap


# --------------Load batch of images-----------------------------------------------------
def LoadBatch():  # Load batch of images
    images = torch.zeros([batchSize, 3, height, width])
    ann = torch.zeros([batchSize, height, width])
    for i in range(batchSize):
        images[i], ann[i] = ReadRandomImage()
    return images, ann

# --------------Load and set net and optimizer-------------------------------------
device = torch.device('cpu')  # torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
Net = torchvision.models.segmentation.deeplabv3_resnet50(pretrained=True)  # Load net
Net.classifier[4] = torch.nn.Conv2d(256, 3, kernel_size=(1, 1), stride=(1, 1))  # Change final layer to 3 classes
Net = Net.to(device)
optimizer = torch.optim.Adam(params=Net.parameters(), lr=Learning_Rate)  # Create adam optimizer
# ----------------Train--------------------------------------------------------------------------
for itr in range(10):  # Training loop
    images, ann = LoadBatch()  # Load taining batch
    images = torch.autograd.Variable(images, requires_grad=False).to(device)  # Load image
    ann = torch.autograd.Variable(ann, requires_grad=False).to(device)  # Load annotation
    Pred = Net(images)['out']  # make prediction
    Net.zero_grad()
    criterion = torch.nn.CrossEntropyLoss()  # Set loss function
    Loss = criterion(Pred, ann.long())  # Calculate cross entropy loss
    Loss.backward()  # Backpropogate loss
    optimizer.step()  # Apply gradient descent change to weight
    seg = torch.argmax(Pred[0], 0).cpu().detach().numpy()  # Get  prediction classes
    print(itr, ") Loss=", Loss.data.cpu().numpy())
    if itr % 1000 == 0:  # Save model weight once every 60k steps permenant file
        print("Saving Model" + str(itr) + ".torch")
        torch.save(Net.state_dict(), str(itr) + ".torch")
torch.save(Net.state_dict(), "Final.torch")
