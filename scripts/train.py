from time import time
import torch
from torch.autograd import Variable
from scripts.utils import *
from data.dataset import  *

def dataloader(train_path, val_path):
    train_data_path = './train.h5py'
    val_data_path = './validation.h5py'
    composed = transforms.Compose([ToTensor()])
    sess_sel = {'train': train_data_path, 'val': val_data_path}
    transformed_dataset = {x: RegistrationDataset(data_dir=sess_sel[x], transform=composed) for x in sess_sel}
    dataloaders = {x: utils.data.DataLoader(transformed_dataset[x], batch_size=4,
                                                 shuffle=True, num_workers=4) for x in sess_sel}
    dataset_sizes = {x: len(transformed_dataset[x]) for x in ['train', 'val']}


    return dataloaders, dataset_sizes


def get_criterion(sched):
    if sched == 'L1-loss':
         sched_sel = torch.nn.L1Loss
    elif sched == "L2-loss":
         sched_sel = torch.nn.MSELoss
    elif sched == "W-GAN":
        pass
    else:
        raise ValueError(' the criterion is not implemented')



def train_model(model, dataloaders,dataset_sizes, criterion_sched, optimizer, scheduler, num_epochs=25):
    since = time.time()

    best_model_wts = model.state_dict()
    best_loss = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                scheduler.step()
                model.train(True)  # Set model to training mode
            else:
                model.train(False)  # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for data in dataloaders[phase]:
                # get the inputs
                moving, target = get_pair(data, pair= True)
                input = organize_data(moving, target, sched='depth_concat')

                # wrap them in Variable
                if use_gpu:
                    moving = Variable(input.cuda())
                    target = Variable(target.cuda())
                else:
                    moving = Variable(input)
                    target = Variable(target)


                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                outputs = model(input)
                _, preds = torch.max(outputs.data, 1)
                criterion = get_criterion(criterion_sched)
                loss = criterion(input, target)

                # backward + optimize only if in training phase
                if phase == 'train':
                    loss.backward()
                    optimizer.step()

                # statistics
                running_loss += loss.data[0]

            epoch_loss = running_loss / dataset_sizes[phase]

            print('{} Loss: {:.4f}'.format(
                phase, epoch_loss))

            # deep copy the model
            if phase == 'val' and epoch_loss > best_loss:
                best_loss = epoch_loss
                best_model_wts = model.state_dict()

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Loss: {:4f}'.format(best_loss))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model
