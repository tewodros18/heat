import heat as ht

import os
import torch

from heat.core.tests.test_suites.basic_test import TestCase
import unittest
# print("after first imports")

class TestDASO(unittest.TestCase):
    def test_daso(self):
        import heat.nn.functional as F
        import heat.optim as optim
        #from heat.optim.lr_scheduler import StepLR
        #from heat.utils import vision_transforms
        #from heat.utils.data.mnist import MNISTDataset

        # class Net(ht.nn.Module):
        #     def __init__(self):
        #         super(Net, self).__init__()
        #         self.conv1 = ht.nn.Conv2d(1, 32, 3, 1)
        #         self.conv2 = ht.nn.Conv2d(32, 64, 3, 1)
        #         self.dropout1 = ht.nn.Dropout2d(0.25)
        #         self.dropout2 = ht.nn.Dropout2d(0.5)
        #         self.fc1 = ht.nn.Linear(9216, 128)
        #         self.fc2 = ht.nn.Linear(128, 10)
        #
        #     def forward(self, x):
        #         x = self.conv1(x)
        #         x = F.relu(x)
        #         x = self.conv2(x)
        #         x = F.relu(x)
        #         x = F.max_pool2d(x, 2)
        #         x = self.dropout1(x)
        #         x = torch.flatten(x, 1)
        #         x = self.fc1(x)
        #         x = F.relu(x)
        #         x = self.dropout2(x)
        #         x = self.fc2(x)
        #         output = F.log_softmax(x, dim=1)
        #         return output

        class Model(ht.nn.Module):
            def __init__(self):
                super(Model, self).__init__()
                # 1 input image channel, 6 output channels, 3x3 square convolution
                # kernel
                self.conv1 = ht.nn.Conv2d(1, 6, 3)
                self.conv2 = ht.nn.Conv2d(6, 16, 3)
                # an affine operation: y = Wx + b
                self.fc1 = ht.nn.Linear(16 * 6 * 6, 120)  # 6*6 from image dimension
                self.fc2 = ht.nn.Linear(120, 84)
                self.fc3 = ht.nn.Linear(84, 10)

            def forward(self, x):
                # Max pooling over a (2, 2) window
                x = self.conv1(x)
                x = F.max_pool2d(F.relu(x), (2, 2))
                # If the size is a square you can only specify a single number
                x = F.max_pool2d(F.relu(self.conv2(x)), 2)
                x = x.view(-1, self.num_flat_features(x))
                x = F.relu(self.fc1(x))
                x = F.relu(self.fc2(x))
                x = self.fc3(x)
                return x

            @staticmethod
            def num_flat_features(x):
                size = x.size()[1:]  # all dimensions except the batch dimension
                num_features = 1
                for s in size:
                    num_features *= s
                return num_features

        class TestDataset(ht.utils.data.Dataset):
            def __init__(self, array, ishuffle):
                super(TestDataset, self).__init__(array, ishuffle=ishuffle)

            def __getitem__(self, item):
                return self.data[item]

            def Ishuffle(self):
                if not self.test_set:
                    ht.utils.data.dataset_ishuffle(self, attrs=[["data", None]])

            def Shuffle(self):
                if not self.test_set:
                    ht.utils.data.dataset_shuffle(self, attrs=[["data", None]])

        def train(model, device, train_loader, optimizer):
            model.train()
            optimizer.last_batch = 20
            loss_fn = torch.nn.MSELoss()
            #print("before loader")
            #for batch_idx, data in enumerate(train_loader):
            for b in range(20):
                data = torch.rand(2, 1, 32, 32)
                target = torch.randn((2, 10), device=ht.get_device().torch_device)
                #print(b)
                data, target = data.to(device), target.to(device)
                optimizer.zero_grad()
                output = model(data)
                loss = loss_fn(output, target)
                ret_loss = loss.clone().detach()
                loss.backward()
                optimizer.step()
                #if b == 20:
                #    break
                # print(b)
            return ret_loss

        # Training settings
        args = {"epochs": 14, "batch_size": 2}
        # todo: break if there is no GPUs / CUDA
        if not torch.cuda.is_available() and ht.MPI_WORLD.size < 8:
            return
        torch.manual_seed(1)

        gpus = torch.cuda.device_count()
        loc_rank = ht.MPI_WORLD.rank % gpus
        device = "cuda:" + str(loc_rank)
        port = str(29500)  # + (args.world_size % args.gpus))
        os.environ["MASTER_ADDR"] = "localhost"
        os.environ["MASTER_PORT"] = port  # "29500"
        os.environ["NCCL_SOCKET_IFNAME"] = "ib"
        #print("before process group init")
        torch.distributed.init_process_group(backend="nccl", rank=loc_rank, world_size=gpus)
        torch.cuda.set_device(device)
        device = torch.device("cuda")
        #print('before data generation')
        data = ht.random.rand(2 * ht.MPI_WORLD.size, 1, 32, 32, split=0)
        #print("before dataset")
        dataset = TestDataset(data, ishuffle=True)
        dataloader = ht.utils.data.datatools.DataLoader(dataset=dataset, batch_size=2)

        model = Model().to(device)
        optimizer = optim.SGD(model.parameters(), lr=1.0)
        daso_optimizer = ht.optim.DASO(
            local_optimizer=optimizer,
            total_epochs=args["epochs"],
            max_global_skips=8,
            stability_level=0.9999,  # this should make it drop every time (hopefully)
            warmup_epochs=1,
            cooldown_epochs=1,
            use_mpi_groups=False,
            #verbose=True,
        )
        # scheduler = StepLR(optimizer, step_size=1, gamma=0.7)
        dp_model = ht.nn.DataParallelMultiGPU(model, daso_optimizer)

        daso_optimizer.print0("finished inti")

        for epoch in range(0, 20):
            ls = train(dp_model, device, dataloader, daso_optimizer)
            # epoch loss logic function to be tested differently
            daso_optimizer.epoch_loss_logic(ls)
            # scheduler.step()
            # if epoch + 1 == 14:
            #     dataloader.last_epoch = True

        # Train()
