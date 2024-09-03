import torch
import torch.nn as nn
import torch.optim as optim
from process import flatten_and_pad_sequences

# Define the model class
class NPCModel(nn.Module):
        def __init__(self):
            super(NPCModel, self).__init__()
            self.fc1 = nn.Linear(3, 10)  # Input layer to hidden layer
            self.fc2 = nn.Linear(10, 20)  # Hidden layer to output layer

        def forward(self, x):
            x = torch.relu(self.fc1(x))  # ReLU activation
            x = self.fc2(x)  # Linear output
            return x

# Step 1: Prepare the Data
inputs = []
outputs = []

def train_model(input_data, output_data):
    input_data = flatten_and_pad_sequences(input_data)
    output_data = flatten_and_pad_sequences(output_data)
    model = NPCModel()

    # Step 3: Set Loss and Optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    # Step 4: Train the Model
    epochs = 500
    for epoch in range(epochs):
        # Zero the parameter gradients
        optimizer.zero_grad()

        # Forward pass
        predictions = model(input_data)

        # Compute loss
        loss = criterion(predictions, output_data)

        # Backward pass and optimize
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 50 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    
    # Save the model
    torch.save(model.state_dict(), 'models/model.pth')
    print("Model saved to models/model.pth")
    return model

def test_model(model, test_inputs, test_outputs):
    model.eval()  # Set the model to evaluation mode
    with torch.no_grad():
        predictions = model(test_inputs)
        print("Test Inputs:\n", test_inputs)
        print("Test Outputs:\n", test_outputs)
        print("Predicted Outputs:\n", predictions)

# Train the model
trained_model = train_model(inputs, outputs)

# Load the model (optional, if you want to test loading the saved model)
model = NPCModel()
model.load_state_dict(torch.load('models/model.pth'))
model.eval()  # Set the model to evaluation mode
print("Model loaded from models/model.pth")

# Test the model
test_model(trained_model, inputs, outputs)