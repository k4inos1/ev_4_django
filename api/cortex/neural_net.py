import random
import math


class CortexNN:
    """
    Cortex Neural Network: A pure Python implementation of a Multi-Layer Perceptron.
    Designed for embedding in lightweight systems without heavy ML dependencies.
    """

    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Initialize weights and biases
        # Weights: Layer 1 (Input -> Hidden)
        self.w1 = [
            [random.uniform(-1, 1) for _ in range(input_size)]
            for _ in range(hidden_size)
        ]
        self.b1 = [random.uniform(-1, 1) for _ in range(hidden_size)]

        # Weights: Layer 2 (Hidden -> Output)
        self.w2 = [
            [random.uniform(-1, 1) for _ in range(hidden_size)]
            for _ in range(output_size)
        ]
        self.b2 = [random.uniform(-1, 1) for _ in range(output_size)]

    def sigmoid(self, x):
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0 if x < 0 else 1

    def sigmoid_derivative(self, x):
        sig = self.sigmoid(x)
        return sig * (1 - sig)

    def forward(self, inputs):
        """
        Forward pass through the network.
        inputs: List of floats
        """
        # Input Layer -> Hidden Layer
        self.z1 = []
        for i in range(self.hidden_size):
            activation = self.b1[i]
            for j in range(self.input_size):
                activation += inputs[j] * self.w1[i][j]
            self.z1.append(activation)

        self.a1 = [self.sigmoid(z) for z in self.z1]

        # Hidden Layer -> Output Layer
        self.z2 = []
        for i in range(self.output_size):
            activation = self.b2[i]
            for j in range(self.hidden_size):
                activation += self.a1[j] * self.w2[i][j]
            self.z2.append(activation)

        self.a2 = [self.sigmoid(z) for z in self.z2]
        return self.a2

    def train(self, inputs, targets):
        """
        Backpropagation algorithm to update weights.
        """
        outputs = self.forward(inputs)

        # Calculate Output Layer Error (MSE Gradient)
        output_errors = []
        output_deltas = []
        for i in range(self.output_size):
            error = targets[i] - outputs[i]
            output_errors.append(error)
            output_deltas.append(error * self.sigmoid_derivative(self.z2[i]))

        # Calculate Hidden Layer Error
        hidden_errors = []
        hidden_deltas = []
        for i in range(self.hidden_size):
            error = 0.0
            for j in range(self.output_size):
                error += output_deltas[j] * self.w2[j][i]
            hidden_errors.append(error)
            hidden_deltas.append(error * self.sigmoid_derivative(self.z1[i]))

        # Update Weights Layer 2 (Hidden -> Output)
        for i in range(self.output_size):
            for j in range(self.hidden_size):
                self.w2[i][j] += self.learning_rate * output_deltas[i] * self.a1[j]
            self.b2[i] += self.learning_rate * output_deltas[i]

        # Update Weights Layer 1 (Input -> Hidden)
        for i in range(self.hidden_size):
            for j in range(self.input_size):
                self.w1[i][j] += self.learning_rate * hidden_deltas[i] * inputs[j]
            self.b1[i] += self.learning_rate * hidden_deltas[i]

        return sum([e**2 for e in output_errors]) / len(output_errors)  # MSE

    def save_weights(self, filepath):
        # Implementation for saving state could go here
        pass
