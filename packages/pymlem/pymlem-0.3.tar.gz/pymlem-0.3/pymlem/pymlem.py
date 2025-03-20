class PyMlem:
    def __init__(self):
        ...
    
    def cifar10(self):
        return( 
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b234c1b3-fc3d-4b70-9da5-4724c314d679",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import pickle"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d277fffa-e943-4ddb-9ca6-80fbe7476c06",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_cifar10_batch(filename):\n",
    "    with open(filename, 'rb') as f:\n",
    "        batch = pickle.load(f, encoding='bytes')\n",
    "        data = batch[b'data']\n",
    "        labels = np.array(batch[b'labels'])\n",
    "        return data, labels\n",
    "\n",
    "def load_cifar10_data():\n",
    "    x_train, y_train = [], []\n",
    "    for i in range(1, 6):\n",
    "        data, labels = load_cifar10_batch(f'datasets/cifar-10-python/cifar-10-batches-py/data_batch_{i}')\n",
    "        x_train.append(data)\n",
    "        y_train.append(labels)\n",
    "\n",
    "    x_train = np.concatenate(x_train)\n",
    "    y_train = np.concatenate(y_train)\n",
    "\n",
    "    x_test, y_test = load_cifar10_batch(f'datasets/cifar-10-python/cifar-10-batches-py/test_batch')\n",
    "\n",
    "    x_train = x_train / 255.0\n",
    "    x_test = x_test / 255.0\n",
    "\n",
    "    return x_train, y_train, x_test, y_test"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fe5d2112-a7f6-4938-94c9-1cc9ba1ec10a",
   "metadata": {},
   "outputs": [],
   "source": [
    "x_train, y_train, x_test, y_test = load_cifar10_data()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6b179244-6cf1-4903-9786-02f4e7afa3d0",
   "metadata": {},
   "outputs": [],
   "source": [
    "np.random.seed(42)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a26195f1-df7e-479c-b755-e1fdf5da009e",
   "metadata": {},
   "outputs": [],
   "source": [
    "input_size = 3072  # 32x32x3 pixels\n",
    "hidden_size1 = 128\n",
    "hidden_size2 = 64\n",
    "output_size = 10  # CIFAR-10 has 10 classes"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3dc03276-1607-43b9-8df5-5ae9c3a924cd",
   "metadata": {},
   "outputs": [],
   "source": [
    "weights = {\n",
    "    \"W1\": np.random.randn(input_size, hidden_size1) * np.sqrt(2.0 / input_size),\n",
    "    \"b1\": np.zeros((1, hidden_size1)),\n",
    "    \"W2\": np.random.randn(hidden_size1, hidden_size2) * np.sqrt(2.0 / hidden_size1),\n",
    "    \"b2\": np.zeros((1, hidden_size2)),\n",
    "    \"W3\": np.random.randn(hidden_size2, output_size) * np.sqrt(2.0 / hidden_size2),\n",
    "    \"b3\": np.zeros((1, output_size))\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9f4d4e91-a773-4259-a647-f490d01fb4e0",
   "metadata": {},
   "outputs": [],
   "source": [
    "def relu(Z):\n",
    "    return np.maximum(0, Z)\n",
    "\n",
    "def softmax(Z):\n",
    "    expZ = np.exp(Z - np.max(Z, axis=1, keepdims=True))\n",
    "    return expZ / np.sum(expZ, axis=1, keepdims=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "46c107dc-c8a6-492d-81db-e0938309e58d",
   "metadata": {},
   "outputs": [],
   "source": [
    "def forward_propagation(X, weights):\n",
    "    Z1 = np.dot(X, weights[\"W1\"]) + weights[\"b1\"]\n",
    "    A1 = relu(Z1)\n",
    "\n",
    "    Z2 = np.dot(A1, weights[\"W2\"]) + weights[\"b2\"]\n",
    "    A2 = relu(Z2)\n",
    "\n",
    "    Z3 = np.dot(A2, weights[\"W3\"]) + weights[\"b3\"]\n",
    "    A3 = softmax(Z3)\n",
    "\n",
    "    return Z1, A1, Z2, A2, Z3, A3"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dfa678a1-120f-42b1-b5de-a689335a9954",
   "metadata": {},
   "outputs": [],
   "source": [
    "def compute_loss(Y_pred, Y_true, weights, lambda_=0.01):\n",
    "    m = Y_true.shape[0]\n",
    "    log_likelihood = -np.log(Y_pred[range(m), Y_true])\n",
    "    loss = np.sum(log_likelihood) / m\n",
    "\n",
    "    # L2 Regularization\n",
    "    L2_regularization = (lambda_ / (2 * m)) * (\n",
    "        np.sum(weights[\"W1\"] ** 2) + np.sum(weights[\"W2\"] ** 2) + np.sum(weights[\"W3\"] ** 2)\n",
    "    )\n",
    "    return loss + L2_regularization"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a4f8aa75-814a-4188-938a-c420b45dad37",
   "metadata": {},
   "outputs": [],
   "source": [
    "def backpropagation(X, Y_true, A1, A2, A3, weights, learning_rate, lambda_):\n",
    "    m = X.shape[0]\n",
    "    \n",
    "    # One-hot encoding of labels\n",
    "    Y_one_hot = np.zeros((m, output_size))\n",
    "    Y_one_hot[np.arange(m), Y_true] = 1\n",
    "\n",
    "    # Compute gradients\n",
    "    dZ3 = A3 - Y_one_hot\n",
    "    dW3 = (np.dot(A2.T, dZ3) + lambda_ * weights[\"W3\"]) / m\n",
    "    db3 = np.sum(dZ3, axis=0, keepdims=True) / m\n",
    "\n",
    "    dA2 = np.dot(dZ3, weights[\"W3\"].T)\n",
    "    dZ2 = dA2 * (A2 > 0)  # ReLU derivative\n",
    "    dW2 = (np.dot(A1.T, dZ2) + lambda_ * weights[\"W2\"]) / m\n",
    "    db2 = np.sum(dZ2, axis=0, keepdims=True) / m\n",
    "\n",
    "    dA1 = np.dot(dZ2, weights[\"W2\"].T)\n",
    "    dZ1 = dA1 * (A1 > 0)  # ReLU derivative\n",
    "    dW1 = (np.dot(X.T, dZ1) + lambda_ * weights[\"W1\"]) / m\n",
    "    db1 = np.sum(dZ1, axis=0, keepdims=True) / m\n",
    "\n",
    "    # Update weights\n",
    "    weights[\"W1\"] -= learning_rate * dW1\n",
    "    weights[\"b1\"] -= learning_rate * db1\n",
    "    weights[\"W2\"] -= learning_rate * dW2\n",
    "    weights[\"b2\"] -= learning_rate * db2\n",
    "    weights[\"W3\"] -= learning_rate * dW3\n",
    "    weights[\"b3\"] -= learning_rate * db3"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "52e69d58-bff0-4a85-9f7f-b2927cc71200",
   "metadata": {},
   "outputs": [],
   "source": [
    "epochs = 50\n",
    "batch_size = 64\n",
    "lambda_ = 0.01 # L2 regularization factor"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "41eff1b4-91c9-436d-af61-0d42188af288",
   "metadata": {},
   "outputs": [],
   "source": [
    "for epoch in range(epochs):\n",
    "    shuffle_indices = np.random.permutation(x_train.shape[0])\n",
    "    X_train, y_train = x_train[shuffle_indices], y_train[shuffle_indices]\n",
    "\n",
    "    for i in range(0, X_train.shape[0], batch_size):\n",
    "        X_batch = x_train[i:i+batch_size]\n",
    "        y_batch = y_train[i:i+batch_size]\n",
    "\n",
    "        Z1, A1, Z2, A2, Z3, A3 = forward_propagation(X_batch, weights)\n",
    "\n",
    "        learning_rate = 0.01 / (1 + 0.01 * epoch) # Learning rate decay\n",
    "        backpropagation(X_batch, y_batch, A1, A2, A3, weights, learning_rate, lambda_)\n",
    "\n",
    "\n",
    "    _, _, _, _, _, train_pred = forward_propagation(x_train, weights)\n",
    "    train_loss = compute_loss(train_pred, y_train, weights, lambda_)\n",
    "\n",
    "    print(f\"Epoch {epoch+1}/{epochs}, Loss: {train_loss:.4f}\")\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "aa5e98b1-1a25-4518-a18f-13c597dfccbd",
   "metadata": {},
   "outputs": [],
   "source": [
    "def predict(X, weights):\n",
    "    _, _, _, _, _, A3 = forward_propagation(X, weights)\n",
    "    return np.argmax(A3, axis=1)\n",
    "\n",
    "y_pred = predict(x_test, weights)\n",
    "accuracy = np.mean(y_pred == y_test) * 100\n",
    "print(f\"Test Accuracy: {accuracy:.2f}%\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
''')
    
    def dt(self):
        return(
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7028b060-331d-4332-bd0e-30fd49886644",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.feature_extraction.text import CountVectorizer\n",
    "from sklearn.tree import DecisionTreeClassifier\n",
    "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d650733d-e45e-4223-bf4f-b65029a52c1d",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_data(data_dir):\n",
    "    texts, labels = [], []\n",
    "\n",
    "    for label in ['pos', 'neg']:\n",
    "        label_dir = os.path.join(data_dir, label)\n",
    "        for filename in os.listdir(label_dir):\n",
    "            with open(os.path.join(label_dir, filename), encoding='utf-8') as f:\n",
    "                texts.append(f.read())\n",
    "            labels.append(1 if label == 'pos' else 0)\n",
    "\n",
    "    return texts, labels"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "05d240b4-f7c6-47f6-a491-d3300ade9f5f",
   "metadata": {},
   "outputs": [],
   "source": [
    "train_dir = \"datasets/aclImdb/train/\"\n",
    "test_dir = \"datasets/aclImdb/test/\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b0909a6a-7626-448c-a15e-8eb4dd8f6ea6",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train, y_train = load_data(train_dir)\n",
    "X_test, y_test = load_data(test_dir)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b97dc387-efde-4f43-8fc7-c232973c9ef9",
   "metadata": {},
   "outputs": [],
   "source": [
    "vectorizer = CountVectorizer(stop_words='english')\n",
    "X_train_vectorized = vectorizer.fit_transform(X_train)\n",
    "X_test_vectorized = vectorizer.transform(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "d0b32801-c319-4924-97b6-cf6568766fde",
   "metadata": {},
   "outputs": [],
   "source": [
    "model = DecisionTreeClassifier(random_state=42)\n",
    "model.fit(X_train_vectorized, y_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "94e11cfc-fbf9-48bb-82d6-23ddfd311a79",
   "metadata": {},
   "outputs": [],
   "source": [
    "y_pred = model.predict(X_test_vectorized)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "212a9f77-b5d6-41e0-afdc-f72808ccdf76",
   "metadata": {},
   "outputs": [],
   "source": [
    "accuracy = accuracy_score(y_test, y_pred)\n",
    "print(f\"Accuracy: {accuracy:.4f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8a153ad8-4155-40ac-8583-e48b77c56fe5",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Classification Report:\")\n",
    "print(classification_report(y_test, y_pred))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5933b119-b0ab-48f1-a3df-8e2013bfa0e6",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Confusion Matrix:\")\n",
    "print(confusion_matrix(y_test, y_pred))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

''')
    
    def mnist(self):
        return (
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "43115740-236e-416b-8911-0236af3abfb6",
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import struct"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "434795b9-980c-4c7b-9c68-075158d60ec2",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_mnist_images(filename):\n",
    "    with open(filename, 'rb') as f:\n",
    "        magic, num, rows, cols = struct.unpack(\">IIII\", f.read(16))\n",
    "        print(num, rows, cols)\n",
    "        images = np.frombuffer(f.read(), dtype=np.uint8).reshape(num, rows*cols)\n",
    "        return images / 255.0\n",
    "\n",
    "def load_mnist_labels(filename):\n",
    "    with open(filename, 'rb') as f:\n",
    "        magic, num = struct.unpack(\">II\", f.read(8))\n",
    "        labels = np.frombuffer(f.read(), dtype=np.uint8)\n",
    "        return labels"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2b66a525-ec25-45dd-8a76-8dd8957c1b43",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train = load_mnist_images('datasets/MNIST/train-images.idx3-ubyte')\n",
    "y_train = load_mnist_labels('datasets/MNIST/train-labels.idx1-ubyte')\n",
    "X_test = load_mnist_images('datasets/MNIST/t10k-images.idx3-ubyte')\n",
    "y_test = load_mnist_labels('datasets/MNIST/t10k-labels.idx1-ubyte')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "44faeeb8-fddc-44b5-a734-bec678f49b22",
   "metadata": {},
   "outputs": [],
   "source": [
    "np.random.seed(42)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "236cc132-fd4e-4e53-9305-fd924efb1be8",
   "metadata": {},
   "outputs": [],
   "source": [
    "input_size = 784 # 28 x 28 pixels\n",
    "hidden_size1 = 128\n",
    "hidden_size2 = 64\n",
    "output_size = 10 # numbers from 0 to 9"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4e57cafb-0808-4419-8662-99a3ac26a90b",
   "metadata": {},
   "outputs": [],
   "source": [
    "weights = {\n",
    "    \"W1\": np.random.randn(input_size, hidden_size1) * np.sqrt(2.0 / input_size),\n",
    "    \"W2\": np.random.randn(hidden_size1, hidden_size2) * np.sqrt(2.0 / hidden_size1),\n",
    "    \"W3\": np.random.randn(hidden_size2, output_size) * np.sqrt(2.0 / hidden_size2),\n",
    "    \"b1\": np.zeros((1, hidden_size1)),\n",
    "    \"b2\": np.zeros((1, hidden_size2)),\n",
    "    \"b3\": np.zeros((1, output_size))\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "04d47351-443e-4a60-bda1-50261ccf3b88",
   "metadata": {},
   "outputs": [],
   "source": [
    "def relu(Z):\n",
    "    return np.maximum(0, Z)\n",
    "\n",
    "def softmax(Z):\n",
    "    expZ = np.exp(Z - np.max(Z, axis=1, keepdims=True)) # numerical stability (removal of very large nums as exponentiation will result in large nums)\n",
    "    return expZ / np.sum(expZ, axis=1, keepdims=True) # normalization"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "dac94b0d-db6a-4036-b6c0-ad0b8833e60c",
   "metadata": {},
   "outputs": [],
   "source": [
    "def forward_propagation(X, weights):\n",
    "    Z1 = np.dot(X, weights[\"W1\"]) + weights[\"b1\"]\n",
    "    A1 = relu(Z1)\n",
    "\n",
    "    Z2 = np.dot(A1, weights[\"W2\"]) + weights[\"b2\"]\n",
    "    A2 = relu(Z2)\n",
    "\n",
    "    Z3 = np.dot(A2, weights[\"W3\"]) + weights[\"b3\"]\n",
    "    A3 = softmax(Z3)\n",
    "\n",
    "    return Z1, A1, Z2, A2, Z3, A3  "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "995e36b8-2f0d-484a-a7ce-527ae641ce6d",
   "metadata": {},
   "outputs": [],
   "source": [
    "def compute_loss(Y_pred, Y_true, weights, lambda_):\n",
    "    m = Y_true.shape[0]\n",
    "    log_likelihood = -np.log(Y_pred[range(m), Y_true])\n",
    "    loss = np.sum(log_likelihood) / m\n",
    "\n",
    "    L2_regularizer = (lambda_ / (2 * m) * (\n",
    "        np.sum(weights[\"W1\"] ** 2) + np.sum(weights[\"W2\"] ** 2) + np.sum(weights[\"W3\"] ** 2)\n",
    "    ))\n",
    "\n",
    "    return loss + L2_regularizer"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "23d73f8e-cbd8-4fc0-a0d4-9a8e39262174",
   "metadata": {},
   "outputs": [],
   "source": [
    "def backpropagation(X, Y_true, A1, A2, A3, weights, learning_rate, lambda_):\n",
    "    m = X.shape[0]\n",
    "\n",
    "    Y_one_hot = np.zeros((m, output_size))\n",
    "    Y_one_hot[np.arange(m), Y_true] = 1\n",
    "\n",
    "    dZ3 = A3 - Y_one_hot\n",
    "    dW3 = (np.dot(A2.T, dZ3) + lambda_ * weights[\"W3\"]) / m\n",
    "    db3 = np.sum(dZ3, axis=0, keepdims=True) / m\n",
    "\n",
    "    dA2 = np.dot(dZ3, weights[\"W3\"].T)\n",
    "    dZ2 = dA2 * (A2 > 0)  # ReLU derivative\n",
    "    dW2 = (np.dot(A1.T, dZ2) + lambda_ * weights[\"W2\"]) / m\n",
    "    db2 = np.sum(dZ2, axis=0, keepdims=True) / m\n",
    "\n",
    "    dA1 = np.dot(dZ2, weights[\"W2\"].T)\n",
    "    dZ1 = dA1 * (A1 > 0)  # ReLU derivative\n",
    "    dW1 = (np.dot(X.T, dZ1) + lambda_ * weights[\"W1\"]) / m\n",
    "    db1 = np.sum(dZ1, axis=0, keepdims=True) / m\n",
    "\n",
    "    # Update weights\n",
    "    weights[\"W1\"] -= learning_rate * dW1\n",
    "    weights[\"b1\"] -= learning_rate * db1\n",
    "    weights[\"W2\"] -= learning_rate * dW2\n",
    "    weights[\"b2\"] -= learning_rate * db2\n",
    "    weights[\"W3\"] -= learning_rate * dW3\n",
    "    weights[\"b3\"] -= learning_rate * db3"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cc37abd4-400f-4255-ae89-24f72fc552d5",
   "metadata": {},
   "outputs": [],
   "source": [
    "epochs = 50\n",
    "batch_size = 64\n",
    "lambda_ = 0.01 # L2 regularization factor"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2cc5c5a7-d19e-4ba3-b3f0-9695fe8f1262",
   "metadata": {},
   "outputs": [],
   "source": [
    "for epoch in range(epochs):\n",
    "    shuffle_indices = np.random.permutation(X_train.shape[0])\n",
    "    X_train, y_train = X_train[shuffle_indices], y_train[shuffle_indices]\n",
    "\n",
    "    for i in range(0, X_train.shape[0], batch_size):\n",
    "        X_batch = X_train[i:i+batch_size]\n",
    "        y_batch = y_train[i:i+batch_size]\n",
    "\n",
    "        Z1, A1, Z2, A2, Z3, A3 = forward_propagation(X_batch, weights)\n",
    "\n",
    "        learning_rate = 0.01 / (1 + 0.01 * epoch) # Learning rate decay\n",
    "        backpropagation(X_batch, y_batch, A1, A2, A3, weights, learning_rate, lambda_)\n",
    "\n",
    "\n",
    "    _, _, _, _, _, train_pred = forward_propagation(X_train, weights)\n",
    "    train_loss = compute_loss(train_pred, y_train, weights, lambda_)\n",
    "\n",
    "    print(f\"Epoch {epoch+1}/{epochs}, Loss: {train_loss:.4f}\")\n",
    "    "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "255a4b19-fdcb-445f-80ba-d12ef229f212",
   "metadata": {},
   "outputs": [],
   "source": [
    "def predict(X, weights):\n",
    "    _, _, _, _, _, A3 = forward_propagation(X, weights)\n",
    "    return np.argmax(A3, axis=1)\n",
    "\n",
    "y_pred = predict(X_test, weights)\n",
    "accuracy = np.mean(y_pred == y_test) * 100\n",
    "print(f\"Test Accuracy: {accuracy:.2f}%\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''
        )
        
    def lr(self):
        return (
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5fe335d3-c7fb-41e8-b293-5516e5addaa6",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.preprocessing import StandardScaler"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c03ae6fb-130b-4d61-a01c-f6a86bd401ae",
   "metadata": {},
   "outputs": [],
   "source": [
    "columns = ['Sex', 'Length', 'Diameter', 'Height', 'WholeWeight', 'ShuckedWeight', 'VisceraWeight', 'ShellWeight', 'Rings']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b231bec8-fe13-4b88-ada4-760a8f2938d3",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = pd.read_csv(\"./datasets/abalone/abalone.data\", header=None, names=columns)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b8e940fd-6138-453e-bef6-0ab33b82773d",
   "metadata": {},
   "outputs": [],
   "source": [
    "data['Sex'] = data['Sex'].map({'M': 0, 'F': 1, 'I': 2})"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4ebe4cd9-c3d0-459e-90fd-8ed6dec2ba49",
   "metadata": {},
   "outputs": [],
   "source": [
    "data.info()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9ff71783-d6e0-4a38-a0a3-484197cb386c",
   "metadata": {},
   "outputs": [],
   "source": [
    "X = data.drop(columns=['Rings'])\n",
    "y = data['Rings']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3a96e81e-2f6f-466f-a6a5-e89482b90101",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c5a75b4a-0675-4b13-9b06-c8ae89127dbf",
   "metadata": {},
   "outputs": [],
   "source": [
    "scaler = StandardScaler()\n",
    "X_train = scaler.fit_transform(X_train)\n",
    "X_test = scaler.transform(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bcdea284-dc15-4653-8971-e33e8cc4161f",
   "metadata": {},
   "outputs": [],
   "source": [
    "def initialize_weights(dim):\n",
    "    weights = np.zeros(dim)\n",
    "    bias = 0\n",
    "    return weights, bias"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "36479f31-04d1-4281-a52b-d2f05a1bc7b7",
   "metadata": {},
   "outputs": [],
   "source": [
    "def predict(X, weights, bias):\n",
    "    return np.dot(X, weights) + bias\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "aba06496-cc2b-4a94-b270-a41f1060fca4",
   "metadata": {},
   "outputs": [],
   "source": [
    "def compute_loss(y_true, y_pred):\n",
    "    m = len(y_true)\n",
    "    loss = (1/(2*m)) * np.sum((y_pred - y_true) ** 2)\n",
    "    return loss\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "62c8ef5b-e5d9-4d9f-a4e7-6e178628feed",
   "metadata": {},
   "outputs": [],
   "source": [
    "def compute_gradients(X, y_true, y_pred):\n",
    "    m = len(y_true)\n",
    "    dw = (1/m) * np.dot(X.T, (y_pred - y_true))\n",
    "    db = (1/m) * np.sum(y_pred -y_true)\n",
    "    return dw, db"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8440adde-b70c-4287-ad8a-0c5b0e2a9139",
   "metadata": {},
   "outputs": [],
   "source": [
    "def update_parameters(weights, bias, dw, db, learning_rate):\n",
    "    weights -= learning_rate * dw\n",
    "    bias -= learning_rate * db\n",
    "    return weights, bias"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2a70b26a-e6b0-43cb-99d5-47bad7586547",
   "metadata": {},
   "outputs": [],
   "source": [
    "def train_linear_regression(X, y, learning_rate, epochs):\n",
    "    weights, bias = initialize_weights(X.shape[1])\n",
    "\n",
    "    for i in range(epochs):\n",
    "\n",
    "        y_pred = predict(X, weights, bias)\n",
    "\n",
    "        loss = compute_loss(y, y_pred)\n",
    "\n",
    "        dw, db = compute_gradients(X, y, y_pred)\n",
    "\n",
    "        weights, bias = update_parameters(weights, bias, dw, db, learning_rate)\n",
    "        \n",
    "        print(f\"Epoch {i}: Loss = {loss:.4f}\")\n",
    "    return weights, bias"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "372fcdaf-a305-4e55-9a0e-a9dc69bf1fa7",
   "metadata": {},
   "outputs": [],
   "source": [
    "learning_rate = 0.01\n",
    "epochs = 1000\n",
    "weights, bias = train_linear_regression(X_train, y_train, learning_rate, epochs)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ef4576d1-4b30-48e7-b059-aa84bee69881",
   "metadata": {},
   "outputs": [],
   "source": [
    "def evaluate_model(X, y, weights, bias):\n",
    "    y_pred = predict(X, weights, bias)\n",
    "    mse = compute_loss(y, y_pred)\n",
    "    return mse"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4b001c64-205a-4639-a98a-79fd2fb20088",
   "metadata": {},
   "outputs": [],
   "source": [
    "mse_test = evaluate_model(X_test, y_test, weights, bias)\n",
    "print(f\"Test MSE: {mse_test:.4f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5673481d-2439-4262-ad33-874cbf0921ee",
   "metadata": {},
   "outputs": [],
   "source": [
    "def show_regression_equation(weights, bias):\n",
    "    eqn = \"y = \"\n",
    "    for i, weight in enumerate(weights):\n",
    "        eqn += f\"{weight:.4f} * {data.columns[i]} + \"\n",
    "    eqn += f\"{bias:.4f}\"\n",
    "    print(f\"Regression Equation: {eqn}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6f169b3d-2e2d-46f3-b3c6-adf648332e2a",
   "metadata": {},
   "outputs": [],
   "source": [
    "show_regression_equation(weights, bias)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8e123d24-f76b-4c1a-8faf-394d2918c79e",
   "metadata": {},
   "outputs": [],
   "source": [
    "def plot_regression(X_test, y_test, weights, bias):\n",
    "    y_pred = predict(X_test, weights, bias)\n",
    "    \n",
    "    plt.figure(figsize=(10, 6))\n",
    "    plt.scatter(y_test, y_pred, color='blue', alpha=0.5, label='Predicted vs Actual')\n",
    "    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', label='Ideal Line')\n",
    "    plt.xlabel('Actual Values')\n",
    "    plt.ylabel('Predicted Values')\n",
    "    plt.title('Regression: Predicted vs Actual Values')\n",
    "    plt.legend()\n",
    "    plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7b8013d7-a7e1-4579-a2e6-88ae545bb2e6",
   "metadata": {},
   "outputs": [],
   "source": [
    "plot_regression(X_test, y_test, weights, bias)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''
        )
        
    def nb(self):
        return (
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "33dd4e12-428f-4e82-9758-eed91b411ee2",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.feature_extraction.text import CountVectorizer\n",
    "from sklearn.naive_bayes import MultinomialNB\n",
    "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "adfdad45-f5f5-49b0-acdc-9a1ce91def06",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = pd.read_csv('datasets/spam.csv', encoding='latin-1')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0e2157bc-2b94-497a-b94b-2af470ed5dd7",
   "metadata": {},
   "outputs": [],
   "source": [
    "data = data[['v1', 'v2']]\n",
    "data.columns = ['label', 'message']\n",
    "data.dropna(axis=0, inplace=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e7ea834f-41e1-4bf4-8c91-2f1edde55c20",
   "metadata": {},
   "outputs": [],
   "source": [
    "X = data['message']\n",
    "y = data['label']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "89590267-9791-4bcd-a99b-06dc9b180395",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "af3b86ff-853c-41ba-a014-a15d1c2390d4",
   "metadata": {},
   "outputs": [],
   "source": [
    "vectorizer = CountVectorizer(stop_words='english')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4d6c02c4-2656-4587-92dd-dc582bb5ab8c",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train_vectorized = vectorizer.fit_transform(X_train)\n",
    "X_test_vectorized = vectorizer.transform(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f10e0494-41f6-4599-b7bc-3a738a5ebdc2",
   "metadata": {},
   "outputs": [],
   "source": [
    "model = MultinomialNB()\n",
    "model.fit(X_train_vectorized, y_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "50a7b858-7a82-448c-9efa-9a9d9e4b9c3a",
   "metadata": {},
   "outputs": [],
   "source": [
    "y_pred = model.predict(X_test_vectorized)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "66cb4112-d7e3-493b-a98c-86bfedf903bd",
   "metadata": {},
   "outputs": [],
   "source": [
    "accuracy = accuracy_score(y_test, y_pred)\n",
    "print(f\"Accuracy: {accuracy:.4f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1d9bc365-c392-4be7-8225-b266b9de0938",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Classification Report:\")\n",
    "print(classification_report(y_test, y_pred))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cfaa2fa2-10ca-4b69-9b8a-87916f7352ed",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Confusion Matrix:\")\n",
    "print(confusion_matrix(y_test, y_pred))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''
        )
    
    def rf(self):
        return (
r'''
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "17c029ef-7657-4ff5-a6ad-f0037ab22922",
   "metadata": {},
   "outputs": [],
   "source": [
    "from sklearn.feature_extraction.text import CountVectorizer\n",
    "from sklearn.ensemble import RandomForestClassifier\n",
    "from sklearn.metrics import accuracy_score, classification_report, confusion_matrix\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "71cd02d0-9f58-450a-942a-7f67a0027b47",
   "metadata": {},
   "outputs": [],
   "source": [
    "def load_data(data_dir):\n",
    "    texts, labels = [], []\n",
    "\n",
    "    for label in ['pos', 'neg']:\n",
    "        label_dir = os.path.join(data_dir, label)\n",
    "        for filename in os.listdir(label_dir):\n",
    "            with open(os.path.join(label_dir, filename), encoding='utf-8') as f:\n",
    "                texts.append(f.read())\n",
    "            labels.append(1 if label == 'pos' else 0)\n",
    "\n",
    "    return texts, labels"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "87044f83-e129-4d16-a350-fb3dba3de509",
   "metadata": {},
   "outputs": [],
   "source": [
    "train_dir = \"datasets/aclImdb/train/\"\n",
    "test_dir = \"datasets/aclImdb/test/\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "118bdbdb",
   "metadata": {},
   "outputs": [],
   "source": [
    "X_train, y_train = load_data(train_dir)\n",
    "X_test, y_test = load_data(test_dir)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0d2f562b-18c9-47be-9ed9-60856f525c99",
   "metadata": {},
   "outputs": [],
   "source": [
    "vectorizer = CountVectorizer(stop_words='english')\n",
    "X_train_vectorized = vectorizer.fit_transform(X_train)\n",
    "X_test_vectorized = vectorizer.transform(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8231ddf3-d674-4b53-ae02-616ad4c9cf31",
   "metadata": {},
   "outputs": [],
   "source": [
    "model = RandomForestClassifier(n_estimators=100, random_state=42)\n",
    "model.fit(X_train_vectorized, y_train)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fe0b9baa-3a69-4117-aa6e-8dfd24fdbf11",
   "metadata": {},
   "outputs": [],
   "source": [
    "y_pred = model.predict(X_test_vectorized)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4f41a308-fdab-44c1-9264-192a9560fbd1",
   "metadata": {},
   "outputs": [],
   "source": [
    "accuracy = accuracy_score(y_test, y_pred)\n",
    "print(f\"Accuracy: {accuracy:.4f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2dba31ae-5b72-440e-8d9a-34c82c404892",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Classification Report:\")\n",
    "print(classification_report(y_test, y_pred))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9a72267d-0450-4475-95a8-e17a0ba44a60",
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Confusion Matrix:\")\n",
    "print(confusion_matrix(y_test, y_pred))"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
'''
        )