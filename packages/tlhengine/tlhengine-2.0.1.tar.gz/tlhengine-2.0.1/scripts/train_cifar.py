import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision import datasets, models
from torch.nn.parallel import DistributedDataParallel as DDP
import os
import argparse

# Parse command line arguments for multi-GPU setup
def parse_args():
    parser = argparse.ArgumentParser(description='PyTorch Multi-GPU Training')
    parser.add_argument('--world-size', default=1, type=int, help='Number of nodes for distributed training')
    parser.add_argument('--local-rank', default=0, type=int, help='Rank of this node')
    parser.add_argument('--dist-url', default='tcp://127.0.0.1:23456', type=str, help='URL for initializing distributed training')
    parser.add_argument('--dist-backend', default='nccl', type=str, help='Backend for distributed training')
    return parser.parse_args()

def main():
    # Argument parsing for multi-GPU setup
    args = parse_args()

    # Initialize distributed training
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'  # Modify according to your GPU setup
    torch.distributed.init_process_group(backend=args.dist_backend, init_method=args.dist_url,
                                         world_size=args.world_size, rank=args.local_rank)

    # ResNet50 model with pretrained weights
    model = models.resnet50(pretrained=True)

    # Move model to the GPU
    model = model.cuda()

    # Wrap model in DistributedDataParallel
    model = DDP(model)

    # Data transformations for resizing to larger than 224x224
    transform = transforms.Compose([
        transforms.Resize(256),  # Resize to 256x256
        transforms.CenterCrop(224),  # Crop to 224x224
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    data_root = '~/datasets/'
    # Download and load CIFAR-10 dataset
    trainset = datasets.CIFAR10(root=data_root, train=True, download=True, transform=transform)
    train_sampler = torch.utils.data.DistributedSampler(trainset, num_replicas=args.world_size, rank=args.local_rank)
    trainloader = DataLoader(trainset, batch_size=32, shuffle=False, num_workers=4, sampler=train_sampler)



    # Validation set (use the test set of CIFAR-10)
    testset = datasets.CIFAR10(root=data_root, train=False, download=True, transform=transform)
    testloader = DataLoader(testset, batch_size=32, shuffle=False, num_workers=4)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss().cuda()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    # Training loop
    for epoch in range(10):  # Train for 10 epochs
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        # Training phase
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            inputs, labels = inputs.cuda(), labels.cuda()

            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            if i % 100 == 99:  # Print every 100 mini-batches
                print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 100:.3f}")
                running_loss = 0.0

        # Print accuracy after each epoch
        print(f"Epoch {epoch + 1} training accuracy: {100 * correct / total:.2f}%")

        # Validation phase
        model.eval()  # Set the model to evaluation mode
        correct = 0
        total = 0
        with torch.no_grad():  # No need to compute gradients during validation
            for data in testloader:
                inputs, labels = data
                inputs, labels = inputs.cuda(), labels.cuda()

                # Forward pass
                outputs = model(inputs)
                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        print(f"Epoch {epoch + 1} validation accuracy: {100 * correct / total:.2f}%")

    print("Finished Training")
    
    # Clean up distributed training
    torch.distributed.destroy_process_group()

if __name__ == '__main__':
    main()
