import torch
import torchvision.transforms as transforms
from PIL import Image
import os

# 加载预训练的DINO模型
dino_model = torch.hub.load('facebookresearch/dinov2', "dinov2_vitb14")
dino_model.eval()

# 定义图像预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 函数：提取图像特征
def extract_features(image_path):
    image = Image.open(image_path).convert("RGB")
    image = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        features = dino_model(image)
    return features.squeeze(0)

# 计算参考图像集的特征
reference_dir = "pic_DALL-E_all/"
reference_features = []
reference_filenames = []
for filename in os.listdir(reference_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        path = os.path.join(reference_dir, filename)
        features = extract_features(path)
        reference_features.append(features)
        reference_filenames.append(filename)
reference_features = torch.stack(reference_features)


# 归一化特征
reference_features = torch.nn.functional.normalize(reference_features, dim=1)


# 计算测试图像的特征并找出最相似的参考图像
test_dir = "pic_test/"
for test_filename in os.listdir(test_dir):
    if test_filename.endswith(('.png', '.jpg', '.JPEG')):
        test_path = os.path.join(test_dir, test_filename)
        test_features = extract_features(test_path)
        test_features = torch.nn.functional.normalize(test_features, dim=0)

        # 计算余弦相似度
        similarity = torch.mm(test_features.unsqueeze(0), reference_features.t())
        top_similarities, top_indices = similarity.topk(3)

        # 打印结果
        print(f"Test Image: {test_filename}")
        for i, index in enumerate(top_indices.squeeze(0)):
            print(f"{i+1}: Similar Image: {reference_filenames[index]} with similarity score: {top_similarities.squeeze(0)[i].item()}")
        print("-----------")
