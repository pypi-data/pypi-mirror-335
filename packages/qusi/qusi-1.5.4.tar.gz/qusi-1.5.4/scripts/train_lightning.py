from qusi.internal.lightning_train_session import train_session
from torch.optim import AdamW

from qusi.model import Hadryss
from qusi.session import TrainHyperparameterConfiguration

from scripts.dataset import get_heart_train_dataset, get_heart_validation_dataset


def main():
    train_light_curve_dataset = get_heart_train_dataset()
    validation_light_curve_dataset = get_heart_validation_dataset()
    model = Hadryss.new()
    train_hyperparameter_configuration = TrainHyperparameterConfiguration.new(
        batch_size=1000, cycles=5000, train_steps_per_cycle=100, validation_steps_per_cycle=10)
    optimizer = AdamW(model.parameters(), lr=1e-2)
    train_session(train_datasets=[train_light_curve_dataset], validation_datasets=[validation_light_curve_dataset],
                  model=model, hyperparameter_configuration=train_hyperparameter_configuration, optimizer=optimizer)


if __name__ == '__main__':
    main()
